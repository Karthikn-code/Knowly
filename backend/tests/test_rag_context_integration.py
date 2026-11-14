
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.services.rag_service import answer_question


@pytest.mark.asyncio
async def test_rag_uses_contextual_query_for_semantic_search():
    user_id = uuid4()
    document_id = uuid4()

    question = "What technologies does it use?"

    history = [
        {
            "role": "user",
            "content": "What is Medi-Van?",
        },
        {
            "role": "assistant",
            "content": (
                "Medi-Van is an automated hospital "
                "transport system."
            ),
        },
    ]

    retrieved_chunk = {
        "filename": "medi_van.txt",
        "document_id": document_id,
        "chunk_id": uuid4(),
        "chunk_index": 0,
        "content": (
            "Medi-Van uses Raspberry Pi, Python, "
            "YOLOv8 and A* path planning."
        ),
        "source_metadata": {},
        "similarity": 0.92,
    }

    mock_semantic_search = AsyncMock(
        return_value=[retrieved_chunk]
    )

    mock_generate_response = AsyncMock(
        return_value=(
            "Medi-Van uses Raspberry Pi, Python, "
            "YOLOv8 and A* path planning [S1]."
        )
    )

    with (
        patch(
            "app.services.rag_service.semantic_search",
            mock_semantic_search,
        ),
        patch(
            "app.services.rag_service.generate_response",
            mock_generate_response,
        ),
    ):
        result = await answer_question(
            db=None,
            user_id=user_id,
            question=question,
            document_id=document_id,
            history=history,
        )

    # Verify semantic search received the contextualized query.
    mock_semantic_search.assert_awaited_once()

    search_arguments = mock_semantic_search.await_args.kwargs

    assert search_arguments["user_id"] == user_id
    assert search_arguments["document_id"] == document_id
    assert search_arguments["limit"] == 5

    contextual_query = search_arguments["query"]

    assert "Medi-Van" in contextual_query
    assert "automated hospital transport system" in contextual_query
    assert question in contextual_query

    # Verify Gemini receives the original question.
    mock_generate_response.assert_awaited_once()

    generation_prompt = (
        mock_generate_response.await_args.args[0]
    )

    assert f"USER QUESTION:\n{question}" in generation_prompt

    # Verify the existing response structure is preserved.
    assert result["answer"].startswith("Medi-Van uses")
    assert len(result["citations"]) == 1
    assert result["citations"][0]["source_id"] == "S1"
    assert result["retrieved_chunks"] == [retrieved_chunk]

@pytest.mark.asyncio
async def test_rag_returns_fallback_when_no_documents_are_retrieved():
    user_id = uuid4()
    question = "Explain the Medi-Van architecture."

    mock_semantic_search = AsyncMock(return_value=[])
    mock_generate_response = AsyncMock()

    with (
        patch(
            "app.services.rag_service.semantic_search",
            mock_semantic_search,
        ),
        patch(
            "app.services.rag_service.generate_response",
            mock_generate_response,
        ),
    ):
        result = await answer_question(
            db=None,
            user_id=user_id,
            question=question,
        )

    mock_semantic_search.assert_awaited_once()
    mock_generate_response.assert_not_awaited()

    assert result["answer"] == (
        "I couldn't find relevant information in your "
        "uploaded documents to answer this question."
    )
    assert result["citations"] == []
    assert result["retrieved_chunks"] == []