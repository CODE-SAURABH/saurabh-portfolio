import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.contact import ContactSubmission

client = TestClient(app)


def make_submission(**overrides: object) -> ContactSubmission:
    values: dict[str, object] = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "subject": "Hello",
        "message": "I would like to talk about a project.",
        "ip_hash": "a" * 64,
        "is_read": False,
        "notified_at": None,
    }
    values.update(overrides)
    submission = ContactSubmission(**values)
    submission.id = uuid.uuid4()
    if getattr(submission, "submitted_at", None) is None:
        submission.submitted_at = datetime(2026, 10, 1, tzinfo=UTC)
    return submission


class FakeScalars:
    def __init__(self, items: list[ContactSubmission]) -> None:
        self.items = items

    def all(self) -> list[ContactSubmission]:
        return self.items


class FakeContactSession:
    def __init__(
        self,
        submissions: list[ContactSubmission],
        *,
        recent_count: int = 0,
    ) -> None:
        self.submissions = list(submissions)
        self.recent_count = recent_count
        self.added: object | None = None
        self.deleted: object | None = None
        self.commits = 0

    def scalar(self, statement: object) -> int:
        if "count" in str(statement).lower():
            return self.recent_count
        return 0

    def scalars(self, statement: object) -> FakeScalars:
        ordered = sorted(
            self.submissions,
            key=lambda submission: submission.submitted_at,
            reverse=True,
        )
        return FakeScalars(ordered)

    def get(
        self,
        model: object,
        submission_id: uuid.UUID,
    ) -> ContactSubmission | None:
        return next(
            (
                submission
                for submission in self.submissions
                if submission.id == submission_id
            ),
            None,
        )

    def add(self, item: object) -> None:
        if isinstance(item, ContactSubmission):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "submitted_at", None) is None:
                item.submitted_at = datetime.now(UTC)
            self.submissions.append(item)
        self.added = item

    def delete(self, item: object) -> None:
        if isinstance(item, ContactSubmission):
            self.submissions.remove(item)
        self.deleted = item

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        pass

    def refresh(self, item: ContactSubmission) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid.uuid4()
        if getattr(item, "submitted_at", None) is None:
            item.submitted_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(
    submissions: list[ContactSubmission],
    *,
    recent_count: int = 0,
) -> FakeContactSession:
    session = FakeContactSession(submissions, recent_count=recent_count)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def valid_payload() -> dict[str, str]:
    return {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "subject": "Hello",
        "message": "I would like to talk about a project.",
    }


def test_submit_contact_stores_submission(monkeypatch: pytest.MonkeyPatch) -> None:
    async def no_notification(submission: ContactSubmission) -> bool:
        return False

    monkeypatch.setattr(
        "app.services.notify.send_contact_notification",
        no_notification,
    )
    session = override_db([])

    response = client.post("/api/v1/contact", json=valid_payload())

    assert response.status_code == 201
    assert "received" in response.json()["data"]["message"]
    assert isinstance(session.added, ContactSubmission)
    assert session.added.name == "Ada Lovelace"
    assert session.added.notified_at is None
    assert session.commits == 1


def test_submit_contact_marks_notified_when_telegram_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def notification_succeeds(submission: ContactSubmission) -> bool:
        return True

    monkeypatch.setattr(
        "app.services.notify.send_contact_notification",
        notification_succeeds,
    )
    session = override_db([])

    response = client.post("/api/v1/contact", json=valid_payload())

    assert response.status_code == 201
    assert isinstance(session.added, ContactSubmission)
    assert session.added.notified_at is not None
    assert session.commits == 2


def test_submit_contact_ignores_notification_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def notification_raises(submission: ContactSubmission) -> bool:
        raise RuntimeError("telegram down")

    monkeypatch.setattr(
        "app.services.notify.send_contact_notification",
        notification_raises,
    )
    session = override_db([])

    response = client.post("/api/v1/contact", json=valid_payload())

    assert response.status_code == 201
    assert isinstance(session.added, ContactSubmission)
    assert session.added.notified_at is None


def test_submit_contact_rejects_invalid_payload() -> None:
    override_db([])

    response = client.post(
        "/api/v1/contact",
        json={
            "name": "Ada",
            "email": "not-an-email",
            "message": "short",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_submit_contact_rate_limits_by_ip() -> None:
    override_db([], recent_count=5)

    response = client.post("/api/v1/contact", json=valid_payload())

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMITED"


def test_admin_contact_inbox_requires_token() -> None:
    override_db([make_submission()])

    response = client.get("/api/v1/admin/contact-inbox")

    assert response.status_code == 401


def test_admin_contact_inbox_lists_newest_first() -> None:
    older = make_submission()
    newer = make_submission(
        email="grace@example.com",
        submitted_at=datetime(2026, 10, 2, tzinfo=UTC),
    )
    override_db([older, newer])

    response = client.get(
        "/api/v1/admin/contact-inbox",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert [item["email"] for item in data] == [
        "grace@example.com",
        "ada@example.com",
    ]


def test_admin_mark_contact_read() -> None:
    submission = make_submission()
    session = override_db([submission])

    response = client.patch(
        f"/api/v1/admin/contact-inbox/{submission.id}/read",
        headers=auth_headers(),
        json={"value": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["is_read"] is True
    assert submission.is_read is True
    assert session.commits == 1


def test_admin_mark_contact_read_returns_404_when_missing() -> None:
    override_db([])

    response = client.patch(
        f"/api/v1/admin/contact-inbox/{uuid.uuid4()}/read",
        headers=auth_headers(),
        json={"value": True},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_admin_delete_contact_submission() -> None:
    submission = make_submission()
    session = override_db([submission])

    response = client.delete(
        f"/api/v1/admin/contact-inbox/{submission.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert session.deleted is submission
    assert session.commits == 1
