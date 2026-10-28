from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    resume_download_url: str


class ResumeUrlUpdate(BaseModel):
    resume_download_url: str = Field(min_length=1, max_length=500)
