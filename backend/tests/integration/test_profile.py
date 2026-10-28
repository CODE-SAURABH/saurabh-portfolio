import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.profile import Profile

client = TestClient(app)


def make_profile(**overrides: object) -> Profile:
    profile = Profile(
        full_name="Saurabh Patil",
        headline="AI / Software Engineer",
        bio="Building useful systems.",
        location="India / IST",
        email="saurabh@example.com",
        availability_note="Open to opportunities",
        **overrides,
    )
    profile.id = uuid.uuid4()
    profile.updated_at = datetime.now(UTC)
    return profile


class FakeProfileSession:
    def __init__(self, profile: Profile | None) -> None:
        self.profile = profile
        self.added: Profile | None = None
        self.committed = False

    def scalar(self, statement: object) -> Profile | None:
        return self.profile

    def add(self, profile: Profile) -> None:
        if getattr(profile, "id", None) is None:
            profile.id = uuid.uuid4()
        if getattr(profile, "updated_at", None) is None:
            profile.updated_at = datetime.now(UTC)
        self.added = profile
        self.profile = profile

    def commit(self) -> None:
        self.committed = True

    def refresh(self, profile: Profile) -> None:
        if getattr(profile, "id", None) is None:
            profile.id = uuid.uuid4()
        if getattr(profile, "updated_at", None) is None:
            profile.updated_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(profile: Profile | None) -> FakeProfileSession:
    session = FakeProfileSession(profile)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_profile_returns_profile() -> None:
    override_db(make_profile())

    response = client.get("/api/v1/profile")

    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == "Saurabh Patil"
    assert response.json()["data"]["email"] == "saurabh@example.com"


def test_public_profile_returns_404_when_missing() -> None:
    override_db(None)

    response = client.get("/api/v1/profile")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_admin_profile_requires_token() -> None:
    override_db(make_profile())

    response = client.get("/api/v1/admin/profile")

    assert response.status_code == 401


def test_admin_profile_returns_profile() -> None:
    override_db(make_profile())

    response = client.get("/api/v1/admin/profile", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["data"]["headline"] == "AI / Software Engineer"


def test_patch_updates_only_supplied_fields() -> None:
    session = override_db(make_profile())

    response = client.patch(
        "/api/v1/admin/profile",
        headers=auth_headers(),
        json={"bio": "Updated biography", "availability_note": "Exploring"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["bio"] == "Updated biography"
    assert response.json()["data"]["availability_note"] == "Exploring"
    assert response.json()["data"]["headline"] == "AI / Software Engineer"
    assert session.committed


def test_patch_rejects_null_required_field() -> None:
    override_db(make_profile())

    response = client.patch(
        "/api/v1/admin/profile",
        headers=auth_headers(),
        json={"full_name": None},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_returns_404_when_profile_missing() -> None:
    override_db(None)

    response = client.patch(
        "/api/v1/admin/profile",
        headers=auth_headers(),
        json={"bio": "Updated"},
    )

    assert response.status_code == 404


def test_put_creates_profile_when_missing() -> None:
    session = override_db(None)

    response = client.put(
        "/api/v1/admin/profile",
        headers=auth_headers(),
        json={
            "full_name": "Saurabh Patil",
            "headline": "AI / Software Engineer",
            "bio": "New profile",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["bio"] == "New profile"
    assert session.added is not None
    assert session.committed


def test_put_replaces_optional_fields() -> None:
    override_db(make_profile())

    response = client.put(
        "/api/v1/admin/profile",
        headers=auth_headers(),
        json={
            "full_name": "Saurabh Patil",
            "headline": "AI / Software Engineer",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["bio"] is None
    assert response.json()["data"]["location"] is None
