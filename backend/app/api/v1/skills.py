from fastapi import APIRouter

from app.db.deps import DatabaseSession
from app.repositories.skill import list_skill_groups_with_skills
from app.schemas.common import DataResponse
from app.schemas.skill import SkillGroupRead

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=DataResponse[list[SkillGroupRead]])
async def read_skills(db: DatabaseSession) -> DataResponse[list[SkillGroupRead]]:
    groups = list_skill_groups_with_skills(db)
    return DataResponse(data=[SkillGroupRead.model_validate(g) for g in groups])
