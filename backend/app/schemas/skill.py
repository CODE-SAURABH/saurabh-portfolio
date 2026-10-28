from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_featured: bool
    display_order: int


class SkillGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    display_order: int
    skills: list[SkillRead]


class SkillAdminRead(SkillRead):
    group_id: UUID


class SkillGroupAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    display_order: int
    skills: list[SkillAdminRead]


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    is_featured: bool = False
    display_order: int = Field(default=0, ge=0)


class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_featured: bool | None = None
    display_order: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_null_name(self) -> "SkillUpdate":
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")
        return self


class SkillGroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)


class SkillGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    display_order: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_null_name(self) -> "SkillGroupUpdate":
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")
        return self
