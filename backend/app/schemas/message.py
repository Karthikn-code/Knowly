
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MessageCreate(BaseModel):
    """Schema for a message submitted by the authenticated user."""

    content: str = Field(
        min_length=1,
        max_length=20000,
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message content cannot be empty.")

        return value


class MessageRead(BaseModel):
    """Schema for returning a stored conversation message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    citations: list[dict[str, Any]]
    created_at: datetime
