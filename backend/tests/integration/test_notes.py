import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.note import Note

client = TestClient(app)


def make_note(**overrides: object) -> Note:
    values: dict[str, object] = {
        "title": "What actually makes RAG useful?",
        "slug": "what-makes-rag-useful",
        "topic_label": "AI SYSTEMS / 001",
        "category": "ai-systems",
        "body": "Chunking, retrieval, and evaluation.",
        "is_published": True,
        "published_at": datetime(2026, 10, 1, tzinfo=UTC),
    }
    values.update(overrides)
    note = Note(**values)
    note.id = uuid.uuid4()
    note.created_at = datetime(2026, 10, 1, tzinfo=UTC)
    note.updated_at = datetime(2026, 10, 1, tzinfo=UTC)
    return note


class FakeScalars:
    def __init__(self, items: list[Note]) -> None:
        self.items = items

    def all(self) -> list[Note]:
        return self.items


class FakeNoteSession:
    def __init__(
        self,
        notes: list[Note],
        *,
        scalar_value: Note | None = None,
    ) -> None:
        self.notes = list(notes)
        self.scalar_value = scalar_value
        self.added: object | None = None
        self.deleted: object | None = None
        self.committed = False
        self.rolled_back = False

    def scalar(self, statement: object) -> Note | int | None:
        if "count" in str(statement).lower():
            return len(self.notes)
        return self.scalar_value

    def scalars(self, statement: object) -> FakeScalars:
        ordered = sorted(
            self.notes,
            key=lambda note: (
                note.published_at or datetime.min.replace(tzinfo=UTC),
                note.created_at,
            ),
            reverse=True,
        )
        return FakeScalars(ordered)

    def get(self, model: object, note_id: uuid.UUID) -> Note | None:
        return next((note for note in self.notes if note.id == note_id), None)

    def add(self, item: object) -> None:
        if isinstance(item, Note):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "created_at", None) is None:
                item.created_at = datetime.now(UTC)
            if getattr(item, "updated_at", None) is None:
                item.updated_at = datetime.now(UTC)
            self.notes.append(item)
        self.added = item

    def delete(self, item: object) -> None:
        if isinstance(item, Note):
            self.notes.remove(item)
        self.deleted = item

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def refresh(self, item: Note) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid.uuid4()
        if getattr(item, "created_at", None) is None:
            item.created_at = datetime.now(UTC)
        if getattr(item, "updated_at", None) is None:
            item.updated_at = datetime.now(UTC)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(
    notes: list[Note],
    *,
    scalar_value: Note | None = None,
) -> FakeNoteSession:
    session = FakeNoteSession(notes, scalar_value=scalar_value)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_notes_returns_collection_with_meta() -> None:
    note = make_note()
    override_db([note])

    response = client.get("/api/v1/notes")

    assert response.status_code == 200
    body = response.json()
    assert body["meta"] == {"total": 1, "offset": 0, "limit": 20}
    assert body["data"][0]["slug"] == "what-makes-rag-useful"
    assert body["data"][0]["topic_label"] == "AI SYSTEMS / 001"


def test_public_notes_validates_pagination() -> None:
    override_db([])

    response = client.get("/api/v1/notes?limit=101")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_public_note_detail_returns_note() -> None:
    note = make_note()
    override_db([note], scalar_value=note)

    response = client.get("/api/v1/notes/what-makes-rag-useful")

    assert response.status_code == 200
    assert response.json()["data"]["body"] == "Chunking, retrieval, and evaluation."


def test_public_note_detail_returns_404_when_missing() -> None:
    override_db([], scalar_value=None)

    response = client.get("/api/v1/notes/missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_admin_notes_requires_token() -> None:
    override_db([make_note()])

    response = client.get("/api/v1/admin/notes")

    assert response.status_code == 401


def test_admin_notes_lists_drafts() -> None:
    draft = make_note(slug="draft-note", is_published=False, published_at=None)
    override_db([draft])

    response = client.get("/api/v1/admin/notes", headers=auth_headers())

    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["is_published"] is False
    assert data[0]["published_at"] is None


def test_create_draft_note_returns_created_note() -> None:
    session = override_db([])

    response = client.post(
        "/api/v1/admin/notes",
        headers=auth_headers(),
        json={
            "title": "New note",
            "slug": "new-note",
            "topic_label": "TOOLS / 002",
            "category": "tools",
            "body": "A draft.",
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["slug"] == "new-note"
    assert data["is_published"] is False
    assert data["published_at"] is None
    assert session.added is not None
    assert session.committed


def test_create_published_note_sets_published_at() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/notes",
        headers=auth_headers(),
        json={
            "title": "Published note",
            "slug": "published-note",
            "is_published": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["published_at"] is not None


def test_create_note_rejects_duplicate_slug() -> None:
    existing = make_note()
    override_db([existing], scalar_value=existing)

    response = client.post(
        "/api/v1/admin/notes",
        headers=auth_headers(),
        json={
            "title": "Duplicate",
            "slug": "what-makes-rag-useful",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_create_note_validates_slug() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/notes",
        headers=auth_headers(),
        json={
            "title": "Invalid",
            "slug": "Not A Slug",
        },
    )

    assert response.status_code == 422


def test_patch_note_updates_fields() -> None:
    note = make_note(is_published=False, published_at=None)
    session = override_db([note])

    response = client.patch(
        f"/api/v1/admin/notes/{note.id}",
        headers=auth_headers(),
        json={"title": "Updated title", "is_published": True},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Updated title"
    assert data["is_published"] is True
    assert data["published_at"] is not None
    assert session.committed


def test_patch_note_rejects_null_required_field() -> None:
    note = make_note()
    override_db([note])

    response = client.patch(
        f"/api/v1/admin/notes/{note.id}",
        headers=auth_headers(),
        json={"title": None},
    )

    assert response.status_code == 422


def test_publish_toggle_sets_and_clears_flag() -> None:
    note = make_note(is_published=False, published_at=None)
    session = override_db([note])

    published = client.patch(
        f"/api/v1/admin/notes/{note.id}/publish",
        headers=auth_headers(),
        json={"value": True},
    )
    unpublished = client.patch(
        f"/api/v1/admin/notes/{note.id}/publish",
        headers=auth_headers(),
        json={"value": False},
    )

    assert published.status_code == 200
    assert published.json()["data"]["is_published"] is True
    assert published.json()["data"]["published_at"] is not None
    assert unpublished.status_code == 200
    assert unpublished.json()["data"]["is_published"] is False
    assert session.committed


def test_delete_note_removes_note() -> None:
    note = make_note()
    session = override_db([note])

    response = client.delete(
        f"/api/v1/admin/notes/{note.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert session.deleted is note
    assert session.committed
