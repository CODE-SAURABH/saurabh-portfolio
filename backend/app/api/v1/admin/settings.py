from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.admin.deps import require_admin
from app.db.deps import DatabaseSession
from app.repositories.settings import get_site_settings, update_site_settings
from app.schemas.common import DataResponse
from app.schemas.settings import SiteSettingsAdminRead, SiteSettingsUpdate

router = APIRouter(
    prefix="/settings",
    tags=["admin-settings"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=DataResponse[SiteSettingsAdminRead])
async def admin_read_settings(db: DatabaseSession) -> DataResponse[SiteSettingsAdminRead]:
    settings = get_site_settings(db)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not configured")
    return DataResponse(data=SiteSettingsAdminRead.model_validate(settings))


@router.patch("", response_model=DataResponse[SiteSettingsAdminRead])
async def admin_update_settings(
    body: SiteSettingsUpdate,
    db: DatabaseSession,
) -> DataResponse[SiteSettingsAdminRead]:
    settings = get_site_settings(db)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not configured")
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return DataResponse(data=SiteSettingsAdminRead.model_validate(settings))
    updated = update_site_settings(db, settings, **updates)
    return DataResponse(data=SiteSettingsAdminRead.model_validate(updated))
