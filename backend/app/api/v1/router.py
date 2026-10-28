from fastapi import APIRouter

from app.api import health
from app.api.v1 import (
    contact,
    education,
    experience,
    notes,
    profile,
    projects,
    resume,
    settings,
    skills,
)
from app.api.v1.admin.router import admin_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(profile.router)
api_router.include_router(experience.router)
api_router.include_router(education.router)
api_router.include_router(skills.router)
api_router.include_router(projects.router)
api_router.include_router(notes.router)
api_router.include_router(contact.router)
api_router.include_router(settings.router)
api_router.include_router(resume.router)
api_router.include_router(admin_router, prefix="/admin")
