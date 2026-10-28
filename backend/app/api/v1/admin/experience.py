from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.api.v1.admin.deps import AdminGuard
from app.db.deps import DatabaseSession
from app.models.experience import Experience
from app.repositories.experience import get_experience, list_experience
from app.schemas.common import DataResponse
from app.schemas.experience import (
    ExperienceAdminRead,
    ExperienceCreate,
    ExperienceReorder,
    ExperienceUpdate,
)

router = APIRouter(prefix="/experience", tags=["admin-experience"])


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Experience entry not found",
    )


def _validation_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"code": "VALIDATION_ERROR", "message": message},
    )


def _apply_fields(experience: Experience, data: dict[str, Any]) -> None:
    for field_name, value in data.items():
        setattr(experience, field_name, value)


def _admin_read(experience: Experience) -> ExperienceAdminRead:
    return ExperienceAdminRead.model_validate(experience)


@router.get("", response_model=DataResponse[list[ExperienceAdminRead]])
async def list_admin_experience(
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[ExperienceAdminRead]]:
    experiences = list_experience(db)
    return DataResponse(data=[_admin_read(experience) for experience in experiences])


@router.post(
    "",
    response_model=DataResponse[ExperienceAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_experience(
    payload: ExperienceCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ExperienceAdminRead]:
    experience = Experience(**payload.model_dump())
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return DataResponse(data=_admin_read(experience))


@router.patch("/reorder", response_model=DataResponse[list[ExperienceAdminRead]])
async def reorder_experience(
    payload: ExperienceReorder,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[ExperienceAdminRead]]:
    experiences = {experience.id: experience for experience in list_experience(db)}
    missing = [item.id for item in payload.items if item.id not in experiences]
    if missing:
        raise _not_found()

    for item in payload.items:
        experiences[item.id].display_order = item.display_order

    db.commit()
    return DataResponse(data=[_admin_read(experience) for experience in list_experience(db)])


@router.get("/{experience_id}", response_model=DataResponse[ExperienceAdminRead])
async def read_admin_experience(
    experience_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ExperienceAdminRead]:
    experience = get_experience(db, experience_id)
    if experience is None:
        raise _not_found()
    return DataResponse(data=_admin_read(experience))


@router.patch("/{experience_id}", response_model=DataResponse[ExperienceAdminRead])
async def update_experience(
    experience_id: UUID,
    payload: ExperienceUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ExperienceAdminRead]:
    experience = get_experience(db, experience_id)
    if experience is None:
        raise _not_found()

    data = payload.model_dump(exclude_unset=True)
    next_start_date = data.get("start_date", experience.start_date)
    next_end_date = data.get("end_date", experience.end_date)
    next_is_current = data.get("is_current", experience.is_current)

    if next_is_current:
        next_end_date = None
    if next_end_date is not None and next_end_date < next_start_date:
        raise _validation_error("end_date cannot be before start_date")

    _apply_fields(experience, data)
    experience.is_current = next_is_current
    experience.end_date = next_end_date

    db.commit()
    db.refresh(experience)
    return DataResponse(data=_admin_read(experience))


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    experience_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    experience = get_experience(db, experience_id)
    if experience is None:
        raise _not_found()

    db.delete(experience)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
