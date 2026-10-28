import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.skill import Skill, SkillGroup

client = TestClient(app)


def make_skill(
    *,
    group_id: uuid.UUID,
    name: str = "Python",
    is_featured: bool = True,
    display_order: int = 0,
) -> Skill:
    skill = Skill(
        group_id=group_id,
        name=name,
        is_featured=is_featured,
        display_order=display_order,
    )
    skill.id = uuid.uuid4()
    skill.created_at = datetime(2026, 10, 1, tzinfo=UTC)
    return skill


def make_group(
    *,
    name: str = "Languages & Backend",
    display_order: int = 0,
    skill_names: list[str] | None = None,
) -> SkillGroup:
    group = SkillGroup(name=name, display_order=display_order)
    group.id = uuid.uuid4()
    group.skills = [
        make_skill(
            group_id=group.id,
            name=skill_name,
            is_featured=index < 2,
            display_order=index,
        )
        for index, skill_name in enumerate(skill_names or [])
    ]
    return group


class FakeScalars:
    def __init__(self, items: list[SkillGroup]) -> None:
        self.items = items

    def all(self) -> list[SkillGroup]:
        return self.items


class FakeSkillSession:
    def __init__(self, groups: list[SkillGroup]) -> None:
        self.groups = list(groups)
        self.added: object | None = None
        self.deleted: object | None = None
        self.commits = 0

    def scalars(self, statement: object) -> FakeScalars:
        ordered = sorted(self.groups, key=lambda group: group.display_order)
        return FakeScalars(ordered)

    def get(self, model: object, group_id: uuid.UUID) -> SkillGroup | None:
        return next((group for group in self.groups if group.id == group_id), None)

    def add(self, item: object) -> None:
        if isinstance(item, SkillGroup):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if not hasattr(item, "skills"):
                item.skills = []
            self.groups.append(item)
        if isinstance(item, Skill):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "created_at", None) is None:
                item.created_at = datetime.now(UTC)
            group = next(
                (group for group in self.groups if group.id == item.group_id),
                None,
            )
            if group is not None and item not in group.skills:
                group.skills.append(item)
        self.added = item

    def delete(self, item: object) -> None:
        if isinstance(item, SkillGroup):
            self.groups.remove(item)
        if isinstance(item, Skill):
            for group in self.groups:
                if item in group.skills:
                    group.skills.remove(item)
        self.deleted = item

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, item: object) -> None:
        if isinstance(item, SkillGroup) and getattr(item, "id", None) is None:
            item.id = uuid.uuid4()
        if isinstance(item, Skill):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "created_at", None) is None:
                item.created_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(groups: list[SkillGroup]) -> FakeSkillSession:
    session = FakeSkillSession(groups)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_skills_lists_groups_and_skills() -> None:
    group = make_group(skill_names=["Python", "FastAPI"])
    override_db([group])

    response = client.get("/api/v1/skills")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["name"] == "Languages & Backend"
    assert [skill["name"] for skill in data[0]["skills"]] == ["Python", "FastAPI"]


def test_admin_skills_requires_token() -> None:
    override_db([make_group()])

    response = client.get("/api/v1/admin/skills")

    assert response.status_code == 401


def test_admin_skills_includes_group_id() -> None:
    group = make_group(skill_names=["Python"])
    override_db([group])

    response = client.get("/api/v1/admin/skills", headers=auth_headers())

    assert response.status_code == 200
    skill = response.json()["data"][0]["skills"][0]
    assert skill["group_id"] == str(group.id)


def test_create_skill_group() -> None:
    session = override_db([])

    response = client.post(
        "/api/v1/admin/skills/groups",
        headers=auth_headers(),
        json={"name": "AI / ML / LLM", "display_order": 1},
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "AI / ML / LLM"
    assert data["skills"] == []
    assert isinstance(session.added, SkillGroup)
    assert session.commits == 1


def test_create_skill_group_rejects_duplicate_name() -> None:
    override_db([make_group(name="AI / ML / LLM")])

    response = client.post(
        "/api/v1/admin/skills/groups",
        headers=auth_headers(),
        json={"name": "ai / ml / llm"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_create_skill_group_validates_name() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/skills/groups",
        headers=auth_headers(),
        json={"name": ""},
    )

    assert response.status_code == 422


def test_update_skill_group() -> None:
    group = make_group()
    session = override_db([group])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}",
        headers=auth_headers(),
        json={"name": "Backend", "display_order": 3},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Backend"
    assert data["display_order"] == 3
    assert session.commits == 1


def test_update_skill_group_rejects_duplicate_name() -> None:
    group = make_group()
    override_db([group, make_group(name="Frontend", display_order=1)])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}",
        headers=auth_headers(),
        json={"name": "frontend"},
    )

    assert response.status_code == 409


def test_update_skill_group_rejects_null_name() -> None:
    group = make_group()
    override_db([group])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}",
        headers=auth_headers(),
        json={"name": None},
    )

    assert response.status_code == 422


def test_update_skill_group_returns_404_when_missing() -> None:
    override_db([])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{uuid.uuid4()}",
        headers=auth_headers(),
        json={"name": "Backend"},
    )

    assert response.status_code == 404


def test_delete_skill_group() -> None:
    group = make_group()
    session = override_db([group])

    response = client.delete(
        f"/api/v1/admin/skills/groups/{group.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert session.deleted is group
    assert session.commits == 1


def test_create_skill() -> None:
    group = make_group()
    session = override_db([group])

    response = client.post(
        f"/api/v1/admin/skills/groups/{group.id}/skills",
        headers=auth_headers(),
        json={"name": "SQL", "is_featured": True, "display_order": 1},
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "SQL"
    assert data["group_id"] == str(group.id)
    assert isinstance(session.added, Skill)
    assert session.commits == 1


def test_create_skill_rejects_duplicate_name() -> None:
    group = make_group(skill_names=["Python"])
    override_db([group])

    response = client.post(
        f"/api/v1/admin/skills/groups/{group.id}/skills",
        headers=auth_headers(),
        json={"name": "python"},
    )

    assert response.status_code == 409


def test_create_skill_returns_404_for_missing_group() -> None:
    override_db([])

    response = client.post(
        f"/api/v1/admin/skills/groups/{uuid.uuid4()}/skills",
        headers=auth_headers(),
        json={"name": "SQL"},
    )

    assert response.status_code == 404


def test_update_skill() -> None:
    group = make_group(skill_names=["Python", "FastAPI"])
    skill = group.skills[0]
    session = override_db([group])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}/skills/{skill.id}",
        headers=auth_headers(),
        json={"name": "Python 3", "is_featured": False, "display_order": 2},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Python 3"
    assert data["is_featured"] is False
    assert data["display_order"] == 2
    assert session.commits == 1


def test_update_skill_rejects_duplicate_name() -> None:
    group = make_group(skill_names=["Python", "FastAPI"])
    skill = group.skills[0]
    override_db([group])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}/skills/{skill.id}",
        headers=auth_headers(),
        json={"name": "fastapi"},
    )

    assert response.status_code == 409


def test_update_skill_rejects_null_name() -> None:
    group = make_group(skill_names=["Python"])
    skill = group.skills[0]
    override_db([group])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}/skills/{skill.id}",
        headers=auth_headers(),
        json={"name": None},
    )

    assert response.status_code == 422


def test_update_skill_returns_404_for_skill_in_other_group() -> None:
    group = make_group(skill_names=["Python"])
    other = make_group(name="Frontend", skill_names=["React"])
    override_db([group, other])

    response = client.patch(
        f"/api/v1/admin/skills/groups/{group.id}/skills/{other.skills[0].id}",
        headers=auth_headers(),
        json={"name": "Vue"},
    )

    assert response.status_code == 404


def test_delete_skill() -> None:
    group = make_group(skill_names=["Python", "FastAPI"])
    skill = group.skills[0]
    session = override_db([group])

    response = client.delete(
        f"/api/v1/admin/skills/groups/{group.id}/skills/{skill.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert session.deleted is skill
    assert session.commits == 1
