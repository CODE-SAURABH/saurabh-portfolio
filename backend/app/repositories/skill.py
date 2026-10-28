from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.skill import SkillGroup


def list_skill_groups_with_skills(db: Session) -> list[SkillGroup]:
    return list(
        db.scalars(
            select(SkillGroup)
            .options(selectinload(SkillGroup.skills))
            .order_by(SkillGroup.display_order.asc())
        ).all()
    )


def get_skill_group(db: Session, group_id: UUID) -> SkillGroup | None:
    return db.get(SkillGroup, group_id)
