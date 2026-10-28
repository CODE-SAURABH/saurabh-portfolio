from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.db.deps import DatabaseSession
from app.repositories.project import get_public_project_by_slug, list_public_projects
from app.schemas.common import CollectionResponse, DataResponse, PaginationMeta
from app.schemas.project import (
    ProjectCategory,
    ProjectPublicDetail,
    ProjectPublicListItem,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=CollectionResponse[ProjectPublicListItem])
async def read_projects(
    db: DatabaseSession,
    featured: Annotated[bool | None, Query()] = None,
    category: Annotated[ProjectCategory | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CollectionResponse[ProjectPublicListItem]:
    projects, total = list_public_projects(
        db,
        featured=featured,
        category=category,
        limit=limit,
        offset=offset,
    )
    return CollectionResponse(
        data=[ProjectPublicListItem.model_validate(project) for project in projects],
        meta=PaginationMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/{slug}", response_model=DataResponse[ProjectPublicDetail])
async def read_project(
    slug: str,
    db: DatabaseSession,
) -> DataResponse[ProjectPublicDetail]:
    project = get_public_project_by_slug(db, slug)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return DataResponse(data=ProjectPublicDetail.model_validate(project))
