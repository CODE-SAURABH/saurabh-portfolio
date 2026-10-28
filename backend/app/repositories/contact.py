from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.contact import ContactSubmission


def create_contact_submission(
    db: Session,
    *,
    name: str,
    email: str,
    subject: str | None,
    message: str,
    ip_hash: str | None,
) -> ContactSubmission:
    submission = ContactSubmission(
        name=name,
        email=email,
        subject=subject,
        message=message,
        ip_hash=ip_hash,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def count_recent_submissions_by_ip(db: Session, ip_hash: str, hours: int = 1) -> int:
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    return (
        db.scalar(
            select(func.count())
            .select_from(ContactSubmission)
            .where(
                ContactSubmission.ip_hash == ip_hash,
                ContactSubmission.submitted_at >= cutoff,
            )
        )
        or 0
    )


def list_contact_submissions(db: Session) -> list[ContactSubmission]:
    return list(
        db.scalars(
            select(ContactSubmission).order_by(ContactSubmission.submitted_at.desc())
        ).all()
    )


def get_contact_submission(db: Session, submission_id: UUID) -> ContactSubmission | None:
    return db.get(ContactSubmission, submission_id)


def mark_contact_read(
    db: Session,
    submission: ContactSubmission,
    *,
    is_read: bool,
) -> ContactSubmission:
    submission.is_read = is_read
    db.commit()
    db.refresh(submission)
    return submission


def mark_contact_notified(
    db: Session,
    submission: ContactSubmission,
) -> ContactSubmission:
    submission.notified_at = datetime.now(UTC)
    db.commit()
    db.refresh(submission)
    return submission


def delete_contact_submission(db: Session, submission: ContactSubmission) -> None:
    db.delete(submission)
    db.commit()
