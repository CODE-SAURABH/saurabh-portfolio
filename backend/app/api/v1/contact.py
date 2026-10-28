import hashlib
import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.core.config import get_settings
from app.db.deps import DatabaseSession
from app.repositories.contact import (
    count_recent_submissions_by_ip,
    create_contact_submission,
    mark_contact_notified,
)
from app.schemas.common import DataResponse, MessageData
from app.schemas.contact import ContactCreate

router = APIRouter(prefix="/contact", tags=["contact"])
logger = logging.getLogger(__name__)

RATE_LIMIT_PER_HOUR = 5


def _hash_ip(ip: str | None) -> str:
    secret = get_settings().SECRET_KEY
    raw = f"{secret}:{ip or 'unknown'}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("cf-connecting-ip")
    if forwarded:
        return forwarded
    return request.client.host if request.client else None


@router.post(
    "",
    response_model=DataResponse[MessageData],
    status_code=status.HTTP_201_CREATED,
)
async def submit_contact(
    body: ContactCreate,
    request: Request,
    db: DatabaseSession,
) -> DataResponse[MessageData]:
    ip_hash = _hash_ip(_client_ip(request))

    recent = count_recent_submissions_by_ip(db, ip_hash, hours=1)
    if recent >= RATE_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many submissions. Please try again later.",
        )

    submission = create_contact_submission(
        db,
        name=body.name,
        email=body.email,
        subject=body.subject,
        message=body.message,
        ip_hash=ip_hash,
    )

    try:
        from app.services.notify import send_contact_notification

        notified = await send_contact_notification(submission)
    except Exception:
        logger.exception("Contact notification raised unexpectedly")
        notified = False

    if notified:
        mark_contact_notified(db, submission)

    return DataResponse(
        data=MessageData(
            message="Thank you for reaching out. Your message has been received."
        )
    )
