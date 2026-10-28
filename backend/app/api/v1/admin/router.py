from fastapi import APIRouter

from app.api.v1.admin import (
    auth,
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

admin_router = APIRouter()
admin_router.include_router(auth.router)
admin_router.include_router(profile.router)
admin_router.include_router(experience.router)
admin_router.include_router(education.router)
admin_router.include_router(skills.router)
admin_router.include_router(projects.router)
admin_router.include_router(notes.router)
admin_router.include_router(contact.router)
admin_router.include_router(settings.router)
admin_router.include_router(resume.router)
