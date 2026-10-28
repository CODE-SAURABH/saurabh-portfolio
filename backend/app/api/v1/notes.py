from fastapi import APIRouter, HTTPException, Query, status

from app.db.deps import DatabaseSession
from app.repositories.note import get_public_note_by_slug, list_public_notes
from app.schemas.common import CollectionResponse, DataResponse, PaginationMeta
from app.schemas.note import NotePublicRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=CollectionResponse[NotePublicRead])
async def read_notes(
    db: DatabaseSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> CollectionResponse[NotePublicRead]:
    notes, total = list_public_notes(db, limit=limit, offset=offset)
    return CollectionResponse(
        data=[NotePublicRead.model_validate(note) for note in notes],
        meta=PaginationMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/{slug}", response_model=DataResponse[NotePublicRead])
async def read_note(slug: str, db: DatabaseSession) -> DataResponse[NotePublicRead]:
    note = get_public_note_by_slug(db, slug)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return DataResponse(data=NotePublicRead.model_validate(note))
