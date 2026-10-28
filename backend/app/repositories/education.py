from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.education import Education


def list_education(db: Session) -> list[Education]:
    return list(
        db.scalars(
            select(Education).order_by(Education.display_order.asc())
        ).all()
    )


def get_education(db: Session, education_id: UUID) -> Education | None:
    return db.get(Education, education_id)
