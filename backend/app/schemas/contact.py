from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    subject: str | None = Field(default=None, max_length=300)
    message: str = Field(min_length=10, max_length=5000)


class ContactAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    subject: str | None
    message: str
    submitted_at: datetime
    is_read: bool
    notified_at: datetime | None


class ContactReadUpdate(BaseModel):
    value: bool = True
