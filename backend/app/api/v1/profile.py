from fastapi import APIRouter, HTTPException, status

from app.db.deps import DatabaseSession
from app.repositories.profile import get_profile
from app.schemas.common import DataResponse
from app.schemas.profile import ProfileRead

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=DataResponse[ProfileRead])
async def read_profile(db: DatabaseSession) -> DataResponse[ProfileRead]:
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return DataResponse(data=ProfileRead.model_validate(profile))
