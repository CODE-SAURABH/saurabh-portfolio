from fastapi import APIRouter

from app.db.deps import DatabaseSession
from app.repositories.education import list_education
from app.schemas.common import DataResponse
from app.schemas.education import EducationPublicRead

router = APIRouter(prefix="/education", tags=["education"])


@router.get("", response_model=DataResponse[list[EducationPublicRead]])
async def read_education(db: DatabaseSession) -> DataResponse[list[EducationPublicRead]]:
    entries = list_education(db)
    return DataResponse(data=[EducationPublicRead.model_validate(e) for e in entries])
