from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.settings import SiteSettings


def get_site_settings(db: Session) -> SiteSettings | None:
    return db.scalar(select(SiteSettings).limit(1))


def update_site_settings(
    db: Session,
    settings: SiteSettings,
    **kwargs: object,
) -> SiteSettings:
    for key, value in kwargs.items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings
