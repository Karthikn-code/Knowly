
import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.db.session import AsyncSessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.semantic_search import semantic_search


pytestmark = pytest.mark.skipif(
    os.getenv("KNOWLY_RUN_DB_INTEGRATION") != "1",
    reason="Set KNOWLY_RUN_DB_INTEGRATION=1 to run PostgreSQL integration tests.",
)


def make_test_embedding():
    """Create a deterministic 768-dimensional test vector."""
    return [1.0] + [0.0] * 767


@pytest.mark.asyncio
async def test_postgres_semantic_search_enforces_real_user_ownership():
    user_a_id = uuid4()
    user_b_id = uuid4()
    document_id = uuid4()

    unique_phrase = f"PRIVATE-OWNERSHIP-TEST-{uuid4()}"

    async with AsyncSessionLocal() as db:
        try:
            user_a = User(
                id=user_a_id,
                google_sub=f"ownership-test-a-{uuid4()}",
                email=f"ownership-test-a-{uuid4()}@example.test",
                full_name="Temporary Ownership Test A",
                is_active=True,
            )

            user_b = User(
                id=user_b_id,
                google_sub=f"ownership-test-b-{uuid4()}",
                email=f"ownership-test-b-{uuid4()}@example.test",
                full_name="Temporary Ownership Test B",
                is_active=True,
            )

            document = Document(
                id=document_id,
                user_id=user_a_id,
                original_filename="temporary-private-test.txt",
                storage_key=f"ownership-test/{uuid4()}.txt",
                file_type="txt",
                mime_type="text/plain",
                file_size=len(unique_phrase),
                status="ready",
                extracted_text=unique_phrase,
            )

            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=0,
                content=unique_phrase,
                source_metadata={},
                embedding=make_test_embedding(),
            )

            db.add_all([user_a, user_b, document, chunk])
            await db.flush()

            with patch(
                "app.services.semantic_search.generate_query_embedding",
                new_callable=AsyncMock,
                return_value=make_test_embedding(),
            ):
                # Owner A must retrieve the document.
                user_a_results = await semantic_search(
                    db=db,
                    user_id=user_a_id,
                    query="Find my private ownership test document",
                    limit=5,
                )

                # User B must not retrieve User A's document.
                user_b_results = await semantic_search(
                    db=db,
                    user_id=user_b_id,
                    query="Find my private ownership test document",
                    limit=5,
                )

            assert any(
                result["document_id"] == document_id
                for result in user_a_results
            ), "Document owner could not retrieve their own document."

            assert all(
                result["document_id"] != document_id
                for result in user_b_results
            ), "SECURITY FAILURE: another user retrieved a private document."

            assert user_b_results == [], (
                "User B unexpectedly received search results from "
                "User A's only test document."
            )

        finally:
            # Remove all temporary database records without committing.
            await db.rollback()
