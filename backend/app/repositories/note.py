from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.note import Note


def list_public_notes(
    db: Session,
    *,
    limit: int,
    offset: int,
) -> tuple[list[Note], int]:
    filters = (Note.is_published.is_(True),)
    total = db.scalar(select(func.count()).select_from(Note).where(*filters)) or 0
    statement = (
        select(Note)
        .where(*filters)
        .order_by(Note.published_at.desc().nullslast(), Note.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement).all()), total


def get_public_note_by_slug(db: Session, slug: str) -> Note | None:
    statement = select(Note).where(Note.slug == slug, Note.is_published.is_(True))
    return db.scalar(statement)


def get_note_by_slug(db: Session, slug: str) -> Note | None:
    return db.scalar(select(Note).where(Note.slug == slug))


def list_admin_notes(db: Session) -> list[Note]:
    statement = select(Note).order_by(
        Note.published_at.desc().nullslast(),
        Note.created_at.desc(),
    )
    return list(db.scalars(statement).all())


def get_note(db: Session, note_id: UUID) -> Note | None:
    return db.get(Note, note_id)
