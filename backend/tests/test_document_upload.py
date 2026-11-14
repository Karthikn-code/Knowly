
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks, HTTPException

from app.api.v1.endpoints import documents


@pytest.mark.asyncio
async def test_refresh_failure_before_commit_rolls_back_and_cleans_up_file(
    monkeypatch,
):
    content = b"Knowly document upload test content."
    user = SimpleNamespace(id=uuid4())

    upload = SimpleNamespace(
        filename="knowly.txt",
        content_type="text/plain",
        read=AsyncMock(side_effect=[content, b""]),
        close=AsyncMock(),
    )

    db = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock(
        side_effect=RuntimeError("Simulated refresh failure")
    )
    db.rollback = AsyncMock()

    storage = documents.document_storage
    save_mock = AsyncMock(
        return_value=("private/knowly-test-key", len(content))
    )
    delete_mock = AsyncMock()

    monkeypatch.setattr(storage, "save", save_mock)
    monkeypatch.setattr(storage, "delete", delete_mock)

    monkeypatch.setattr(
        documents,
        "validate_and_extract",
        lambda filename, file_bytes: (
            "txt",
            "text/plain",
            "Knowly document upload test content.",
        ),
    )

    monkeypatch.setattr(
        documents,
        "save_document_chunks",
        AsyncMock(return_value=1),
    )

    monkeypatch.setattr(
        documents,
        "record_audit_event",
        AsyncMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await documents.upload_document(
            request=MagicMock(),
            background_tasks=BackgroundTasks(),
            file=upload,
            current_user=user,
            _=None,
            db=db,
        )

    assert exc_info.value.status_code == 500

    # The database transaction was already committed.
    db.commit.assert_awaited_once()

    # A refresh failure must not delete the committed document's file.
    db.rollback.assert_awaited_once()
    delete_mock.assert_awaited_once_with("private/knowly-test-key")
