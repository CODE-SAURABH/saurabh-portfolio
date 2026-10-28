from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.api.v1.admin.deps import AdminGuard
from app.db.deps import DatabaseSession
from app.models.project import Project, ProjectSection, ProjectTechnology
from app.repositories.project import (
    get_admin_project,
    get_project_by_slug,
    list_admin_projects,
)
from app.schemas.common import DataResponse
from app.schemas.project import (
    ProjectAdminListItem,
    ProjectAdminRead,
    ProjectCreate,
    ProjectFlagUpdate,
    ProjectReorder,
    ProjectSectionAdminRead,
    ProjectSectionCreate,
    ProjectSectionUpdate,
    ProjectTechnologyAdminRead,
    ProjectTechnologyCreate,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["admin-projects"])


def _not_found(message: str = "Project not found") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message,
    )


def _conflict(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def _apply_fields(target: Any, data: dict[str, Any]) -> None:
    for field_name, value in data.items():
        setattr(target, field_name, value)


def _admin_read(project: Project) -> ProjectAdminRead:
    return ProjectAdminRead.model_validate(project)


def _admin_list_item(project: Project) -> ProjectAdminListItem:
    return ProjectAdminListItem.model_validate(project)


@router.get("", response_model=DataResponse[list[ProjectAdminListItem]])
async def list_projects(
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[ProjectAdminListItem]]:
    projects = list_admin_projects(db)
    return DataResponse(data=[_admin_list_item(project) for project in projects])


@router.post(
    "",
    response_model=DataResponse[ProjectAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    payload: ProjectCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectAdminRead]:
    if get_project_by_slug(db, payload.slug) is not None:
        raise _conflict("A project with this slug already exists")

    project = Project(**payload.model_dump())
    db.add(project)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise _conflict("A project with this slug already exists") from error
    db.refresh(project)
    return DataResponse(data=_admin_read(project))


@router.patch("/reorder", response_model=DataResponse[list[ProjectAdminListItem]])
async def reorder_projects(
    payload: ProjectReorder,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[list[ProjectAdminListItem]]:
    projects = {project.id: project for project in list_admin_projects(db)}
    missing = [item.id for item in payload.items if item.id not in projects]
    if missing:
        raise _not_found()

    for item in payload.items:
        projects[item.id].display_order = item.display_order

    db.commit()
    return DataResponse(
        data=[_admin_list_item(project) for project in list_admin_projects(db)]
    )


@router.get("/{project_id}", response_model=DataResponse[ProjectAdminRead])
async def read_project(
    project_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()
    return DataResponse(data=_admin_read(project))


@router.patch("/{project_id}", response_model=DataResponse[ProjectAdminRead])
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    data = payload.model_dump(exclude_unset=True)
    next_slug = data.get("slug")
    if next_slug is not None and next_slug != project.slug:
        existing = get_project_by_slug(db, next_slug)
        if existing is not None and existing.id != project.id:
            raise _conflict("A project with this slug already exists")

    _apply_fields(project, data)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise _conflict("A project with this slug already exists") from error
    db.refresh(project)
    return DataResponse(data=_admin_read(project))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{project_id}/publish", response_model=DataResponse[ProjectAdminRead])
async def set_project_published(
    project_id: UUID,
    payload: ProjectFlagUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    project.is_published = payload.value
    db.commit()
    db.refresh(project)
    return DataResponse(data=_admin_read(project))


@router.patch("/{project_id}/feature", response_model=DataResponse[ProjectAdminRead])
async def set_project_featured(
    project_id: UUID,
    payload: ProjectFlagUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    project.is_featured = payload.value
    db.commit()
    db.refresh(project)
    return DataResponse(data=_admin_read(project))


def _find_section(project: Project, section_id: UUID) -> ProjectSection | None:
    return next(
        (section for section in project.sections if section.id == section_id),
        None,
    )


@router.post(
    "/{project_id}/sections",
    response_model=DataResponse[ProjectSectionAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_project_section(
    project_id: UUID,
    payload: ProjectSectionCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectSectionAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    section = ProjectSection(project_id=project.id, **payload.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return DataResponse(data=ProjectSectionAdminRead.model_validate(section))


@router.patch(
    "/{project_id}/sections/{section_id}",
    response_model=DataResponse[ProjectSectionAdminRead],
)
async def update_project_section(
    project_id: UUID,
    section_id: UUID,
    payload: ProjectSectionUpdate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectSectionAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    section = _find_section(project, section_id)
    if section is None:
        raise _not_found("Project section not found")

    _apply_fields(section, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(section)
    return DataResponse(data=ProjectSectionAdminRead.model_validate(section))


@router.delete(
    "/{project_id}/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project_section(
    project_id: UUID,
    section_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    section = _find_section(project, section_id)
    if section is None:
        raise _not_found("Project section not found")

    db.delete(section)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{project_id}/technologies",
    response_model=DataResponse[ProjectTechnologyAdminRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_project_technology(
    project_id: UUID,
    payload: ProjectTechnologyCreate,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> DataResponse[ProjectTechnologyAdminRead]:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    name = payload.name.strip()
    if any(
        technology.name.casefold() == name.casefold()
        for technology in project.technologies
    ):
        raise _conflict("This technology is already attached to the project")

    technology = ProjectTechnology(
        project_id=project.id,
        name=name,
        display_order=payload.display_order,
    )
    db.add(technology)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise _conflict("This technology is already attached to the project") from error
    db.refresh(technology)
    return DataResponse(data=ProjectTechnologyAdminRead.model_validate(technology))


@router.delete(
    "/{project_id}/technologies/{technology_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project_technology(
    project_id: UUID,
    technology_id: UUID,
    _admin: AdminGuard,
    db: DatabaseSession,
) -> Response:
    project = get_admin_project(db, project_id)
    if project is None:
        raise _not_found()

    technology = next(
        (
            item
            for item in project.technologies
            if item.id == technology_id
        ),
        None,
    )
    if technology is None:
        raise _not_found("Project technology not found")

    db.delete(technology)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
