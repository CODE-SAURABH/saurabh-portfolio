from fastapi import APIRouter

from app.db.deps import DatabaseSession
from app.repositories.experience import list_experience
from app.schemas.common import DataResponse
from app.schemas.experience import ExperiencePublicRead

router = APIRouter(prefix="/experience", tags=["experience"])


@router.get("", response_model=DataResponse[list[ExperiencePublicRead]])
async def read_experience(
    db: DatabaseSession,
) -> DataResponse[list[ExperiencePublicRead]]:
    experiences = list_experience(db)
    return DataResponse(
        data=[ExperiencePublicRead.model_validate(experience) for experience in experiences]
    )
