import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.education import Education

client = TestClient(app)


def make_education(**overrides: object) -> Education:
    values: dict[str, object] = {
        "institution": "ADCET, Ashta",
        "degree": "B.Tech",
        "field": "Computer Science & Engineering",
        "start_date": date(2020, 8, 1),
        "end_date": date(2024, 6, 1),
        "description": None,
        "display_order": 0,
    }
    values.update(overrides)
    education = Education(**values)
    education.id = uuid.uuid4()
    education.created_at = datetime(2026, 10, 1, tzinfo=UTC)
    return education


class FakeScalars:
    def __init__(self, items: list[Education]) -> None:
        self.items = items

    def all(self) -> list[Education]:
        return self.items


class FakeEducationSession:
    def __init__(self, entries: list[Education]) -> None:
        self.entries = list(entries)
        self.added: object | None = None
        self.deleted: object | None = None
        self.commits = 0

    def scalars(self, statement: object) -> FakeScalars:
        ordered = sorted(
            self.entries,
            key=lambda entry: entry.display_order,
        )
        return FakeScalars(ordered)

    def get(self, model: object, education_id: uuid.UUID) -> Education | None:
        return next(
            (entry for entry in self.entries if entry.id == education_id),
            None,
        )

    def add(self, item: object) -> None:
        if isinstance(item, Education):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "created_at", None) is None:
                item.created_at = datetime.now(UTC)
            self.entries.append(item)
        self.added = item

    def delete(self, item: object) -> None:
        if isinstance(item, Education):
            self.entries.remove(item)
        self.deleted = item

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, item: Education) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid.uuid4()
        if getattr(item, "created_at", None) is None:
            item.created_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(entries: list[Education]) -> FakeEducationSession:
    session = FakeEducationSession(entries)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_education_lists_in_display_order() -> None:
    second = make_education(institution="Second", display_order=1)
    first = make_education(institution="First", display_order=0)
    override_db([second, first])

    response = client.get("/api/v1/education")

    assert response.status_code == 200
    data = response.json()["data"]
    assert [entry["institution"] for entry in data] == ["First", "Second"]


def test_admin_education_requires_token() -> None:
    override_db([make_education()])

    response = client.get("/api/v1/admin/education")

    assert response.status_code == 401


def test_admin_education_lists_created_at() -> None:
    override_db([make_education()])

    response = client.get("/api/v1/admin/education", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["data"][0]["created_at"] is not None


def test_create_education() -> None:
    session = override_db([])

    response = client.post(
        "/api/v1/admin/education",
        headers=auth_headers(),
        json={
            "institution": "New School",
            "degree": "B.Sc",
            "field": "Computer Science",
            "start_date": "2024-08-01",
            "end_date": "2027-06-01",
            "description": "Coursework.",
            "display_order": 2,
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["institution"] == "New School"
    assert data["display_order"] == 2
    assert isinstance(session.added, Education)
    assert session.commits == 1


def test_create_education_rejects_end_before_start() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/education",
        headers=auth_headers(),
        json={
            "institution": "New School",
            "degree": "B.Sc",
            "start_date": "2027-08-01",
            "end_date": "2024-06-01",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_education_validates_required_fields() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/education",
        headers=auth_headers(),
        json={"institution": "", "degree": ""},
    )

    assert response.status_code == 422


def test_read_education_returns_404_when_missing() -> None:
    override_db([])

    response = client.get(
        f"/api/v1/admin/education/{uuid.uuid4()}",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_patch_education_updates_fields() -> None:
    education = make_education()
    session = override_db([education])

    response = client.patch(
        f"/api/v1/admin/education/{education.id}",
        headers=auth_headers(),
        json={"degree": "M.Tech", "field": None},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["degree"] == "M.Tech"
    assert data["field"] is None
    assert session.commits == 1


def test_patch_education_rejects_invalid_date_order() -> None:
    education = make_education()
    override_db([education])

    response = client.patch(
        f"/api/v1/admin/education/{education.id}",
        headers=auth_headers(),
        json={"end_date": "2019-01-01"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_education_rejects_null_required_field() -> None:
    education = make_education()
    override_db([education])

    response = client.patch(
        f"/api/v1/admin/education/{education.id}",
        headers=auth_headers(),
        json={"institution": None},
    )

    assert response.status_code == 422


def test_delete_education() -> None:
    education = make_education()
    session = override_db([education])

    response = client.delete(
        f"/api/v1/admin/education/{education.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert session.deleted is education
    assert session.commits == 1
