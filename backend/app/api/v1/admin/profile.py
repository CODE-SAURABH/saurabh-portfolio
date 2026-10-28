from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.v1.admin.deps import AdminGuard
from app.db.deps import DatabaseSession
from app.models.profile import Profile
from app.repositories.profile import get_profile
from app.schemas.common import DataResponse
from app.schemas.profile import ProfileRead, ProfileReplace, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["admin-profile"])


def _apply_profile_fields(profile: Profile, data: dict[str, Any]) -> None:
    for field_name, value in data.items():
        setattr(profile, field_name, value)


@router.get("", response_model=DataResponse[ProfileRead])
async def read_admin_profile(
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProfileRead]:
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return DataResponse(data=ProfileRead.model_validate(profile))


@router.put("", response_model=DataResponse[ProfileRead])
async def replace_admin_profile(
    payload: ProfileReplace,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProfileRead]:
    profile = get_profile(db)
    data = payload.model_dump()
    if profile is None:
        profile = Profile(**data)
        db.add(profile)
    else:
        _apply_profile_fields(profile, data)

    db.commit()
    db.refresh(profile)
    return DataResponse(data=ProfileRead.model_validate(profile))


@router.patch("", response_model=DataResponse[ProfileRead])
async def update_admin_profile(
    payload: ProfileUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProfileRead]:
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    _apply_profile_fields(profile, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(profile)
    return DataResponse(data=ProfileRead.model_validate(profile))
