from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NoteFields(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    slug: str = Field(
        min_length=1,
        max_length=150,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    topic_label: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    body: str | None = None


class NoteCreate(NoteFields):
    is_published: bool = False
    published_at: datetime | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    topic_label: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    body: str | None = None
    is_published: bool | None = None
    published_at: datetime | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "NoteUpdate":
        for field_name in ("title", "slug"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class NotePublishUpdate(BaseModel):
    value: bool


class NotePublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    topic_label: str | None
    category: str | None
    body: str | None
    published_at: datetime | None


class NoteAdminRead(NotePublicRead):
    is_published: bool
    created_at: datetime
    updated_at: datetime
