
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.document import Document
from app.services.document_processing import save_document_chunks


def make_document(extracted_text="Knowly document content."):
    return Document(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="test.txt",
        storage_key="test-storage-key",
        file_type="txt",
        mime_type="text/plain",
        file_size=len(extracted_text),
        status="processing",
        extracted_text=extracted_text,
    )


@pytest.mark.asyncio
async def test_save_document_chunks_creates_chunk_records():
    document = make_document(
        "First paragraph contains useful information.\n\n"
        "Second paragraph contains more information.\n\n"
        "Third paragraph completes the document."
    )

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    saved_count = await save_document_chunks(
        db,
        document,
        chunk_size=60,
        overlap=10,
    )

    assert saved_count > 1

    db.execute.assert_awaited_once()
    db.add_all.assert_called_once()
    db.flush.assert_awaited_once()

    records = db.add_all.call_args.args[0]

    assert len(records) == saved_count

    assert [
        record.chunk_index for record in records
    ] == list(range(saved_count))

    for record in records:
        assert record.document_id == document.id
        assert record.content
        assert isinstance(record.source_metadata, dict)
        assert record.embedding is None


@pytest.mark.asyncio
async def test_save_document_chunks_preserves_source_offsets():
    text = " ".join(f"word{i}" for i in range(100))
    document = make_document(text)

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    await save_document_chunks(
        db,
        document,
        chunk_size=80,
        overlap=15,
    )

    records = db.add_all.call_args.args[0]

    for record in records:
        start = record.source_metadata["start_char"]
        end = record.source_metadata["end_char"]

        assert 0 <= start < end <= len(text)
        assert record.content == text[start:end]


@pytest.mark.asyncio
async def test_save_document_chunks_deletes_existing_chunks_first():
    document = make_document()

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    await save_document_chunks(db, document)

    statement = db.execute.await_args.args[0]

    assert "DELETE FROM document_chunks" in str(statement)
    assert "document_chunks.document_id" in str(statement)

    assert db.execute.await_count == 1
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_document_chunks_handles_empty_document():
    document = make_document("   \n\n   ")

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    saved_count = await save_document_chunks(db, document)

    assert saved_count == 0

    db.execute.assert_awaited_once()
    db.add_all.assert_not_called()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_document_chunks_rejects_unpersisted_document():
    document = make_document()
    document.id = None

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    with pytest.raises(
        ValueError,
        match="Document must be persisted",
    ):
        await save_document_chunks(db, document)

    db.execute.assert_not_awaited()
    db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_save_document_chunks_does_not_commit_or_rollback():
    document = make_document()

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    await save_document_chunks(db, document)

    db.flush.assert_awaited_once()
    db.commit.assert_not_awaited()
    db.rollback.assert_not_awaited()
