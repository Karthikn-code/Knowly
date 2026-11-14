
"""
Knowly semantic search service.

Retrieves relevant and diverse document chunks using pgvector
cosine distance and Maximum Marginal Relevance (MMR).

All searches are restricted to the authenticated user's documents.
"""

import math
import re
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_query_embedding


# Retrieve additional candidates before selecting the final results.
CANDIDATE_MULTIPLIER = 3
MAX_CANDIDATES = 60

# Higher values prioritize relevance; lower values prioritize diversity.
MMR_RELEVANCE_WEIGHT = 0.75


def _normalize_content(content: str) -> str:
    """Normalize text for exact duplicate detection."""

    return re.sub(r"\s+", " ", content).strip().casefold()


def _cosine_similarity(
    vector_a: Any,
    vector_b: Any,
) -> float:
    """Calculate cosine similarity between two embedding vectors."""

    if vector_a is None or vector_b is None:
        return 0.0

    try:
        a = [float(value) for value in vector_a]
        b = [float(value) for value in vector_b]

        if not a or len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))

        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)

        return max(-1.0, min(1.0, similarity))

    except (TypeError, ValueError, OverflowError):
        return 0.0


def _select_diverse_chunks(
    candidates: list[tuple[Any, str, float]],
    limit: int,
) -> list[tuple[Any, str, float]]:
    """
    Select relevant and diverse chunks using MMR.

    Each candidate contains:
        (DocumentChunk, filename, cosine_distance)

    Relevance is derived from the database cosine distance.
    Diversity is derived from pairwise chunk embedding similarity.
    """

    if not candidates:
        return []

    remaining = list(candidates)
    selected: list[tuple[Any, str, float]] = []
    selected_embeddings: list[Any] = []

    # Remove exact duplicate content while preserving ranking order.
    unique_candidates = []
    seen_content = set()

    for candidate in remaining:
        chunk = candidate[0]
        normalized_content = _normalize_content(chunk.content)

        if not normalized_content:
            continue

        if normalized_content in seen_content:
            continue

        seen_content.add(normalized_content)
        unique_candidates.append(candidate)

    remaining = unique_candidates

    while remaining and len(selected) < limit:
        best_index = 0
        best_score = float("-inf")

        for index, candidate in enumerate(remaining):
            chunk, _, cosine_distance = candidate

            relevance = 1.0 - float(cosine_distance)

            if selected_embeddings:
                redundancy = max(
                    _cosine_similarity(
                        chunk.embedding,
                        selected_embedding,
                    )
                    for selected_embedding in selected_embeddings
                )
            else:
                redundancy = 0.0

            mmr_score = (
                MMR_RELEVANCE_WEIGHT * relevance
                - (1.0 - MMR_RELEVANCE_WEIGHT) * redundancy
            )

            if mmr_score > best_score:
                best_score = mmr_score
                best_index = index

        chosen = remaining.pop(best_index)

        selected.append(chosen)
        selected_embeddings.append(chosen[0].embedding)

    return selected


async def semantic_search(
    db: AsyncSession,
    user_id: UUID,
    query: str,
    limit: int = 5,
    document_id: UUID | None = None,
) -> list[dict[str, Any]]:
    """
    Search the authenticated user's document chunks.

    Retrieves an expanded candidate pool and applies MMR to
    improve relevance and reduce repetitive results.

    The caller must supply the authenticated user's ID.

    An optional document_id further restricts the search.

    This function does not commit or modify database records.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= limit <= 20:
        raise ValueError("Search limit must be between 1 and 20.")

    # Generate one query embedding.
    query_embedding = await generate_query_embedding(query.strip())

    # Retrieve more candidates than the final requested result count.
    candidate_limit = min(
        limit * CANDIDATE_MULTIPLIER,
        MAX_CANDIDATES,
    )

    cosine_distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("cosine_distance")

    # Preserve strict authenticated-user ownership filtering.
    statement = (
        select(
            DocumentChunk,
            Document.original_filename,
            cosine_distance,
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            Document.user_id == user_id,
            DocumentChunk.embedding.is_not(None),
        )
    )

    # Apply optional document-level filtering.
    if document_id is not None:
        statement = statement.where(
            DocumentChunk.document_id == document_id
        )

    statement = (
        statement
        .order_by(cosine_distance.asc())
        .limit(candidate_limit)
    )

    result = await db.execute(statement)

    candidates = result.all()

    # Select relevant, non-duplicate and diverse chunks.
    selected_chunks = _select_diverse_chunks(
        candidates=candidates,
        limit=limit,
    )

    # Preserve the existing output structure.
    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "filename": filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "source_metadata": chunk.source_metadata,
            "cosine_distance": float(distance),
            "similarity": 1.0 - float(distance),
        }
        for chunk, filename, distance in selected_chunks
    ]
