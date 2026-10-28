from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.elements import ColumnElement

from app.models.project import Project


def list_public_projects(
    db: Session,
    *,
    featured: bool | None,
    category: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Project], int]:
    filters: list[ColumnElement[bool]] = [Project.is_published.is_(True)]
    if featured is not None:
        filters.append(Project.is_featured.is_(featured))
    if category is not None:
        filters.append(Project.category == category)

    total = db.scalar(select(func.count()).select_from(Project).where(*filters)) or 0
    statement = (
        select(Project)
        .where(*filters)
        .options(selectinload(Project.technologies))
        .order_by(Project.display_order.asc(), Project.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement).all()), total


def get_public_project_by_slug(db: Session, slug: str) -> Project | None:
    statement = (
        select(Project)
        .where(Project.slug == slug, Project.is_published.is_(True))
        .options(
            selectinload(Project.technologies),
            selectinload(Project.sections),
        )
    )
    return db.scalar(statement)


def get_project_by_slug(db: Session, slug: str) -> Project | None:
    return db.scalar(select(Project).where(Project.slug == slug))


def list_admin_projects(db: Session) -> list[Project]:
    statement = (
        select(Project)
        .options(selectinload(Project.technologies))
        .order_by(Project.display_order.asc(), Project.created_at.asc())
    )
    return list(db.scalars(statement).all())


def get_admin_project(db: Session, project_id: UUID) -> Project | None:
    return db.get(Project, project_id)
