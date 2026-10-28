from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.api.v1.admin.deps import AdminGuard
from app.db.deps import DatabaseSession
from app.models.note import Note
from app.repositories.note import get_note, get_note_by_slug, list_admin_notes
from app.schemas.common import DataResponse
from app.schemas.note import (
    NoteAdminRead,
    NoteCreate,
    NotePublishUpdate,
    NoteUpdate,
)

router = APIRouter(prefix="/notes", tags=["admin-notes"])


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Note not found",
    )


def _conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="A note with this slug already exists",
    )


def _apply_fields(note: Note, data: dict[str, Any]) -> None:
    for field_name, value in data.items():
        setattr(note, field_name, value)


def _admin_read(note: Note) -> NoteAdminRead:
    return NoteAdminRead.model_validate(note)


def _publish(note: Note) -> None:
    note.is_published = True
    if note.published_at is None:
        note.published_at = datetime.now(UTC)


@router.get("", response_model=DataResponse[list[NoteAdminRead]])
async def list_notes(
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[NoteAdminRead]]:
    notes = list_admin_notes(db)
    return DataResponse(data=[_admin_read(note) for note in notes])


@router.post(
    "",
    response_model=DataResponse[NoteAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    payload: NoteCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[NoteAdminRead]:
    if get_note_by_slug(db, payload.slug) is not None:
        raise _conflict()

    data = payload.model_dump()
    if data["is_published"] and data["published_at"] is None:
        data["published_at"] = datetime.now(UTC)

    note = Note(**data)
    db.add(note)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise _conflict() from error
    db.refresh(note)
    return DataResponse(data=_admin_read(note))


@router.get("/{note_id}", response_model=DataResponse[NoteAdminRead])
async def read_note(
    note_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[NoteAdminRead]:
    note = get_note(db, note_id)
    if note is None:
        raise _not_found()
    return DataResponse(data=_admin_read(note))


@router.patch("/{note_id}", response_model=DataResponse[NoteAdminRead])
async def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[NoteAdminRead]:
    note = get_note(db, note_id)
    if note is None:
        raise _not_found()

    data = payload.model_dump(exclude_unset=True)
    next_slug = data.get("slug")
    if next_slug is not None and next_slug != note.slug:
        existing = get_note_by_slug(db, next_slug)
        if existing is not None and existing.id != note.id:
            raise _conflict()

    _apply_fields(note, data)
    if note.is_published and note.published_at is None:
        note.published_at = datetime.now(UTC)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise _conflict() from error
    db.refresh(note)
    return DataResponse(data=_admin_read(note))


@router.patch("/{note_id}/publish", response_model=DataResponse[NoteAdminRead])
async def set_note_published(
    note_id: UUID,
    payload: NotePublishUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[NoteAdminRead]:
    note = get_note(db, note_id)
    if note is None:
        raise _not_found()

    if payload.value:
        _publish(note)
    else:
        note.is_published = False

    db.commit()
    db.refresh(note)
    return DataResponse(data=_admin_read(note))


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    note = get_note(db, note_id)
    if note is None:
        raise _not_found()

    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
