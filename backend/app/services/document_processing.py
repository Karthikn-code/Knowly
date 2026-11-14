
"""
Knowly document processing service.

Converts extracted document text into database chunks.
The caller owns transaction commit and rollback.
"""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_chunking import split_text_into_chunks

async def save_document_chunks(
    db: AsyncSession,
    document: Document,
    chunk_size: int = 3000,
    overlap: int = 400,
) -> int:
    """
    Generate and save chunks for an existing document.

    Existing chunks are replaced to support safe reprocessing.

    This function flushes changes but never commits or rolls back.
    Transaction management belongs to the calling endpoint.
    """

    if document.id is None:
        raise ValueError("Document must be persisted before processing.")

    extracted_text = document.extracted_text or ""

    chunks_data = split_text_into_chunks(
        extracted_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    # Remove previously generated chunks.
    await db.execute(
        delete(DocumentChunk).where(
            DocumentChunk.document_id == document.id
        )
    )

    chunk_records = [
        DocumentChunk(
            document_id=document.id,
            chunk_index=chunk["chunk_index"],
            content=chunk["content"],
            source_metadata=chunk["source_metadata"],
            embedding=None,
        )
        for chunk in chunks_data
    ]

    if chunk_records:
        db.add_all(chunk_records)

    await db.flush()

    return len(chunk_records)