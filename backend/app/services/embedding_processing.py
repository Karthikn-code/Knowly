
"""
Knowly embedding processing service.

Generates and stores Gemini embeddings for document chunks.
The caller owns transaction commit and rollback.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_document_embedding


async def generate_document_embeddings(
    db: AsyncSession,
    document: Document,
) -> int:
    """
    Generate and save embeddings for pending chunks of a document.

    The supplied Document must already have been loaded through
    an ownership-checked query by the calling endpoint.

    This function flushes changes but never commits or rolls back.
    """

    if document.id is None:
        raise ValueError("Document must be persisted before embedding.")

    result = await db.execute(
        select(DocumentChunk)
        .where(
            DocumentChunk.document_id == document.id,
            DocumentChunk.embedding.is_(None),
        )
        .order_by(DocumentChunk.chunk_index)
    )

    chunks = result.scalars().all()

    processed_count = 0

    for chunk in chunks:
        embedding = await generate_document_embedding(chunk.content)

        chunk.embedding = embedding
        processed_count += 1

    await db.flush()

    return processed_count
