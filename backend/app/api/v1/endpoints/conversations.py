
import hashlib
import secrets
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import CSRFProtection
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.conversation_share import ConversationShare
from app.models.message import Message
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationShareCreated,
    ConversationUpdate,
    SharedConversationRead,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


async def get_owned_conversation(
    conversation_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> Conversation:
    """Return a conversation only if it belongs to the authenticated user."""

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
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a conversation belonging to the authenticated user."""

    conversation = Conversation(
        user_id=current_user.id,
        title=payload.title,
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.get(
    "",
    response_model=list[ConversationRead],
)
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """List the authenticated user's conversations, pinned first."""

    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(
            Conversation.is_pinned.desc(),
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return result.scalars().all()


@router.get(
    "/shares/{token}",
    response_model=SharedConversationRead,
)
async def get_shared_conversation(
    token: Annotated[
        str,
        Path(min_length=40, max_length=128),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
):
    """Return a read-only public conversation using a valid share token."""

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    result = await db.execute(
        select(Conversation, ConversationShare)
        .join(
            ConversationShare,
            ConversationShare.conversation_id == Conversation.id,
        )
        .where(
            ConversationShare.token_hash == token_hash,
            ConversationShare.revoked_at.is_(None),
        )
    )

    row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This share link is invalid or has been revoked.",
        )

    conversation, _share = row

    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    )

    messages = messages_result.scalars().all()

    shared_messages = [
        {
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]

    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Referrer-Policy"] = "no-referrer"

    return {
        "title": conversation.title,
        "messages": shared_messages,
    }


@router.get(
    "/{conversation_id}",
    response_model=ConversationRead,
)
async def get_conversation(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve one conversation owned by the authenticated user."""

    return await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationRead,
)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update the title or pin status of an owned conversation."""

    conversation = await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(conversation, field, value)

    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an owned conversation and its associated messages."""

    conversation = await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )

    await db.delete(conversation)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{conversation_id}/share",
    response_model=ConversationShareCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation_share(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new share link for an owned conversation."""

    conversation = await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )

    # Generate an unpredictable, cryptographically secure token.
    token = secrets.token_urlsafe(32)

    # Store only the SHA-256 hash of the token.
    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    # Revoke previously active links for this conversation.
    await db.execute(
        update(ConversationShare)
        .where(
            ConversationShare.conversation_id == conversation.id,
            ConversationShare.revoked_at.is_(None),
        )
        .values(revoked_at=func.now())
    )

    share = ConversationShare(
        conversation_id=conversation.id,
        token_hash=token_hash,
    )

    db.add(share)

    await db.commit()
    await db.refresh(share)

    share_url = (
        f"{settings.FRONTEND_URL.rstrip('/')}/share/{token}"
    )

    return ConversationShareCreated(
        id=share.id,
        share_url=share_url,
        created_at=share.created_at,
    )


@router.delete(
    "/{conversation_id}/share",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_conversation_share(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Revoke all active share links for an owned conversation."""

    conversation = await get_owned_conversation(
        conversation_id,
        current_user.id,
        db,
    )

    await db.execute(
        update(ConversationShare)
        .where(
            ConversationShare.conversation_id == conversation.id,
            ConversationShare.revoked_at.is_(None),
        )
        .values(revoked_at=func.now())
    )

    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
