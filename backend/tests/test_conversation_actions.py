
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.dialects import postgresql

from app.api.v1.endpoints.conversations import (
    delete_conversation,
    list_conversations,
    update_conversation,
)
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationUpdate


def compile_statement(statement):
    return statement.compile(dialect=postgresql.dialect())


@pytest.mark.asyncio
async def test_list_conversations_filters_by_user_and_orders_pinned_first():
    user_id = uuid4()

    conversations = [
        SimpleNamespace(id=uuid4(), is_pinned=True),
        SimpleNamespace(id=uuid4(), is_pinned=False),
    ]

    result = SimpleNamespace(
        scalars=lambda: SimpleNamespace(
            all=lambda: conversations
        )
    )

    db = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )

    response = await list_conversations(
        current_user=SimpleNamespace(id=user_id),
        db=db,
        limit=20,
        offset=0,
    )

    assert response == conversations

    statement = db.execute.await_args.args[0]
    compiled = compile_statement(statement)
    sql = str(compiled)

    assert "conversations.user_id" in sql
    assert "conversations.is_pinned DESC" in sql
    assert "conversations.updated_at DESC" in sql
    assert user_id in compiled.params.values()


@pytest.mark.asyncio
@pytest.mark.parametrize("pin_status", [True, False])
async def test_update_conversation_persists_pin_status(pin_status):
    user_id = uuid4()
    conversation_id = uuid4()

    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Test conversation",
        is_pinned=not pin_status,
    )

    result = SimpleNamespace(
        scalar_one_or_none=lambda: conversation
    )

    db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )

    response = await update_conversation(
        conversation_id=conversation_id,
        payload=ConversationUpdate(is_pinned=pin_status),
        current_user=SimpleNamespace(id=user_id),
        _=None,
        db=db,
    )

    assert response.is_pinned is pin_status
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(conversation)

    statement = db.execute.await_args.args[0]
    compiled = compile_statement(statement)
    sql = str(compiled)

    assert "conversations.id" in sql
    assert "conversations.user_id" in sql
    assert conversation_id in compiled.params.values()
    assert user_id in compiled.params.values()


@pytest.mark.asyncio
async def test_update_conversation_rejects_another_users_conversation():
    user_id = uuid4()
    conversation_id = uuid4()

    result = SimpleNamespace(
        scalar_one_or_none=lambda: None
    )

    db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_conversation(
            conversation_id=conversation_id,
            payload=ConversationUpdate(is_pinned=True),
            current_user=SimpleNamespace(id=user_id),
            _=None,
            db=db,
        )

    assert exc_info.value.status_code == 404
    db.commit.assert_not_awaited()

    statement = db.execute.await_args.args[0]
    compiled = compile_statement(statement)
    sql = str(compiled)

    assert "conversations.user_id" in sql
    assert user_id in compiled.params.values()


@pytest.mark.asyncio
async def test_delete_conversation_deletes_owned_conversation():
    user_id = uuid4()
    conversation_id = uuid4()

    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Conversation to delete",
        is_pinned=False,
    )

    result = SimpleNamespace(
        scalar_one_or_none=lambda: conversation
    )

    db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
        delete=AsyncMock(),
        commit=AsyncMock(),
    )

    response = await delete_conversation(
        conversation_id=conversation_id,
        current_user=SimpleNamespace(id=user_id),
        _=None,
        db=db,
    )

    assert response.status_code == 204
    db.delete.assert_awaited_once_with(conversation)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_conversation_rejects_another_users_conversation():
    user_id = uuid4()
    conversation_id = uuid4()

    result = SimpleNamespace(
        scalar_one_or_none=lambda: None
    )

    db = SimpleNamespace(
        execute=AsyncMock(return_value=result),
        delete=AsyncMock(),
        commit=AsyncMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await delete_conversation(
            conversation_id=conversation_id,
            current_user=SimpleNamespace(id=user_id),
            _=None,
            db=db,
        )

    assert exc_info.value.status_code == 404
    db.delete.assert_not_awaited()
    db.commit.assert_not_awaited()

    statement = db.execute.await_args.args[0]
    compiled = compile_statement(statement)
    sql = str(compiled)

    assert "conversations.user_id" in sql
    assert user_id in compiled.params.values()

