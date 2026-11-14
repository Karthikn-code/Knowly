from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.services.semantic_search import semantic_search


@pytest.mark.asyncio
async def test_semantic_search_always_filters_by_authenticated_user():
    user_id = uuid4()

    mock_db = SimpleNamespace(
        execute=AsyncMock(
            return_value=SimpleNamespace(all=lambda: [])
        )
    )

    with patch(
        "app.services.semantic_search.generate_query_embedding",
        new_callable=AsyncMock,
        return_value=[0.1, 0.2],
    ):
        await semantic_search(
            db=mock_db,
            user_id=user_id,
            query="Private document search",
            limit=5,
        )

    statement = mock_db.execute.await_args.args[0]
    compiled = statement.compile()

    # The generated SQL must contain the document ownership predicate.
    assert "documents.user_id" in str(compiled)

    # The authenticated user ID must be bound to the SQL query.
    assert user_id in compiled.params.values()


@pytest.mark.asyncio
async def test_document_filter_preserves_user_ownership_restriction():
    user_id = uuid4()
    document_id = uuid4()

    mock_db = SimpleNamespace(
        execute=AsyncMock(
            return_value=SimpleNamespace(all=lambda: [])
        )
    )

    with patch(
        "app.services.semantic_search.generate_query_embedding",
        new_callable=AsyncMock,
        return_value=[0.1, 0.2],
    ):
        await semantic_search(
            db=mock_db,
            user_id=user_id,
            query="Search within one document",
            document_id=document_id,
            limit=5,
        )

    statement = mock_db.execute.await_args.args[0]
    compiled = statement.compile()

    sql = str(compiled)
    parameters = compiled.params.values()

    # Both restrictions must remain in the same SQL query.
    assert "documents.user_id" in sql
    assert "document_chunks.document_id" in sql

    assert user_id in parameters
    assert document_id in parameters
