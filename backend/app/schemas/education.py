from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EducationPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    institution: str
    degree: str
    field: str | None
    start_date: date
    end_date: date | None
    description: str | None
    display_order: int


class EducationCreate(BaseModel):
    institution: str = Field(min_length=1, max_length=300)
    degree: str = Field(min_length=1, max_length=200)
    field: str | None = Field(default=None, max_length=200)
    start_date: date
    end_date: date | None = None
    description: str | None = None
    display_order: int = Field(default=0, ge=0)


class EducationUpdate(BaseModel):
    institution: str | None = Field(default=None, min_length=1, max_length=300)
    degree: str | None = Field(default=None, min_length=1, max_length=200)
    field: str | None = Field(default=None, max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    display_order: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "EducationUpdate":
        for field_name in ("institution", "degree", "start_date"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class EducationAdminRead(EducationPublicRead):
    created_at: datetime
