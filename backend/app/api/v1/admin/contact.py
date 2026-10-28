from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.admin.deps import require_admin
from app.db.deps import DatabaseSession
from app.repositories.contact import (
    delete_contact_submission,
    get_contact_submission,
    list_contact_submissions,
    mark_contact_read,
)
from app.schemas.common import DataResponse, MessageData
from app.schemas.contact import ContactAdminRead, ContactReadUpdate

router = APIRouter(
    prefix="/contact-inbox",
    tags=["admin-contact"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=DataResponse[list[ContactAdminRead]])
async def admin_list_contacts(db: DatabaseSession) -> DataResponse[list[ContactAdminRead]]:
    submissions = list_contact_submissions(db)
    return DataResponse(data=[ContactAdminRead.model_validate(s) for s in submissions])


@router.patch("/{submission_id}/read", response_model=DataResponse[ContactAdminRead])
async def admin_mark_contact_read(
    submission_id: UUID,
    body: ContactReadUpdate,
    db: DatabaseSession,
) -> DataResponse[ContactAdminRead]:
    submission = get_contact_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    updated = mark_contact_read(db, submission, is_read=body.value)
    return DataResponse(data=ContactAdminRead.model_validate(updated))


@router.delete("/{submission_id}", response_model=DataResponse[MessageData])
async def admin_delete_contact(
    submission_id: UUID,
    db: DatabaseSession,
) -> DataResponse[MessageData]:
    submission = get_contact_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    delete_contact_submission(db, submission)
    return DataResponse(data=MessageData(message="Submission deleted"))
