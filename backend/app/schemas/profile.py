from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ProfileFields(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    headline: str = Field(min_length=1, max_length=200)
    bio: str | None = None
    location: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    github_url: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)
    website_url: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)
    availability_note: str | None = Field(default=None, max_length=200)


class ProfileReplace(ProfileFields):
    pass


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    headline: str | None = Field(default=None, min_length=1, max_length=200)
    bio: str | None = None
    location: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    github_url: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)
    website_url: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)
    availability_note: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "ProfileUpdate":
        for field_name in ("full_name", "headline"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class ProfileRead(ProfileFields):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    updated_at: datetime
