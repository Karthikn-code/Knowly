from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services import document_tasks


def make_session_context(db):
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=db)
    context.__aexit__ = AsyncMock(return_value=False)
    return context


def make_document_result(document):
    return SimpleNamespace(
        scalar_one_or_none=lambda: document
    )


def make_count_result(count):
    return SimpleNamespace(
        scalar_one=lambda: count
    )


@pytest.mark.asyncio
async def test_successful_document_processing(monkeypatch):
    document = SimpleNamespace(
        id=uuid4(),
        status="processing",
    )

    db = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            make_document_result(document),
            make_count_result(2),
            make_count_result(0),
        ]
    )
    db.commit = AsyncMock()

    monkeypatch.setattr(
        document_tasks,
        "AsyncSessionLocal",
        MagicMock(return_value=make_session_context(db)),
    )

    generate_embeddings = AsyncMock(return_value=2)

    monkeypatch.setattr(
        document_tasks,
        "generate_document_embeddings",
        generate_embeddings,
    )

    await document_tasks.process_document_embeddings(document.id)

    assert document.status == "ready"
    generate_embeddings.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_embedding_failure_marks_document_failed(monkeypatch):
    document = SimpleNamespace(
        id=uuid4(),
        status="processing",
    )

    processing_db = MagicMock()
    processing_db.execute = AsyncMock(
        return_value=make_document_result(document)
    )

    failure_db = MagicMock()
    failure_db.execute = AsyncMock(
        return_value=make_document_result(document)
    )
    failure_db.commit = AsyncMock()

    contexts = [
        make_session_context(processing_db),
        make_session_context(failure_db),
    ]

    monkeypatch.setattr(
        document_tasks,
        "AsyncSessionLocal",
        MagicMock(side_effect=contexts),
    )

    monkeypatch.setattr(
        document_tasks,
        "generate_document_embeddings",
        AsyncMock(
            side_effect=RuntimeError("Simulated Gemini failure")
        ),
    )

    await document_tasks.process_document_embeddings(document.id)

    assert document.status == "failed"
    failure_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_deleted_document_is_skipped(monkeypatch):
    document_id = uuid4()

    db = MagicMock()
    db.execute = AsyncMock(
        return_value=make_document_result(None)
    )

    monkeypatch.setattr(
        document_tasks,
        "AsyncSessionLocal",
        MagicMock(return_value=make_session_context(db)),
    )

    generate_embeddings = AsyncMock()

    monkeypatch.setattr(
        document_tasks,
        "generate_document_embeddings",
        generate_embeddings,
    )

    await document_tasks.process_document_embeddings(document_id)

    generate_embeddings.assert_not_awaited()
    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_non_processing_document_is_skipped(monkeypatch):
    document = SimpleNamespace(
        id=uuid4(),
        status="ready",
    )

    db = MagicMock()
    db.execute = AsyncMock(
        return_value=make_document_result(document)
    )

    monkeypatch.setattr(
        document_tasks,
        "AsyncSessionLocal",
        MagicMock(return_value=make_session_context(db)),
    )

    generate_embeddings = AsyncMock()

    monkeypatch.setattr(
        document_tasks,
        "generate_document_embeddings",
        generate_embeddings,
    )

    await document_tasks.process_document_embeddings(document.id)

    generate_embeddings.assert_not_awaited()
    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_duplicate_task_skips_already_ready_document(monkeypatch):
    document = SimpleNamespace(
        id=uuid4(),
        status="processing",
    )

    first_db = MagicMock()
    first_db.execute = AsyncMock(
        side_effect=[
            make_document_result(document),
            make_count_result(2),
            make_count_result(0),
        ]
    )
    first_db.commit = AsyncMock()

    second_db = MagicMock()
    second_db.execute = AsyncMock(
        return_value=make_document_result(document)
    )

    contexts = [
        make_session_context(first_db),
        make_session_context(second_db),
    ]

    monkeypatch.setattr(
        document_tasks,
        "AsyncSessionLocal",
        MagicMock(side_effect=contexts),
    )

    generate_embeddings = AsyncMock(return_value=2)

    monkeypatch.setattr(
        document_tasks,
        "generate_document_embeddings",
        generate_embeddings,
    )

    await document_tasks.process_document_embeddings(document.id)
    await document_tasks.process_document_embeddings(document.id)

    assert document.status == "ready"
    generate_embeddings.assert_awaited_once()
    first_db.commit.assert_awaited_once()
    second_db.commit.assert_not_called()

    # Confirm that processing uses a database row lock.
    first_statement = first_db.execute.await_args_list[0].args[0]
    assert first_statement._for_update_arg is not None


@pytest.mark.asyncio
async def test_recovery_reschedules_stale_documents(monkeypatch):
    document_ids = [uuid4(), uuid4()]

    db = MagicMock()
    db.execute = AsyncMock(
        return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(
                all=lambda: document_ids
            )
        )
    )

    monkeypatch.setattr(
        document_tasks,
        "AsyncSessionLocal",
        MagicMock(return_value=make_session_context(db)),
    )

    process_document = AsyncMock()

    monkeypatch.setattr(
        document_tasks,
        "process_document_embeddings",
        process_document,
    )

    recovered_count = (
        await document_tasks.recover_stale_document_embeddings()
    )

    assert recovered_count == 2

    assert [
        call.args[0]
        for call in process_document.await_args_list
    ] == document_ids

    db.execute.assert_awaited_once()
