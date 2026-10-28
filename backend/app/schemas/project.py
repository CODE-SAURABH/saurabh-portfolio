from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

ProjectCategory = Literal["ai", "vision", "tools", "product"]
ProjectVisualType = Literal["rag", "vision", "nodes", "journal", "utility"]


class ProjectFields(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    short_description: str | None = Field(default=None, max_length=400)
    long_description: str | None = None
    status: str | None = Field(default=None, max_length=50)
    category: ProjectCategory
    visual_type: ProjectVisualType | None = None
    github_url: str | None = Field(default=None, max_length=500)
    live_url: str | None = Field(default=None, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=500)


class ProjectCreate(ProjectFields):
    is_published: bool = False
    is_featured: bool = False
    display_order: int = Field(default=0, ge=0)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    short_description: str | None = Field(default=None, max_length=400)
    long_description: str | None = None
    status: str | None = Field(default=None, max_length=50)
    category: ProjectCategory | None = None
    visual_type: ProjectVisualType | None = None
    is_published: bool | None = None
    is_featured: bool | None = None
    display_order: int | None = Field(default=None, ge=0)
    github_url: str | None = Field(default=None, max_length=500)
    live_url: str | None = Field(default=None, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "ProjectUpdate":
        for field_name in ("title", "slug", "category"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class ProjectFlagUpdate(BaseModel):
    value: bool


class ProjectTechnologyPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class ProjectTechnologyAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    display_order: int


class ProjectSectionPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    overline: str | None
    title: str
    body: str | None
    display_order: int


class ProjectSectionAdminRead(ProjectSectionPublicRead):
    pass


class ProjectPublicListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    short_description: str | None
    category: ProjectCategory
    visual_type: ProjectVisualType | None
    is_featured: bool
    display_order: int
    github_url: str | None
    live_url: str | None
    thumbnail_url: str | None
    technologies: list[ProjectTechnologyPublicRead]


class ProjectPublicDetail(ProjectPublicListItem):
    long_description: str | None
    status: str | None
    sections: list[ProjectSectionPublicRead]


class ProjectAdminListItem(ProjectFields):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_published: bool
    is_featured: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
    technologies: list[ProjectTechnologyAdminRead]


class ProjectAdminRead(ProjectAdminListItem):
    sections: list[ProjectSectionAdminRead]


class ProjectTechnologyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)


class ProjectSectionCreate(BaseModel):
    overline: str | None = Field(default=None, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    body: str | None = None
    display_order: int = Field(default=0, ge=0)


class ProjectSectionUpdate(BaseModel):
    overline: str | None = Field(default=None, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = None
    display_order: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "ProjectSectionUpdate":
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null")
        return self


class ProjectReorderItem(BaseModel):
    id: UUID
    display_order: int = Field(ge=0)


class ProjectReorder(BaseModel):
    items: list[ProjectReorderItem] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_ids(self) -> "ProjectReorder":
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("items must contain unique project ids")
        return self
