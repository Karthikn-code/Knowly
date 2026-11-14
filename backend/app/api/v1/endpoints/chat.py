
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import CSRFProtection
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageRead
from app.services.audit import record_audit_event
from app.services.embedding_service import GeminiEmbeddingError
from app.services.gemini_service import GeminiGenerationError
from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/conversations/{conversation_id}/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=list[MessageRead],
    status_code=status.HTTP_201_CREATED,
)
async def chat_with_documents(
    conversation_id: UUID,
    payload: MessageCreate,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Generate a document-grounded answer in an owned conversation.

    User message, assistant response, and audit event are
    persisted together in a single database transaction.
    """

    # 1. Verify conversation ownership.
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    # 2. Retrieve recent conversation history.
    # When timestamps are equal, assistant messages come first
    # in descending order so reversing the result restores
    # user-first chronological order.
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(
            Message.created_at.desc(),
            case(
                (Message.role == "assistant", 0),
                else_=1,
            ).asc(),
            Message.id.desc(),
        )
        .limit(8)
    )

    previous_messages = list(
        reversed(history_result.scalars().all())
    )

    history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in previous_messages
    ]

    # 3. Retrieve document context and generate the answer.
    try:
        rag_result = await answer_question(
            db=db,
            user_id=current_user.id,
            question=payload.content,
            history=history,
        )

    except (GeminiEmbeddingError, GeminiGenerationError) as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI service is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    # 4. Assign deterministic timestamps to the message pair.
    user_message_time = datetime.now(timezone.utc)

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.content,
        created_at=user_message_time,
    )

    # Ensure the assistant response always follows the user message.
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=rag_result["answer"],
        citations=rag_result["citations"],
        created_at=user_message_time + timedelta(microseconds=1),
    )

    # 5. Add both messages to the transaction.
    db.add_all(
        [
            user_message,
            assistant_message,
        ]
    )

    # 6. Update conversation activity.
    conversation.updated_at = func.now()

    # 7. Record the successful chat operation.
    await record_audit_event(
        db,
        event_type="chat.answer.generated",
        outcome="success",
        request=request,
        user_id=current_user.id,
        resource_type="conversation",
        resource_id=str(conversation.id),
        metadata={
            "retrieved_chunk_count": len(
                rag_result["retrieved_chunks"]
            ),
            "citation_count": len(
                rag_result["citations"]
            ),
        },
    )

    # 8. Persist messages and audit event atomically.
    await db.commit()

    # 9. Refresh persisted messages.
    await db.refresh(user_message)
    await db.refresh(assistant_message)

    # 10. Return both messages in the correct order.
    return [
        user_message,
        assistant_message,
    ]
