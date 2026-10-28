from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.api.v1.admin.deps import AdminGuard
from app.db.deps import DatabaseSession
from app.models.skill import Skill, SkillGroup
from app.repositories.skill import get_skill_group, list_skill_groups_with_skills
from app.schemas.common import DataResponse
from app.schemas.skill import (
    SkillAdminRead,
    SkillCreate,
    SkillGroupAdminRead,
    SkillGroupCreate,
    SkillGroupUpdate,
    SkillUpdate,
)

router = APIRouter(prefix="/skills", tags=["admin-skills"])


def _not_found(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message,
    )


def _conflict(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def _group_read(group: SkillGroup) -> SkillGroupAdminRead:
    return SkillGroupAdminRead.model_validate(group)


def _skill_read(skill: Skill) -> SkillAdminRead:
    return SkillAdminRead.model_validate(skill)


def _apply_fields(item: Any, data: dict[str, Any]) -> None:
    for field_name, value in data.items():
        setattr(item, field_name, value)


def _find_skill(group: SkillGroup, skill_id: UUID) -> Skill | None:
    return next((skill for skill in group.skills if skill.id == skill_id), None)


@router.get("", response_model=DataResponse[list[SkillGroupAdminRead]])
async def list_admin_skills(
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[SkillGroupAdminRead]]:
    groups = list_skill_groups_with_skills(db)
    return DataResponse(data=[_group_read(group) for group in groups])


@router.post(
    "/groups",
    response_model=DataResponse[SkillGroupAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_skill_group(
    payload: SkillGroupCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[SkillGroupAdminRead]:
    groups = list_skill_groups_with_skills(db)
    if any(group.name.casefold() == payload.name.casefold() for group in groups):
        raise _conflict("Skill group already exists")

    group = SkillGroup(**payload.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return DataResponse(data=_group_read(group))


@router.patch(
    "/groups/{group_id}",
    response_model=DataResponse[SkillGroupAdminRead],
)
async def update_skill_group(
    group_id: UUID,
    payload: SkillGroupUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[SkillGroupAdminRead]:
    group = get_skill_group(db, group_id)
    if group is None:
        raise _not_found("Skill group not found")

    data = payload.model_dump(exclude_unset=True)
    next_name = data.get("name")
    if next_name is not None:
        groups = list_skill_groups_with_skills(db)
        duplicate = any(
            other.id != group.id and other.name.casefold() == next_name.casefold()
            for other in groups
        )
        if duplicate:
            raise _conflict("Skill group already exists")

    _apply_fields(group, data)
    db.commit()
    db.refresh(group)
    return DataResponse(data=_group_read(group))


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_group(
    group_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    group = get_skill_group(db, group_id)
    if group is None:
        raise _not_found("Skill group not found")

    db.delete(group)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/groups/{group_id}/skills",
    response_model=DataResponse[SkillAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    group_id: UUID,
    payload: SkillCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[SkillAdminRead]:
    group = get_skill_group(db, group_id)
    if group is None:
        raise _not_found("Skill group not found")
    if any(
        skill.name.casefold() == payload.name.casefold() for skill in group.skills
    ):
        raise _conflict("Skill already exists in this group")

    skill = Skill(group_id=group.id, **payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return DataResponse(data=_skill_read(skill))


@router.patch(
    "/groups/{group_id}/skills/{skill_id}",
    response_model=DataResponse[SkillAdminRead],
)
async def update_skill(
    group_id: UUID,
    skill_id: UUID,
    payload: SkillUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[SkillAdminRead]:
    group = get_skill_group(db, group_id)
    if group is None:
        raise _not_found("Skill group not found")
    skill = _find_skill(group, skill_id)
    if skill is None:
        raise _not_found("Skill not found")

    data = payload.model_dump(exclude_unset=True)
    next_name = data.get("name")
    if next_name is not None:
        duplicate = any(
            other.id != skill.id and other.name.casefold() == next_name.casefold()
            for other in group.skills
        )
        if duplicate:
            raise _conflict("Skill already exists in this group")

    _apply_fields(skill, data)
    db.commit()
    db.refresh(skill)
    return DataResponse(data=_skill_read(skill))


@router.delete(
    "/groups/{group_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_skill(
    group_id: UUID,
    skill_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    group = get_skill_group(db, group_id)
    if group is None:
        raise _not_found("Skill group not found")
    skill = _find_skill(group, skill_id)
    if skill is None:
        raise _not_found("Skill not found")

    db.delete(skill)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
