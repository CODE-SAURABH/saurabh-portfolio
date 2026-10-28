from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    status,
)

from app.api.v1.admin.deps import require_admin
from app.db.deps import DatabaseSession
from app.repositories.settings import get_site_settings, update_site_settings
from app.schemas.common import DataResponse
from app.schemas.resume import ResumeUploadResponse
from app.services.storage import StorageUnavailableError, upload_resume_pdf

router = APIRouter(
    prefix="/resume",
    tags=["admin-resume"],
    dependencies=[Depends(require_admin)],
)

MAX_RESUME_BYTES = 5 * 1024 * 1024


def _validation_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"code": "VALIDATION_ERROR", "message": message},
    )


@router.get("", response_model=DataResponse[ResumeUploadResponse])
async def admin_read_resume(db: DatabaseSession) -> DataResponse[ResumeUploadResponse]:
    settings = get_site_settings(db)
    if settings is None or not settings.resume_download_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not available yet",
        )
    return DataResponse(
        data=ResumeUploadResponse(resume_download_url=settings.resume_download_url)
    )


@router.post(
    "/upload",
    response_model=DataResponse[ResumeUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def admin_upload_resume(
    file: UploadFile,
    db: DatabaseSession,
) -> DataResponse[ResumeUploadResponse]:
    if file.content_type != "application/pdf":
        raise _validation_error("Resume must be a PDF")

    data = await file.read(MAX_RESUME_BYTES + 1)
    if not data:
        raise _validation_error("Resume file is empty")
    if len(data) > MAX_RESUME_BYTES:
        raise _validation_error("Resume must be 5 MB or smaller")

    settings = get_site_settings(db)
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not configured",
        )

    try:
        url = await upload_resume_pdf(data)
    except StorageUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    update_site_settings(db, settings, resume_download_url=url)
    return DataResponse(data=ResumeUploadResponse(resume_download_url=url))
