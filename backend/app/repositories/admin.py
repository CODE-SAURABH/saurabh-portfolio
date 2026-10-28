from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin import AdminCredential


def get_admin_credential(db: Session) -> AdminCredential | None:
    return db.scalar(select(AdminCredential).limit(1))
