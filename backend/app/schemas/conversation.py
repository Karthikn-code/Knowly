
from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class ConversationCreate(BaseModel):
    title: str = Field(
        default="New Conversation",
        min_length=1,
        max_length=255,
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Conversation title cannot be empty.")

        return value


class ConversationUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    is_pinned: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Conversation title cannot be empty.")

        return value

    @model_validator(mode="after")
    def validate_update(self):
        supplied_fields = self.model_fields_set

        if not supplied_fields:
            raise ValueError(
                "At least one field must be provided for an update."
            )

        if "title" in supplied_fields and self.title is None:
            raise ValueError("Conversation title cannot be null.")

        if "is_pinned" in supplied_fields and self.is_pinned is None:
            raise ValueError("Pin status cannot be null.")

        return self


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


class ConversationShareCreated(BaseModel):
    """Returned once when a new share link is created."""

    id: UUID
    share_url: str
    created_at: datetime


class SharedMessageRead(BaseModel):
    """Public message representation without private metadata."""

    role: str
    content: str
    created_at: datetime


class SharedConversationRead(BaseModel):
    """Read-only public representation of a shared conversation."""

    title: str
    messages: list[SharedMessageRead]
