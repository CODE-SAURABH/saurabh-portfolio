import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.experience import Experience

client = TestClient(app)


def make_experience(**overrides: object) -> Experience:
    values: dict[str, object] = {
        "company": "Acme Systems",
        "role_title": "Software Engineer",
        "employment_type": "Full-time",
        "start_date": date(2024, 1, 1),
        "end_date": None,
        "is_current": True,
        "description": "Built useful systems.",
        "display_order": 0,
    }
    values.update(overrides)
    experience = Experience(**values)
    experience.id = uuid.uuid4()
    experience.created_at = datetime.now(UTC)
    experience.updated_at = datetime.now(UTC)
    return experience


class FakeScalars:
    def __init__(self, items: list[Experience]) -> None:
        self.items = items

    def all(self) -> list[Experience]:
        return self.items


class FakeExperienceSession:
    def __init__(self, experiences: list[Experience]) -> None:
        self.experiences = list(experiences)
        self.added: Experience | None = None
        self.deleted: Experience | None = None
        self.committed = False

    def scalars(self, statement: object) -> FakeScalars:
        ordered = sorted(
            self.experiences,
            key=lambda experience: (
                experience.display_order,
                -experience.start_date.toordinal(),
            ),
        )
        return FakeScalars(ordered)

    def get(self, model: object, experience_id: uuid.UUID) -> Experience | None:
        for experience in self.experiences:
            if experience.id == experience_id:
                return experience
        return None

    def add(self, experience: Experience) -> None:
        if getattr(experience, "id", None) is None:
            experience.id = uuid.uuid4()
        if getattr(experience, "created_at", None) is None:
            experience.created_at = datetime.now(UTC)
        if getattr(experience, "updated_at", None) is None:
            experience.updated_at = datetime.now(UTC)
        self.added = experience
        self.experiences.append(experience)

    def delete(self, experience: Experience) -> None:
        self.deleted = experience
        self.experiences.remove(experience)

    def commit(self) -> None:
        self.committed = True

    def refresh(self, experience: Experience) -> None:
        if getattr(experience, "id", None) is None:
            experience.id = uuid.uuid4()
        if getattr(experience, "created_at", None) is None:
            experience.created_at = datetime.now(UTC)
        if getattr(experience, "updated_at", None) is None:
            experience.updated_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(experiences: list[Experience]) -> FakeExperienceSession:
    session = FakeExperienceSession(experiences)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_experience_returns_ordered_entries() -> None:
    second = make_experience(company="Second", display_order=2)
    first = make_experience(company="First", display_order=1)
    override_db([second, first])

    response = client.get("/api/v1/experience")

    assert response.status_code == 200
    data = response.json()["data"]
    assert [entry["company"] for entry in data] == ["First", "Second"]
    assert "display_order" not in data[0]
    assert "created_at" not in data[0]


def test_public_experience_returns_empty_list() -> None:
    override_db([])

    response = client.get("/api/v1/experience")

    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_admin_experience_requires_token() -> None:
    override_db([make_experience()])

    response = client.get("/api/v1/admin/experience")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_admin_experience_lists_all_entries() -> None:
    override_db([make_experience(display_order=1), make_experience(display_order=0)])

    response = client.get("/api/v1/admin/experience", headers=auth_headers())

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["display_order"] == 0
    assert "updated_at" in data[0]


def test_create_experience_normalizes_current_role_dates() -> None:
    session = override_db([])

    response = client.post(
        "/api/v1/admin/experience",
        headers=auth_headers(),
        json={
            "company": "New Co",
            "role_title": "AI Engineer",
            "employment_type": "Full-time",
            "start_date": "2025-01-01",
            "end_date": "2025-06-01",
            "is_current": True,
            "description": "New role",
            "display_order": 3,
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["company"] == "New Co"
    assert data["end_date"] is None
    assert session.added is not None
    assert session.committed


def test_create_experience_rejects_invalid_date_range() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/experience",
        headers=auth_headers(),
        json={
            "company": "New Co",
            "role_title": "AI Engineer",
            "start_date": "2025-06-01",
            "end_date": "2025-01-01",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_experience_returns_entry() -> None:
    experience = make_experience()
    override_db([experience])

    response = client.get(
        f"/api/v1/admin/experience/{experience.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["data"]["company"] == "Acme Systems"


def test_get_experience_returns_404_when_missing() -> None:
    override_db([])

    response = client.get(
        f"/api/v1/admin/experience/{uuid.uuid4()}",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_patch_updates_only_supplied_fields() -> None:
    experience = make_experience()
    session = override_db([experience])

    response = client.patch(
        f"/api/v1/admin/experience/{experience.id}",
        headers=auth_headers(),
        json={"employment_type": "Contract", "description": "Updated description"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["employment_type"] == "Contract"
    assert data["description"] == "Updated description"
    assert data["company"] == "Acme Systems"
    assert session.committed


def test_patch_current_role_clears_end_date() -> None:
    experience = make_experience(end_date=date(2024, 12, 1), is_current=False)
    override_db([experience])

    response = client.patch(
        f"/api/v1/admin/experience/{experience.id}",
        headers=auth_headers(),
        json={"is_current": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["end_date"] is None


def test_patch_rejects_invalid_merged_date_range() -> None:
    experience = make_experience(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 1),
        is_current=False,
    )
    session = override_db([experience])

    response = client.patch(
        f"/api/v1/admin/experience/{experience.id}",
        headers=auth_headers(),
        json={"end_date": "2023-12-01"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert not session.committed


def test_delete_experience_removes_entry() -> None:
    experience = make_experience()
    session = override_db([experience])

    response = client.delete(
        f"/api/v1/admin/experience/{experience.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert session.deleted is experience
    assert session.committed


def test_delete_experience_returns_404_when_missing() -> None:
    override_db([])

    response = client.delete(
        f"/api/v1/admin/experience/{uuid.uuid4()}",
        headers=auth_headers(),
    )

    assert response.status_code == 404


def test_reorder_updates_display_order() -> None:
    first = make_experience(company="First", display_order=0)
    second = make_experience(company="Second", display_order=1)
    session = override_db([first, second])

    response = client.patch(
        "/api/v1/admin/experience/reorder",
        headers=auth_headers(),
        json={
            "items": [
                {"id": str(first.id), "display_order": 1},
                {"id": str(second.id), "display_order": 0},
            ]
        },
    )

    assert response.status_code == 200
    assert [entry["company"] for entry in response.json()["data"]] == ["Second", "First"]
    assert session.committed


def test_reorder_rejects_unknown_entry() -> None:
    override_db([make_experience()])

    response = client.patch(
        "/api/v1/admin/experience/reorder",
        headers=auth_headers(),
        json={"items": [{"id": str(uuid.uuid4()), "display_order": 0}]},
    )

    assert response.status_code == 404


def test_reorder_rejects_duplicate_ids() -> None:
    experience = make_experience()
    override_db([experience])

    response = client.patch(
        "/api/v1/admin/experience/reorder",
        headers=auth_headers(),
        json={
            "items": [
                {"id": str(experience.id), "display_order": 0},
                {"id": str(experience.id), "display_order": 1},
            ]
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
