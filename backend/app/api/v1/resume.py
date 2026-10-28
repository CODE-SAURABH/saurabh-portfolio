from fastapi import APIRouter, HTTPException, status

from app.db.deps import DatabaseSession
from app.repositories.settings import get_site_settings
from app.schemas.common import DataResponse
from app.schemas.resume import ResumeUploadResponse

router = APIRouter(prefix="/resume", tags=["resume"])


@router.get("", response_model=DataResponse[ResumeUploadResponse])
async def read_resume_url(db: DatabaseSession) -> DataResponse[ResumeUploadResponse]:
    settings = get_site_settings(db)
    if settings is None or not settings.resume_download_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not available yet",
        )
    return DataResponse(
        data=ResumeUploadResponse(resume_download_url=settings.resume_download_url)
    )
