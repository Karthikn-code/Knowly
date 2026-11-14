
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services import embedding_processing


def make_chunk(index, content, embedding=None):
    return SimpleNamespace(
        id=uuid4(),
        document_id=uuid4(),
        chunk_index=index,
        content=content,
        embedding=embedding,
    )


def make_document():
    return SimpleNamespace(id=uuid4())


def make_result(chunks):
    return SimpleNamespace(
        scalars=lambda: SimpleNamespace(
            all=lambda: chunks
        )
    )


@pytest.mark.asyncio
async def test_generate_document_embeddings_successfully():
    document = make_document()

    chunks = [
        make_chunk(0, "First chunk"),
        make_chunk(1, "Second chunk"),
        make_chunk(2, "Third chunk"),
    ]

    db = MagicMock()
    db.execute = AsyncMock(return_value=make_result(chunks))
    db.flush = AsyncMock()

    embeddings = [
        [0.1] * 768,
        [0.2] * 768,
        [0.3] * 768,
    ]

    generate_embedding = AsyncMock(side_effect=embeddings)

    original = embedding_processing.generate_document_embedding

    embedding_processing.generate_document_embedding = (
        generate_embedding
    )

    try:
        processed_count = (
            await embedding_processing.generate_document_embeddings(
                db,
                document,
            )
        )
    finally:
        embedding_processing.generate_document_embedding = original

    assert processed_count == 3

    assert generate_embedding.await_count == 3

    assert [
        call.args[0]
        for call in generate_embedding.await_args_list
    ] == [
        "First chunk",
        "Second chunk",
        "Third chunk",
    ]

    assert chunks[0].embedding == embeddings[0]
    assert chunks[1].embedding == embeddings[1]
    assert chunks[2].embedding == embeddings[2]

    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_document_embeddings_handles_no_pending_chunks():
    document = make_document()

    db = MagicMock()
    db.execute = AsyncMock(return_value=make_result([]))
    db.flush = AsyncMock()

    generate_embedding = AsyncMock()

    original = embedding_processing.generate_document_embedding
    embedding_processing.generate_document_embedding = generate_embedding

    try:
        processed_count = (
            await embedding_processing.generate_document_embeddings(
                db,
                document,
            )
        )
    finally:
        embedding_processing.generate_document_embedding = original

    assert processed_count == 0
    generate_embedding.assert_not_awaited()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_document_embeddings_processes_only_pending_chunks():
    document = make_document()

    pending_chunks = [
        make_chunk(1, "Pending chunk"),
    ]

    db = MagicMock()
    db.execute = AsyncMock(
        return_value=make_result(pending_chunks)
    )
    db.flush = AsyncMock()

    generate_embedding = AsyncMock(
        return_value=[0.5] * 768
    )

    original = embedding_processing.generate_document_embedding
    embedding_processing.generate_document_embedding = generate_embedding

    try:
        processed_count = (
            await embedding_processing.generate_document_embeddings(
                db,
                document,
            )
        )
    finally:
        embedding_processing.generate_document_embedding = original

    assert processed_count == 1
    generate_embedding.assert_awaited_once_with("Pending chunk")

    statement = db.execute.await_args.args[0]

    assert "document_chunks.embedding IS NULL" in str(statement)


@pytest.mark.asyncio
async def test_generate_document_embeddings_stops_on_embedding_failure():
    document = make_document()

    chunks = [
        make_chunk(0, "First chunk"),
        make_chunk(1, "Second chunk"),
        make_chunk(2, "Third chunk"),
    ]

    db = MagicMock()
    db.execute = AsyncMock(return_value=make_result(chunks))
    db.flush = AsyncMock()

    generate_embedding = AsyncMock(
        side_effect=[
            [0.1] * 768,
            RuntimeError("Simulated Gemini failure"),
        ]
    )

    original = embedding_processing.generate_document_embedding
    embedding_processing.generate_document_embedding = generate_embedding

    try:
        with pytest.raises(
            RuntimeError,
            match="Simulated Gemini failure",
        ):
            await embedding_processing.generate_document_embeddings(
                db,
                document,
            )
    finally:
        embedding_processing.generate_document_embedding = original

    assert chunks[0].embedding == [0.1] * 768
    assert chunks[1].embedding is None
    assert chunks[2].embedding is None

    assert generate_embedding.await_count == 2

    # The caller must roll back the transaction after this failure.
    db.flush.assert_not_awaited()
    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_generate_document_embeddings_rejects_unpersisted_document():
    document = SimpleNamespace(id=None)

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    with pytest.raises(
        ValueError,
        match="Document must be persisted",
    ):
        await embedding_processing.generate_document_embeddings(
            db,
            document,
        )

    db.execute.assert_not_awaited()
    db.flush.assert_not_awaited()
