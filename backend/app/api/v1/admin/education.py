from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.api.v1.admin.deps import AdminGuard
from app.db.deps import DatabaseSession
from app.models.education import Education
from app.repositories.education import get_education, list_education
from app.schemas.common import DataResponse
from app.schemas.education import (
    EducationAdminRead,
    EducationCreate,
    EducationUpdate,
)

router = APIRouter(prefix="/education", tags=["admin-education"])


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Education entry not found",
    )


def _validation_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"code": "VALIDATION_ERROR", "message": message},
    )


def _validate_dates(start_date: date, end_date: date | None) -> None:
    if end_date is not None and end_date < start_date:
        raise _validation_error("end_date cannot be before start_date")


def _apply_fields(education: Education, data: dict[str, Any]) -> None:
    for field_name, value in data.items():
        setattr(education, field_name, value)


def _admin_read(education: Education) -> EducationAdminRead:
    return EducationAdminRead.model_validate(education)


@router.get("", response_model=DataResponse[list[EducationAdminRead]])
async def list_admin_education(
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[EducationAdminRead]]:
    entries = list_education(db)
    return DataResponse(data=[_admin_read(entry) for entry in entries])


@router.post(
    "",
    response_model=DataResponse[EducationAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_education(
    payload: EducationCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[EducationAdminRead]:
    _validate_dates(payload.start_date, payload.end_date)
    education = Education(**payload.model_dump())
    db.add(education)
    db.commit()
    db.refresh(education)
    return DataResponse(data=_admin_read(education))


@router.get("/{education_id}", response_model=DataResponse[EducationAdminRead])
async def read_admin_education(
    education_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[EducationAdminRead]:
    education = get_education(db, education_id)
    if education is None:
        raise _not_found()
    return DataResponse(data=_admin_read(education))


@router.patch("/{education_id}", response_model=DataResponse[EducationAdminRead])
async def update_education(
    education_id: UUID,
    payload: EducationUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[EducationAdminRead]:
    education = get_education(db, education_id)
    if education is None:
        raise _not_found()

    data = payload.model_dump(exclude_unset=True)
    next_start_date = data.get("start_date", education.start_date)
    next_end_date = data.get("end_date", education.end_date)
    _validate_dates(next_start_date, next_end_date)

    _apply_fields(education, data)
    db.commit()
    db.refresh(education)
    return DataResponse(data=_admin_read(education))


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    education = get_education(db, education_id)
    if education is None:
        raise _not_found()

    db.delete(education)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
