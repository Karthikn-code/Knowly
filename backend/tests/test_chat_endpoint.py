from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request

from app.api.v1.endpoints.chat import chat_with_documents
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.embedding_service import GeminiEmbeddingError
from app.services.gemini_service import GeminiGenerationError


def make_request():
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/conversations/test/chat",
        "raw_path": b"/conversations/test/chat",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 8000),
    }
    return Request(scope)


def make_database(conversation=None, history=None):
    db = MagicMock()

    conversation_result = MagicMock()
    conversation_result.scalar_one_or_none.return_value = conversation

    history_result = MagicMock()
    history_result.scalars.return_value.all.return_value = history or []

    db.execute = AsyncMock(
        side_effect=[
            conversation_result,
            history_result,
        ]
    )
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()

    return db


@pytest.mark.asyncio
async def test_successful_chat_persists_messages_and_audit():
    user_id = uuid4()
    conversation_id = uuid4()

    conversation = SimpleNamespace(
        id=conversation_id,
        updated_at=None,
    )

    previous_message = SimpleNamespace(
        role="user",
        content="What is Knowly?",
    )

    db = make_database(
        conversation=conversation,
        history=[previous_message],
    )

    rag_result = {
        "answer": "Knowly is an AI document assistant [S1].",
        "citations": [
            {"source_id": "S1", "filename": "test.txt"}
        ],
        "retrieved_chunks": [{"content": "Knowly document"}],
    }

    with (
        patch(
            "app.api.v1.endpoints.chat.answer_question",
            new=AsyncMock(return_value=rag_result),
        ) as mock_answer,
        patch(
            "app.api.v1.endpoints.chat.record_audit_event",
            new=AsyncMock(),
        ) as mock_audit,
    ):
        response = await chat_with_documents(
            conversation_id=conversation_id,
            payload=MessageCreate(content="What is Knowly?"),
            request=make_request(),
            current_user=SimpleNamespace(id=user_id),
            _=None,
            db=db,
        )

    assert len(response) == 2
    assert response[0].role == "user"
    assert response[1].role == "assistant"

    assert response[0].content == "What is Knowly?"
    assert response[1].content == rag_result["answer"]
    assert response[1].citations == rag_result["citations"]

    assert response[1].created_at > response[0].created_at

    mock_answer.assert_awaited_once()
    assert mock_answer.await_args.kwargs["user_id"] == user_id

    mock_audit.assert_awaited_once()
    assert mock_audit.await_args.kwargs["event_type"] == "chat.answer.generated"

    db.add_all.assert_called_once()
    persisted_messages = db.add_all.call_args.args[0]

    assert len(persisted_messages) == 2
    assert all(isinstance(message, Message) for message in persisted_messages)

    db.commit.assert_awaited_once()
    assert db.rollback.await_count == 0


@pytest.mark.asyncio
async def test_chat_rejects_conversation_owned_by_another_user():
    db = make_database(conversation=None)

    with (
        patch(
            "app.api.v1.endpoints.chat.answer_question",
            new=AsyncMock(),
        ) as mock_answer,
        patch(
            "app.api.v1.endpoints.chat.record_audit_event",
            new=AsyncMock(),
        ) as mock_audit,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await chat_with_documents(
                conversation_id=uuid4(),
                payload=MessageCreate(content="Test question"),
                request=make_request(),
                current_user=SimpleNamespace(id=uuid4()),
                _=None,
                db=db,
            )

    assert exc_info.value.status_code == 404
    mock_answer.assert_not_awaited()
    mock_audit.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_gemini_generation_failure_rolls_back_chat():
    conversation = SimpleNamespace(
        id=uuid4(),
        updated_at=None,
    )

    db = make_database(conversation=conversation)

    with (
        patch(
            "app.api.v1.endpoints.chat.answer_question",
            new=AsyncMock(
                side_effect=GeminiGenerationError("Gemini unavailable")
            ),
        ),
        patch(
            "app.api.v1.endpoints.chat.record_audit_event",
            new=AsyncMock(),
        ) as mock_audit,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await chat_with_documents(
                conversation_id=conversation.id,
                payload=MessageCreate(content="Test question"),
                request=make_request(),
                current_user=SimpleNamespace(id=uuid4()),
                _=None,
                db=db,
            )

    assert exc_info.value.status_code == 503
    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()
    db.add_all.assert_not_called()
    mock_audit.assert_not_awaited()


@pytest.mark.asyncio
async def test_embedding_failure_rolls_back_chat():
    conversation = SimpleNamespace(
        id=uuid4(),
        updated_at=None,
    )

    db = make_database(conversation=conversation)

    with (
        patch(
            "app.api.v1.endpoints.chat.answer_question",
            new=AsyncMock(
                side_effect=GeminiEmbeddingError("Embedding unavailable")
            ),
        ),
        patch(
            "app.api.v1.endpoints.chat.record_audit_event",
            new=AsyncMock(),
        ) as mock_audit,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await chat_with_documents(
                conversation_id=conversation.id,
                payload=MessageCreate(content="Test question"),
                request=make_request(),
                current_user=SimpleNamespace(id=uuid4()),
                _=None,
                db=db,
            )

    assert exc_info.value.status_code == 503
    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()
    db.add_all.assert_not_called()
    mock_audit.assert_not_awaited()


@pytest.mark.asyncio
async def test_chat_passes_history_to_rag_in_chronological_order():
    user_id = uuid4()
    conversation_id = uuid4()

    conversation = SimpleNamespace(
        id=conversation_id,
        updated_at=None,
    )

    older_message = SimpleNamespace(
        role="user",
        content="What is Medi-Van?",
    )

    newer_message = SimpleNamespace(
        role="assistant",
        content="Medi-Van is a hospital transport system.",
    )

    # The database query returns messages newest first.
    db = make_database(
        conversation=conversation,
        history=[newer_message, older_message],
    )

    rag_result = {
        "answer": "It uses Raspberry Pi.",
        "citations": [],
        "retrieved_chunks": [],
    }

    with (
        patch(
            "app.api.v1.endpoints.chat.answer_question",
            new=AsyncMock(return_value=rag_result),
        ) as mock_answer,
        patch(
            "app.api.v1.endpoints.chat.record_audit_event",
            new=AsyncMock(),
        ),
    ):
        await chat_with_documents(
            conversation_id=conversation_id,
            payload=MessageCreate(
                content="What technologies does it use?"
            ),
            request=make_request(),
            current_user=SimpleNamespace(id=user_id),
            _=None,
            db=db,
        )

    mock_answer.assert_awaited_once()

    assert mock_answer.await_args.kwargs["history"] == [
        {
            "role": "user",
            "content": "What is Medi-Van?",
        },
        {
            "role": "assistant",
            "content": "Medi-Van is a hospital transport system.",
        },
    ]