
"""
Knowly background document-processing tasks.

Uses PostgreSQL row-level locking to prevent duplicate processing.
Uses a separate database session from the upload request.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_processing import generate_document_embeddings

logger = logging.getLogger(__name__)

STALE_DOCUMENT_AGE = timedelta(hours=1)
RECOVERY_INTERVAL_SECONDS = 300


async def process_document_embeddings(document_id: UUID) -> None:
    """
    Generate embeddings for a document.

    A PostgreSQL row lock ensures that only one worker processes
    a document at a time.

    On failure, the transaction is rolled back and the document
    is marked failed in a separate transaction.
    """

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Document)
                .where(Document.id == document_id)
                .with_for_update()
            )

            document = result.scalar_one_or_none()

            if document is None:
                logger.warning(
                    "Document %s no longer exists.",
                    document_id,
                )
                return

            if document.status not in {"uploaded", "processing"}:
                logger.info(
                    "Skipping document %s with status %s.",
                    document_id,
                    document.status,
                )
                return

            await generate_document_embeddings(
                db=db,
                document=document,
            )

            total_result = await db.execute(
                select(func.count())
                .select_from(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
            )
            total_chunks = total_result.scalar_one()

            pending_result = await db.execute(
                select(func.count())
                .select_from(DocumentChunk)
                .where(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.embedding.is_(None),
                )
            )
            pending_chunks = pending_result.scalar_one()

            if total_chunks == 0:
                raise RuntimeError(
                    "Document processing produced no chunks."
                )

            if pending_chunks > 0:
                raise RuntimeError(
                    "Some document chunks still have missing embeddings."
                )

            document.status = "ready"
            await db.commit()

            logger.info(
                "Document %s processed successfully. Chunks: %s",
                document_id,
                total_chunks,
            )

    except Exception:
        logger.exception(
            "Embedding generation failed for document %s.",
            document_id,
        )

        try:
            async with AsyncSessionLocal() as failure_db:
                result = await failure_db.execute(
                    select(Document)
                    .where(Document.id == document_id)
                    .with_for_update()
                )

                document = result.scalar_one_or_none()

                if document is not None and document.status in {
                    "uploaded",
                    "processing",
                }:
                    document.status = "failed"
                    await failure_db.commit()

        except Exception:
            logger.exception(
                "Could not update failure status for document %s.",
                document_id,
            )


async def recover_stale_document_embeddings() -> int:
    """
    Find documents left in an intermediate state for over one hour
    and reschedule their embedding generation.

    Row-level locking inside process_document_embeddings prevents
    duplicate workers from generating embeddings simultaneously.
    """

    cutoff = datetime.now(timezone.utc) - STALE_DOCUMENT_AGE

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Document.id)
            .where(
                Document.status.in_(("uploaded", "processing")),
                Document.updated_at < cutoff,
            )
            .order_by(Document.created_at.asc())
        )

        document_ids = result.scalars().all()

    for document_id in document_ids:
        await process_document_embeddings(document_id)

    return len(document_ids)


async def document_recovery_loop() -> None:
    """
    Periodically recover interrupted document-processing tasks.
    """

    while True:
        try:
            recovered_count = await recover_stale_document_embeddings()

            if recovered_count:
                logger.info(
                    "Document recovery checked %s stale documents.",
                    recovered_count,
                )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Document recovery cycle failed."
            )

        await asyncio.sleep(RECOVERY_INTERVAL_SECONDS)
