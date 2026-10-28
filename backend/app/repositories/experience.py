from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.experience import Experience


def list_experience(db: Session) -> list[Experience]:
    statement = select(Experience).order_by(
        Experience.display_order.asc(),
        Experience.start_date.desc(),
    )
    return list(db.scalars(statement).all())


def get_experience(db: Session, experience_id: UUID) -> Experience | None:
    return db.get(Experience, experience_id)
