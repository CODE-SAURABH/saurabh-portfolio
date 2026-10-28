from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SiteSettingsPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    site_title: str
    tagline: str | None
    og_image_url: str | None
    resume_download_url: str | None


class SiteSettingsAdminRead(SiteSettingsPublicRead):
    id: UUID


class SiteSettingsUpdate(BaseModel):
    site_title: str | None = Field(default=None, min_length=1, max_length=200)
    tagline: str | None = Field(default=None, max_length=300)
    og_image_url: str | None = Field(default=None, max_length=500)
    resume_download_url: str | None = Field(default=None, max_length=500)

    @field_validator("site_title")
    @classmethod
    def site_title_cannot_be_null(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("site_title cannot be null")
        return value
