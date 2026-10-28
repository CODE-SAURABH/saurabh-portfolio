import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "project"
    __table_args__ = (
        Index("ix_project_is_featured_is_published", "is_featured", "is_published"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(400))
    long_description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    visual_type: Mapped[str | None] = mapped_column(String(50))
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        index=True,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        index=True,
        nullable=False,
    )
    github_url: Mapped[str | None] = mapped_column(String(500))
    live_url: Mapped[str | None] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    technologies: Mapped[list["ProjectTechnology"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectTechnology.display_order",
    )
    sections: Mapped[list["ProjectSection"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectSection.display_order",
    )


class ProjectTechnology(Base):
    __tablename__ = "project_technology"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            name="uq_project_technology_project_id_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        index=True,
        nullable=False,
    )
    project: Mapped[Project] = relationship(back_populates="technologies")


class ProjectSection(Base):
    __tablename__ = "project_section"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    overline: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        index=True,
        nullable=False,
    )
    project: Mapped[Project] = relationship(back_populates="sections")
