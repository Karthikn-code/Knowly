
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    """Safe document metadata returned to the authenticated user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    file_type: str
    mime_type: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: datetime


class CitationSourceRead(BaseModel):
    """Source content returned for an authenticated citation preview."""

    document_id: UUID
    chunk_id: UUID
    filename: str
    chunk_index: int
    content: str
    source_metadata: dict[str, Any]
