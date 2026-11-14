
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
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


router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"],
)


async def get_owned_conversation(
    conversation_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> Conversation:
    """Return a conversation only if it belongs to the given user."""

    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )

    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return conversation


@router.post(
    "",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: UUID,
    payload: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save a user message in a conversation owned by the user."""

    conversation = await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )

    message = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.content,
    )

    db.add(message)

    # Update conversation activity for correct recent-first sorting.
    conversation.updated_at = func.now()

    await db.commit()
    await db.refresh(message)

    return message


@router.get(
    "",
    response_model=list[MessageRead],
)
async def list_messages(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Retrieve messages from a conversation owned by the user."""

    conversation = await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(
            Message.created_at.asc(),
            case(
                (Message.role == "user", 0),
                else_=1,
            ).asc(),
            Message.id.asc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return result.scalars().all()
