import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.settings import SiteSettings

client = TestClient(app)


def make_settings(**overrides: object) -> SiteSettings:
    values: dict[str, object] = {
        "site_title": "Saurabh Patil - AI & Software Engineer",
        "tagline": "AI Systems, Built With Intent",
        "og_image_url": None,
        "resume_download_url": None,
    }
    values.update(overrides)
    settings = SiteSettings(**values)
    settings.id = uuid.uuid4()
    settings.updated_at = datetime(2026, 10, 1, tzinfo=UTC)
    return settings


class FakeSettingsSession:
    def __init__(self, settings: SiteSettings | None) -> None:
        self.settings = settings
        self.commits = 0

    def scalar(self, statement: object) -> SiteSettings | None:
        return self.settings

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, item: SiteSettings) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid.uuid4()
        if getattr(item, "updated_at", None) is None:
            item.updated_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(settings: SiteSettings | None) -> FakeSettingsSession:
    session = FakeSettingsSession(settings)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_settings_returns_public_fields() -> None:
    override_db(make_settings())

    response = client.get("/api/v1/settings")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["site_title"] == "Saurabh Patil - AI & Software Engineer"
    assert data["tagline"] == "AI Systems, Built With Intent"
    assert "id" not in data


def test_public_settings_returns_404_when_missing() -> None:
    override_db(None)

    response = client.get("/api/v1/settings")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_admin_settings_requires_token() -> None:
    override_db(make_settings())

    response = client.get("/api/v1/admin/settings")

    assert response.status_code == 401


def test_admin_settings_returns_id() -> None:
    settings = make_settings()
    override_db(settings)

    response = client.get("/api/v1/admin/settings", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["data"]["id"] == str(settings.id)


def test_admin_update_settings_persists_fields() -> None:
    session = override_db(make_settings())

    response = client.patch(
        "/api/v1/admin/settings",
        headers=auth_headers(),
        json={
            "site_title": "Updated title",
            "tagline": "Updated tagline",
            "og_image_url": "https://example.com/og.png",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["site_title"] == "Updated title"
    assert data["tagline"] == "Updated tagline"
    assert data["og_image_url"] == "https://example.com/og.png"
    assert session.commits == 1


def test_admin_update_settings_can_clear_optional_field() -> None:
    session = override_db(make_settings())

    response = client.patch(
        "/api/v1/admin/settings",
        headers=auth_headers(),
        json={"tagline": None},
    )

    assert response.status_code == 200
    assert response.json()["data"]["tagline"] is None
    assert session.commits == 1


def test_admin_update_settings_rejects_null_site_title() -> None:
    override_db(make_settings())

    response = client.patch(
        "/api/v1/admin/settings",
        headers=auth_headers(),
        json={"site_title": None},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_admin_update_settings_empty_body_is_noop() -> None:
    session = override_db(make_settings())

    response = client.patch(
        "/api/v1/admin/settings",
        headers=auth_headers(),
        json={},
    )

    assert response.status_code == 200
    assert response.json()["data"]["site_title"] == "Saurabh Patil - AI & Software Engineer"
    assert session.commits == 0


def test_admin_update_settings_returns_404_when_missing() -> None:
    override_db(None)

    response = client.patch(
        "/api/v1/admin/settings",
        headers=auth_headers(),
        json={"tagline": "New"},
    )

    assert response.status_code == 404
