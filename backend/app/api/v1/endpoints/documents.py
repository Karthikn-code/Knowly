
import asyncio
import logging
from pathlib import PurePath
from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import CSRFProtection
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.document import (
    CitationSourceRead,
    DocumentRead,
)
from app.services.audit import record_audit_event
from app.services.document_processing import save_document_chunks
from app.services.document_storage import (
    DocumentStorageError,
    document_storage,
)
from app.services.document_tasks import process_document_embeddings
from app.services.document_validation import (
    DocumentValidationError,
    SUPPORTED_TYPES,
    validate_and_extract,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

MAX_UPLOAD_SIZE = settings.MAX_UPLOAD_SIZE_BYTES
MAX_FILENAME_LENGTH = 255
UPLOAD_CHUNK_SIZE = 64 * 1024


async def get_owned_document(
    document_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> Document:
    """Retrieve a document only when it belongs to the user."""

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Validate, extract, store and process an uploaded document."""

    filename = file.filename

    if (
        not filename
        or len(filename) > MAX_FILENAME_LENGTH
        or filename in {".", ".."}
        or "\x00" in filename
        or "\r" in filename
        or "\n" in filename
        or PurePath(filename).name != filename
        or "/" in filename
        or "\\" in filename
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename.",
        )

    extension = PurePath(filename).suffix.lower()
    expected_type = SUPPORTED_TYPES.get(extension)

    if expected_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file format.",
        )

    declared_mime = file.content_type

    allowed_mime_types = {
        expected_type["mime_type"],
        "application/octet-stream",
    }

    if declared_mime and declared_mime not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Uploaded MIME type does not match the file extension.",
        )

    content = bytearray()

    try:
        while True:
            chunk = await file.read(UPLOAD_CHUNK_SIZE)

            if not chunk:
                break

            content.extend(chunk)

            if len(content) > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail="File exceeds the 10 MB upload limit.",
                )

    finally:
        await file.close()

    file_bytes = bytes(content)

    try:
        file_type, mime_type, extracted_text = await asyncio.to_thread(
            validate_and_extract,
            filename,
            file_bytes,
        )

    except DocumentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    storage_key = None

    try:
        # Save the original document in private storage.
        storage_key, file_size = await document_storage.save(file_bytes)

        # Create the document database record.
        document = Document(
            user_id=current_user.id,
            original_filename=filename,
            storage_key=storage_key,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            status="processing",
            extracted_text=extracted_text,
        )

        db.add(document)

        # Generate the document ID before creating its chunks.
        await db.flush()

        # Generate and save document chunks.
        chunk_count = await save_document_chunks(
            db=db,
            document=document,
        )

        logger.info(
            "Document chunking completed. "
            "Document ID: %s, Chunks: %s",
            document.id,
            chunk_count,
        )

        # Record the upload audit event.
        await record_audit_event(
            db,
            event_type="document.upload",
            outcome="success",
            request=request,
            user_id=current_user.id,
            resource_type="document",
            resource_id=str(document.id),
        )

        # Commit document, chunks and audit event together.
        await db.commit()
        await db.flush()

        await db.refresh(document)

    except Exception as exc:
        # Roll back document, chunks and audit event.
        await db.rollback()

        # Clean up the privately stored file only when
        # the database transaction has failed.
        if storage_key is not None:
            try:
                await document_storage.delete(storage_key)

            except DocumentStorageError:
                logger.exception(
                    "Failed to clean up a document after upload failure."
                )

        logger.exception("Document upload failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the document.",
        ) from exc

    # The database transaction is already committed.
    # Scheduling failure must never delete the persisted file.
    try:
        background_tasks.add_task(
            process_document_embeddings,
            document.id,
        )

    except Exception:
        logger.exception(
            "Could not schedule document embedding generation. "
            "The recovery service will retry the document."
        )

    return document


@router.get(
    "",
    response_model=list[DocumentRead],
)
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """List documents belonging to the authenticated user."""

    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(
            Document.created_at.desc(),
            Document.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return result.scalars().all()


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
)
async def get_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve metadata for an owned document."""

    return await get_owned_document(
        document_id,
        current_user.id,
        db,
    )


@router.get(
    "/{document_id}/chunks/{chunk_id}",
    response_model=CitationSourceRead,
)
async def get_citation_source(
    document_id: UUID,
    chunk_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve a cited document chunk belonging to the authenticated user."""

    # Verify that the parent document belongs to the current user.
    document = await get_owned_document(
        document_id,
        current_user.id,
        db,
    )

    # Verify that the requested chunk belongs to this document.
    result = await db.execute(
        select(DocumentChunk).where(
            DocumentChunk.id == chunk_id,
            DocumentChunk.document_id == document.id,
        )
    )

    source_chunk = result.scalar_one_or_none()

    if source_chunk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citation source not found.",
        )

    return CitationSourceRead(
        document_id=document.id,
        chunk_id=source_chunk.id,
        filename=document.original_filename,
        chunk_index=source_chunk.chunk_index,
        content=source_chunk.content,
        source_metadata=source_chunk.source_metadata,
    )


@router.get(
    "/{document_id}/download",
)
async def download_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Download a privately stored document."""

    document = await get_owned_document(
        document_id,
        current_user.id,
        db,
    )

    try:
        content = await document_storage.read(document.storage_key)

    except DocumentStorageError as exc:
        logger.exception("Unable to read stored document.")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored document not found.",
        ) from exc

    safe_filename = quote(
        document.original_filename,
        safe="",
    )

    return Response(
        content=content,
        media_type=document.mime_type,
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{safe_filename}"
            ),
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: UUID,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an owned document and its physical file."""

    document = await get_owned_document(
        document_id,
        current_user.id,
        db,
    )

    storage_key = document.storage_key

    try:
        await record_audit_event(
            db,
            event_type="document.delete",
            outcome="success",
            request=request,
            user_id=current_user.id,
            resource_type="document",
            resource_id=str(document.id),
        )

        await db.delete(document)
        await db.commit()
        await db.flush()
        await db.refresh(document)

    except Exception as exc:
        await db.rollback()

        logger.exception("Document deletion failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the document.",
        ) from exc

    try:
        await document_storage.delete(storage_key)

    except DocumentStorageError:
        logger.exception(
            "Document metadata was deleted, "
            "but physical file cleanup failed."
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
