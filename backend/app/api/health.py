import logging

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.db.deps import DatabaseSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response, db: DatabaseSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        logger.warning("Database readiness check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "db": "error"}

    return {"status": "ok", "db": "connected"}
