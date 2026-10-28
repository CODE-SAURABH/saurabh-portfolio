"""Seed script - populates the database with initial content.

Run from backend directory:
    DATABASE_URL=postgresql+psycopg://... python -m scripts.seed

Idempotent: safe to run multiple times.
"""

import os
import sys
from datetime import UTC, date, datetime
from typing import Any

# Add parent dir to path so `app` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import create_db_engine, create_session, normalize_database_url
from app.models import *  # noqa: F401,F403
from app.models.admin import AdminCredential
from app.models.education import Education
from app.models.experience import Experience
from app.models.note import Note
from app.models.profile import Profile
from app.models.project import Project, ProjectSection, ProjectTechnology
from app.models.settings import SiteSettings
from app.models.skill import Skill, SkillGroup


def _exists(session: Session, model: type[Base]) -> bool:
    return session.scalar(select(model).limit(1)) is not None


def _seed_profile(session: Session) -> None:
    if _exists(session, Profile):
        return
    session.add(
        Profile(
            full_name="Saurabh Patil",
            headline="AI / Software Engineer",
            bio=(
                "Computer science graduate exploring AI-powered systems. "
                "I care about the whole loop - the data, the model, the "
                "interface, and whether the result earns a place in someone's day."
            ),
            location="Maharashtra, India",
            email="",
            github_url="https://github.com/CODE-SAURABH",
            linkedin_url="",
            availability_note="Open to opportunities",
        )
    )
    print("Profile seeded")


def _seed_settings(session: Session) -> None:
    if _exists(session, SiteSettings):
        return
    session.add(
        SiteSettings(
            site_title="Saurabh Patil - AI & Software Engineer",
            tagline="AI Systems, Built With Intent",
        )
    )
    print("Site settings seeded")


def _seed_admin(session: Session) -> None:
    if _exists(session, AdminCredential):
        return
    default_pw = os.environ.get("ADMIN_PASSWORD", "changeme123")
    session.add(AdminCredential(password_hash=hash_password(default_pw)))
    print(f"Admin credential seeded (password: {default_pw})")
    print("  CHANGE THIS IMMEDIATELY via the admin password reset script")


def _seed_education(session: Session) -> None:
    if _exists(session, Education):
        return
    entries: list[dict[str, Any]] = [
        {
            "institution": "ADCET, Ashta",
            "degree": "B.Tech",
            "field": "Computer Science & Engineering",
            "start_date": date(2020, 8, 1),
            "end_date": date(2024, 6, 1),
        },
        {
            "institution": "Cambridge Junior College",
            "degree": "HSC",
            "field": "Science",
            "start_date": date(2018, 6, 1),
            "end_date": date(2020, 3, 1),
        },
        {
            "institution": "New English School",
            "degree": "SSC",
            "field": None,
            "start_date": date(2016, 6, 1),
            "end_date": date(2018, 3, 1),
        },
    ]
    for order, entry in enumerate(entries):
        session.add(Education(**entry, display_order=order))
    print("Education seeded")


def _seed_experience(session: Session) -> None:
    if _exists(session, Experience):
        return
    session.add(
        Experience(
            company="KPIT Technologies",
            role_title="Software Engineer",
            employment_type="Full-time",
            start_date=date(2025, 1, 1),
            is_current=True,
            description=(
                "Working on software engineering projects. "
                "Details are confidential."
            ),
            display_order=0,
        )
    )
    print("Experience seeded")


def _seed_skills(session: Session) -> None:
    if _exists(session, SkillGroup):
        return
    groups: dict[str, list[str]] = {
        "Languages & Backend": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "REST APIs",
        ],
        "AI / ML / LLM": [
            "LangChain",
            "RAG",
            "Embeddings",
            "Prompt Engineering",
            "ChromaDB",
        ],
        "Frontend & Delivery": ["React", "TypeScript", "HTML/CSS", "Vite", "Git"],
        "Working Style": [
            "Systems thinking",
            "Documentation",
            "Iterative delivery",
            "Learning in public",
        ],
    }
    for order, (group_name, skills) in enumerate(groups.items()):
        group = SkillGroup(name=group_name, display_order=order)
        session.add(group)
        session.flush()
        for j, skill_name in enumerate(skills):
            session.add(
                Skill(
                    group_id=group.id,
                    name=skill_name,
                    is_featured=(j < 2),
                    display_order=j,
                )
            )
    print("Skills seeded")


def _seed_projects(session: Session) -> None:
    if _exists(session, Project):
        return
    projects_data: list[dict[str, Any]] = [
        {
            "title": "Vidnyan-Bot",
            "slug": "vidnyan-bot",
            "short_description": (
                "RAG-powered conversational assistant for educational content."
            ),
            "category": "ai",
            "visual_type": "rag",
            "is_published": True,
            "is_featured": True,
            "display_order": 0,
            "technologies": [
                "Python",
                "LangChain",
                "Embeddings",
                "Chroma",
                "FastAPI",
            ],
            "sections": [
                {
                    "overline": "01 / PROBLEM FRAMING",
                    "title": "Problem framing",
                    "body": (
                        "Students benefit from answers tuned to their syllabus, "
                        "but generic search engines return broad results. The "
                        "goal was to build a retrieval-augmented assistant that "
                        "retrieves relevant chunks from a curated knowledge base."
                    ),
                    "display_order": 0,
                },
                {
                    "overline": "02 / APPROACH",
                    "title": "Approach",
                    "body": (
                        "Documents ingested -> chunked -> embedded -> stored in "
                        "a vector database. At query time, the user's question "
                        "is embedded, k-nearest chunks retrieved, and a language "
                        "model generates a grounded answer."
                    ),
                    "display_order": 1,
                },
                {
                    "overline": "03 / SYSTEM SHAPE",
                    "title": "System shape",
                    "body": (
                        "FastAPI backend, LangChain orchestration layer, "
                        "ChromaDB for vector storage. The system is designed to "
                        "be swappable at each layer."
                    ),
                    "display_order": 2,
                },
            ],
        },
        {
            "title": "Sugarcane Leaf Disease Detection",
            "slug": "sugarcane-disease",
            "short_description": (
                "Computer vision model classifying diseases from leaf images."
            ),
            "category": "vision",
            "visual_type": "vision",
            "is_published": True,
            "is_featured": True,
            "display_order": 1,
            "technologies": [
                "Python",
                "TensorFlow",
                "CNN",
                "Image Processing",
            ],
            "sections": [
                {
                    "overline": "01 / PROBLEM FRAMING",
                    "title": "Problem framing",
                    "body": (
                        "Manual disease detection in sugarcane farms is slow and "
                        "error-prone. An image classification model can provide "
                        "quick preliminary diagnosis from a phone camera."
                    ),
                    "display_order": 0,
                },
            ],
        },
        {
            "title": "OpenSkills",
            "slug": "openskills",
            "short_description": (
                "Open-source collection of production-grade AI agent skills."
            ),
            "category": "tools",
            "visual_type": "nodes",
            "is_published": True,
            "is_featured": False,
            "display_order": 2,
            "technologies": ["Python", "AI Agents", "MCP", "Open Source"],
            "sections": [],
        },
        {
            "title": "DayEnd Journal",
            "slug": "dayend-journal",
            "short_description": (
                "Offline-first PWA for daily journaling with weekly reflection "
                "reports."
            ),
            "category": "product",
            "visual_type": "journal",
            "is_published": True,
            "is_featured": False,
            "display_order": 3,
            "technologies": ["React", "PWA", "IndexedDB", "Offline-first"],
            "sections": [],
        },
    ]

    for project_data in projects_data:
        techs: list[str] = project_data.pop("technologies", [])
        sects: list[dict[str, Any]] = project_data.pop("sections", [])
        project = Project(**project_data)
        session.add(project)
        session.flush()
        for t_order, tech_name in enumerate(techs):
            session.add(
                ProjectTechnology(
                    project_id=project.id,
                    name=tech_name,
                    display_order=t_order,
                )
            )
        for sect in sects:
            session.add(ProjectSection(project_id=project.id, **sect))
    print("Projects seeded")


def _seed_notes(session: Session) -> None:
    if _exists(session, Note):
        return
    session.add(
        Note(
            title="What actually makes RAG useful?",
            slug="what-makes-rag-useful",
            topic_label="AI SYSTEMS / 001",
            category="ai-systems",
            body=(
                "Chunking strategy matters more than model choice. Retrieval "
                "quality determines answer quality. The interface must "
                "communicate confidence honestly."
            ),
            is_published=True,
            published_at=datetime.now(UTC),
        )
    )
    print("Notes seeded")


def seed() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    engine = create_db_engine(normalize_database_url(database_url))
    session = create_session(engine)

    try:
        _seed_profile(session)
        _seed_settings(session)
        _seed_admin(session)
        _seed_education(session)
        _seed_experience(session)
        _seed_skills(session)
        _seed_projects(session)
        _seed_notes(session)
        session.commit()
        print("\nSeed complete")

    except Exception as exc:
        session.rollback()
        print(f"\nSeed failed: {exc}")
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    seed()
