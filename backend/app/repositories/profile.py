from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile


def get_profile(db: Session) -> Profile | None:
    return db.scalar(select(Profile).limit(1))
