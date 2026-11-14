
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.services.semantic_search import (
    _cosine_similarity,
    _select_diverse_chunks,
    semantic_search,
)


def make_candidate(
    content,
    embedding,
    distance,
    chunk_index=0,
):
    document_id = uuid4()

    chunk = SimpleNamespace(
        id=uuid4(),
        document_id=document_id,
        chunk_index=chunk_index,
        content=content,
        source_metadata={},
        embedding=embedding,
    )

    return chunk, "test_document.txt", distance


def test_cosine_similarity():
    assert _cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert _cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)
    assert _cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)


def test_cosine_similarity_handles_invalid_vectors():
    assert _cosine_similarity(None, [1, 0]) == 0.0
    assert _cosine_similarity([1, 0], [1, 0, 1]) == 0.0
    assert _cosine_similarity([0, 0], [1, 0]) == 0.0


def test_exact_duplicate_chunks_are_removed():
    candidates = [
        make_candidate(
            "Knowly uses semantic search.",
            [1, 0],
            0.10,
        ),
        make_candidate(
            "  KNOWLY uses semantic search.  ",
            [1, 0],
            0.12,
        ),
        make_candidate(
            "Knowly uses Gemini embeddings.",
            [0, 1],
            0.15,
        ),
    ]

    selected = _select_diverse_chunks(
        candidates,
        limit=5,
    )

    assert len(selected) == 2


def test_mmr_prioritizes_relevance_for_first_result():
    candidates = [
        make_candidate(
            "Highly relevant content.",
            [1, 0],
            0.05,
        ),
        make_candidate(
            "Less relevant content.",
            [0, 1],
            0.30,
        ),
    ]

    selected = _select_diverse_chunks(
        candidates,
        limit=1,
    )

    assert selected[0][0].content == "Highly relevant content."


def test_mmr_selects_diverse_chunks():
    candidates = [
        make_candidate(
            "Relevant content A.",
            [1, 0],
            0.05,
        ),
        make_candidate(
            "Very similar content B.",
            [0.99, 0.01],
            0.06,
        ),
        make_candidate(
            "Different useful content C.",
            [0, 1],
            0.12,
        ),
    ]

    selected = _select_diverse_chunks(
        candidates,
        limit=2,
    )

    assert len(selected) == 2
    assert selected[0][0].content == "Relevant content A."
    assert selected[1][0].content == "Different useful content C."


def test_mmr_respects_requested_limit():
    candidates = [
        make_candidate(
            f"Unique document content {index}.",
            [1, index + 1],
            0.05 + index * 0.01,
            chunk_index=index,
        )
        for index in range(8)
    ]

    selected = _select_diverse_chunks(
        candidates,
        limit=3,
    )

    assert len(selected) == 3


@pytest.mark.asyncio
async def test_semantic_search_retrieves_expanded_candidate_pool():
    user_id = uuid4()

    candidates = [
        make_candidate(
            f"Unique content {index}.",
            [1, index + 1],
            0.05 + index * 0.01,
            chunk_index=index,
        )
        for index in range(6)
    ]

    mock_db = SimpleNamespace(
        execute=AsyncMock(
            return_value=SimpleNamespace(all=lambda: candidates)
        )
    )

    with patch(
        "app.services.semantic_search.generate_query_embedding",
        new_callable=AsyncMock,
        return_value=[0.1, 0.2],
    ) as mock_embedding:
        results = await semantic_search(
            db=mock_db,
            user_id=user_id,
            query="Knowly retrieval",
            limit=2,
        )

    mock_embedding.assert_awaited_once_with("Knowly retrieval")
    mock_db.execute.assert_awaited_once()

    statement = mock_db.execute.await_args.args[0]

    # The expanded candidate pool should be three times the final limit.
    assert statement._limit_clause.value == 6

    assert len(results) == 2

    assert all(
        "chunk_id" in result
        and "document_id" in result
        and "filename" in result
        and "similarity" in result
        for result in results
    )


@pytest.mark.asyncio
async def test_semantic_search_rejects_empty_query():
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        await semantic_search(
            db=None,
            user_id=uuid4(),
            query="   ",
        )


@pytest.mark.asyncio
async def test_semantic_search_rejects_invalid_limit():
    with pytest.raises(ValueError, match="Search limit"):
        await semantic_search(
            db=None,
            user_id=uuid4(),
            query="Knowly",
            limit=25,
        )
