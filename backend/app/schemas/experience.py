from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExperienceFields(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    role_title: str = Field(min_length=1, max_length=200)
    employment_type: str | None = Field(default=None, max_length=50)
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    description: str | None = None


class ExperienceCreate(ExperienceFields):
    display_order: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def normalize_dates(self) -> "ExperienceCreate":
        if self.is_current:
            self.end_date = None
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class ExperienceUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    role_title: str | None = Field(default=None, min_length=1, max_length=200)
    employment_type: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    description: str | None = None
    display_order: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "ExperienceUpdate":
        for field_name in ("company", "role_title", "start_date"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class ExperiencePublicRead(ExperienceFields):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class ExperienceAdminRead(ExperiencePublicRead):
    display_order: int
    created_at: datetime
    updated_at: datetime


class ExperienceReorderItem(BaseModel):
    id: UUID
    display_order: int = Field(ge=0)


class ExperienceReorder(BaseModel):
    items: list[ExperienceReorderItem] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_ids(self) -> "ExperienceReorder":
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("items must contain unique experience ids")
        return self
