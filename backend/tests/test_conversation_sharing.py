
import hashlib
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException, Response
from sqlalchemy.dialects import postgresql

from app.api.v1.endpoints import conversations as conversation_endpoints
from app.api.v1.endpoints.conversations import (
    create_conversation_share,
    get_shared_conversation,
    revoke_conversation_share,
)
from app.models.conversation import Conversation
from app.models.conversation_share import ConversationShare


def compile_statement(statement):
    return statement.compile(dialect=postgresql.dialect())


def make_result(value=None):
    return SimpleNamespace(
        scalar_one_or_none=lambda: value
    )


@pytest.mark.asyncio
async def test_create_conversation_share_stores_only_token_hash(
    monkeypatch,
):
    user_id = uuid4()
    conversation_id = uuid4()
    share_id = uuid4()
    created_at = datetime.now(timezone.utc)

    raw_token = "test_secure_share_token_12345678901234567890"

    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Private conversation",
        is_pinned=False,
    )

    db = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                make_result(conversation),
                None,
            ]
        ),
        add=Mock(),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )

    monkeypatch.setattr(
        conversation_endpoints.secrets,
        "token_urlsafe",
        lambda length: raw_token,
    )

    monkeypatch.setattr(
        conversation_endpoints.settings,
        "FRONTEND_URL",
        "http://localhost:3000",
    )

    async def refresh_share(share):
        share.id = share_id
        share.created_at = created_at

    db.refresh.side_effect = refresh_share

    response = await create_conversation_share(
        conversation_id=conversation_id,
        current_user=SimpleNamespace(id=user_id),
        _=None,
        db=db,
    )

    assert response.id == share_id
    assert response.created_at == created_at
    assert response.share_url == (
        f"http://localhost:3000/share/{raw_token}"
    )

    share = db.add.call_args.args[0]

    assert isinstance(share, ConversationShare)
    assert share.conversation_id == conversation_id
    assert share.token_hash == hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()
    assert share.token_hash != raw_token

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(share)

    # Verify that existing active shares are revoked first.
    revoke_statement = db.execute.await_args_list[1].args[0]
    compiled = compile_statement(revoke_statement)
    sql = str(compiled)

    assert "conversation_shares" in sql
    assert "conversation_shares.revoked_at IS NULL" in sql
    assert conversation_id in compiled.params.values()


@pytest.mark.asyncio
async def test_create_conversation_share_rejects_non_owner(
    monkeypatch,
):
    user_id = uuid4()
    conversation_id = uuid4()

    db = SimpleNamespace(
        execute=AsyncMock(
            return_value=make_result(None)
        ),
        add=Mock(),
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_conversation_share(
            conversation_id=conversation_id,
            current_user=SimpleNamespace(id=user_id),
            _=None,
            db=db,
        )

    assert exc_info.value.status_code == 404
    db.add.assert_not_called()
    db.commit.assert_not_awaited()

    statement = db.execute.await_args.args[0]
    compiled = compile_statement(statement)

    assert "conversations.user_id" in str(compiled)
    assert user_id in compiled.params.values()


@pytest.mark.asyncio
async def test_get_shared_conversation_returns_minimal_public_data():
    raw_token = "test_secure_share_token_12345678901234567890"

    conversation = SimpleNamespace(
        id=uuid4(),
        title="Shared conversation",
    )

    share = SimpleNamespace(
        id=uuid4(),
    )

    created_at = datetime.now(timezone.utc)

    message = SimpleNamespace(
        id=uuid4(),
        role="assistant",
        content="This is a shared answer.",
        citations=[{"private": "citation metadata"}],
        created_at=created_at,
    )

    first_result = SimpleNamespace(
        one_or_none=lambda: (conversation, share)
    )

    second_result = SimpleNamespace(
        scalars=lambda: SimpleNamespace(
            all=lambda: [message]
        )
    )

    db = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[first_result, second_result]
        )
    )

    response_headers = Response()

    result = await get_shared_conversation(
        token=raw_token,
        db=db,
        response=response_headers,
    )

    assert result["title"] == "Shared conversation"
    assert len(result["messages"]) == 1

    shared_message = result["messages"][0]

    assert shared_message == {
        "role": "assistant",
        "content": "This is a shared answer.",
        "created_at": created_at,
    }

    # Private message metadata must not be returned.
    assert "id" not in shared_message
    assert "citations" not in shared_message

    # Verify that the lookup uses the SHA-256 hash.
    lookup_statement = db.execute.await_args_list[0].args[0]
    compiled = compile_statement(lookup_statement)

    expected_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    assert expected_hash in compiled.params.values()
    assert "conversation_shares.revoked_at IS NULL" in str(compiled)

    assert response_headers.headers["Cache-Control"] == "no-store"
    assert response_headers.headers["X-Robots-Tag"] == (
        "noindex, nofollow"
    )
    assert response_headers.headers["Referrer-Policy"] == (
        "no-referrer"
    )


@pytest.mark.asyncio
async def test_get_shared_conversation_rejects_invalid_or_revoked_token():
    raw_token = "test_secure_share_token_12345678901234567890"

    result = SimpleNamespace(
        one_or_none=lambda: None
    )

    db = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )

    response_headers = Response()

    with pytest.raises(HTTPException) as exc_info:
        await get_shared_conversation(
            token=raw_token,
            db=db,
            response=response_headers,
        )

    assert exc_info.value.status_code == 404
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_conversation_share_revokes_active_links():
    user_id = uuid4()
    conversation_id = uuid4()

    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Conversation to revoke",
        is_pinned=False,
    )

    db = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                make_result(conversation),
                None,
            ]
        ),
        commit=AsyncMock(),
    )

    response = await revoke_conversation_share(
        conversation_id=conversation_id,
        current_user=SimpleNamespace(id=user_id),
        _=None,
        db=db,
    )

    assert response.status_code == 204
    db.commit.assert_awaited_once()

    revoke_statement = db.execute.await_args_list[1].args[0]
    compiled = compile_statement(revoke_statement)
    sql = str(compiled)

    assert "conversation_shares" in sql
    assert "conversation_shares.revoked_at IS NULL" in sql
    assert conversation_id in compiled.params.values()


@pytest.mark.asyncio
async def test_revoke_conversation_share_rejects_non_owner():
    user_id = uuid4()
    conversation_id = uuid4()

    db = SimpleNamespace(
        execute=AsyncMock(
            return_value=make_result(None)
        ),
        commit=AsyncMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await revoke_conversation_share(
            conversation_id=conversation_id,
            current_user=SimpleNamespace(id=user_id),
            _=None,
            db=db,
        )

    assert exc_info.value.status_code == 404
    db.commit.assert_not_awaited()

    statement = db.execute.await_args.args[0]
    compiled = compile_statement(statement)

    assert "conversations.user_id" in str(compiled)
    assert user_id in compiled.params.values()
