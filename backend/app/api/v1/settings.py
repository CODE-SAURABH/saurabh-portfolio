from fastapi import APIRouter, HTTPException, status

from app.db.deps import DatabaseSession
from app.repositories.settings import get_site_settings
from app.schemas.common import DataResponse
from app.schemas.settings import SiteSettingsPublicRead

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=DataResponse[SiteSettingsPublicRead])
async def read_settings(db: DatabaseSession) -> DataResponse[SiteSettingsPublicRead]:
    settings = get_site_settings(db)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not configured")
    return DataResponse(data=SiteSettingsPublicRead.model_validate(settings))
