import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.settings import SiteSettings
from app.services.storage import StorageUnavailableError

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


def test_admin_resume_requires_token() -> None:
    override_db(make_settings())

    response = client.get("/api/v1/admin/resume")

    assert response.status_code == 401


def test_admin_resume_returns_current_url() -> None:
    override_db(
        make_settings(resume_download_url="https://cdn.example.com/resume.pdf")
    )

    response = client.get("/api/v1/admin/resume", headers=auth_headers())

    assert response.status_code == 200
    assert (
        response.json()["data"]["resume_download_url"]
        == "https://cdn.example.com/resume.pdf"
    )


def test_admin_resume_returns_404_when_not_uploaded() -> None:
    override_db(make_settings())

    response = client.get("/api/v1/admin/resume", headers=auth_headers())

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_upload_resume_rejects_non_pdf() -> None:
    override_db(make_settings())

    response = client.post(
        "/api/v1/admin/resume/upload",
        headers=auth_headers(),
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_upload_resume_rejects_empty_file() -> None:
    override_db(make_settings())

    response = client.post(
        "/api/v1/admin/resume/upload",
        headers=auth_headers(),
        files={"file": ("resume.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 422


def test_upload_resume_rejects_oversized_file() -> None:
    override_db(make_settings())

    response = client.post(
        "/api/v1/admin/resume/upload",
        headers=auth_headers(),
        files={
            "file": (
                "resume.pdf",
                b"x" * (5 * 1024 * 1024 + 1),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422


def test_upload_resume_returns_404_without_settings() -> None:
    override_db(None)

    response = client.post(
        "/api/v1/admin/resume/upload",
        headers=auth_headers(),
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 404


def test_upload_resume_returns_503_when_storage_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unavailable(data: bytes) -> str:
        raise StorageUnavailableError("RESUME_BUCKET binding is not available")

    monkeypatch.setattr(
        "app.api.v1.admin.resume.upload_resume_pdf",
        unavailable,
    )
    override_db(make_settings())

    response = client.post(
        "/api/v1/admin/resume/upload",
        headers=auth_headers(),
        files={"file": ("resume.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 503


def test_upload_resume_updates_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploaded: dict[str, object] = {}

    async def store(data: bytes) -> str:
        uploaded["size"] = len(data)
        return "https://cdn.example.com/resume/resume.pdf?v=123"

    monkeypatch.setattr(
        "app.api.v1.admin.resume.upload_resume_pdf",
        store,
    )
    settings = make_settings()
    session = override_db(settings)

    response = client.post(
        "/api/v1/admin/resume/upload",
        headers=auth_headers(),
        files={"file": ("resume.pdf", b"%PDF-1.4 resume", "application/pdf")},
    )

    assert response.status_code == 201
    assert (
        response.json()["data"]["resume_download_url"]
        == "https://cdn.example.com/resume/resume.pdf?v=123"
    )
    assert settings.resume_download_url == (
        "https://cdn.example.com/resume/resume.pdf?v=123"
    )
    assert uploaded["size"] == len(b"%PDF-1.4 resume")
    assert session.commits == 1
