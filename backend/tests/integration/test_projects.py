import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.deps import get_db
from app.main import app
from app.models.project import Project, ProjectSection, ProjectTechnology

client = TestClient(app)


def make_project(
    *,
    technologies: list[str] | None = None,
    sections: list[dict[str, object]] | None = None,
    **overrides: object,
) -> Project:
    values: dict[str, object] = {
        "title": "Vidnyan-Bot",
        "slug": "vidnyan-bot",
        "short_description": "A retrieval-augmented science assistant.",
        "long_description": "Long-form case study.",
        "status": "Completed",
        "category": "ai",
        "visual_type": "rag",
        "is_published": True,
        "is_featured": True,
        "display_order": 0,
        "github_url": "https://github.com/example/vidnyan-bot",
        "live_url": None,
        "thumbnail_url": None,
    }
    values.update(overrides)
    project = Project(**values)
    project.id = uuid.uuid4()
    project.created_at = datetime.now(UTC)
    project.updated_at = datetime.now(UTC)
    project.technologies = [
        ProjectTechnology(
            id=uuid.uuid4(),
            project_id=project.id,
            name=name,
            display_order=index,
        )
        for index, name in enumerate(technologies or [])
    ]
    project.sections = []
    for index, section in enumerate(sections or []):
        raw_order = section.get("display_order", index)
        display_order = int(raw_order) if isinstance(raw_order, (int, str)) else index
        project.sections.append(
            ProjectSection(
                id=uuid.uuid4(),
                project_id=project.id,
                overline=section.get("overline"),
                title=str(section.get("title", "Section")),
                body=section.get("body"),
                display_order=display_order,
            )
        )
    return project


class FakeScalars:
    def __init__(self, items: list[Project]) -> None:
        self.items = items

    def all(self) -> list[Project]:
        return self.items


class FakeProjectSession:
    def __init__(
        self,
        projects: list[Project],
        *,
        scalar_value: Project | None = None,
    ) -> None:
        self.projects = list(projects)
        self.scalar_value = scalar_value
        self.added: object | None = None
        self.deleted: object | None = None
        self.committed = False
        self.rolled_back = False

    def scalar(self, statement: object) -> Project | int | None:
        if "count" in str(statement).lower():
            return len(self.projects)
        return self.scalar_value

    def scalars(self, statement: object) -> FakeScalars:
        ordered = sorted(
            self.projects,
            key=lambda project: (
                project.display_order,
                project.created_at,
            ),
        )
        return FakeScalars(ordered)

    def get(self, model: object, project_id: uuid.UUID) -> Project | None:
        for project in self.projects:
            if project.id == project_id:
                return project
        return None

    def add(self, item: object) -> None:
        if isinstance(item, Project):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "created_at", None) is None:
                item.created_at = datetime.now(UTC)
            if getattr(item, "updated_at", None) is None:
                item.updated_at = datetime.now(UTC)
            item.technologies = []
            item.sections = []
            self.projects.append(item)
        elif isinstance(item, ProjectSection):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            project = self._find_project(item.project_id)
            if project is not None:
                project.sections.append(item)
        elif isinstance(item, ProjectTechnology):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            project = self._find_project(item.project_id)
            if project is not None:
                project.technologies.append(item)
        self.added = item

    def delete(self, item: object) -> None:
        if isinstance(item, Project):
            self.projects.remove(item)
        elif isinstance(item, ProjectSection):
            project = self._find_project(item.project_id)
            if project is not None and item in project.sections:
                project.sections.remove(item)
        elif isinstance(item, ProjectTechnology):
            project = self._find_project(item.project_id)
            if project is not None and item in project.technologies:
                project.technologies.remove(item)
        self.deleted = item

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def refresh(self, item: Project | ProjectSection | ProjectTechnology) -> None:
        if isinstance(item, Project):
            if getattr(item, "id", None) is None:
                item.id = uuid.uuid4()
            if getattr(item, "created_at", None) is None:
                item.created_at = datetime.now(UTC)
            if getattr(item, "updated_at", None) is None:
                item.updated_at = datetime.now(UTC)
        elif getattr(item, "id", None) is None:
            item.id = uuid.uuid4()

    def _find_project(self, project_id: uuid.UUID) -> Project | None:
        return next(
            (project for project in self.projects if project.id == project_id),
            None,
        )


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(
    projects: list[Project],
    *,
    scalar_value: Project | None = None,
) -> FakeProjectSession:
    session = FakeProjectSession(projects, scalar_value=scalar_value)
    app.dependency_overrides[get_db] = lambda: session
    return session


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token()}"}


def test_public_projects_returns_collection_with_meta() -> None:
    project = make_project(technologies=["LangChain", "Chroma"])
    override_db([project])

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    body = response.json()
    assert body["meta"] == {"total": 1, "offset": 0, "limit": 20}
    assert body["data"][0]["slug"] == "vidnyan-bot"
    assert body["data"][0]["technologies"] == [{"name": "LangChain"}, {"name": "Chroma"}]


def test_public_projects_validates_pagination() -> None:
    override_db([])

    response = client.get("/api/v1/projects?limit=101")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_public_project_detail_returns_sections_and_technologies() -> None:
    project = make_project(
        technologies=["LangChain"],
        sections=[
            {
                "overline": "01 / Problem",
                "title": "Problem framing",
                "body": "Students need better answers.",
            }
        ],
    )
    override_db([project], scalar_value=project)

    response = client.get("/api/v1/projects/vidnyan-bot")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["long_description"] == "Long-form case study."
    assert data["sections"][0]["title"] == "Problem framing"
    assert data["technologies"] == [{"name": "LangChain"}]


def test_public_project_detail_returns_404_when_missing() -> None:
    override_db([], scalar_value=None)

    response = client.get("/api/v1/projects/missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_admin_projects_requires_token() -> None:
    override_db([make_project()])

    response = client.get("/api/v1/admin/projects")

    assert response.status_code == 401


def test_admin_projects_lists_drafts() -> None:
    draft = make_project(slug="draft-project", is_published=False)
    override_db([draft])

    response = client.get("/api/v1/admin/projects", headers=auth_headers())

    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["is_published"] is False
    assert "sections" not in data[0]


def test_create_project_returns_created_project() -> None:
    session = override_db([])

    response = client.post(
        "/api/v1/admin/projects",
        headers=auth_headers(),
        json={
            "title": "New Project",
            "slug": "new-project",
            "short_description": "A new project.",
            "category": "tools",
            "visual_type": "nodes",
            "is_published": True,
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["slug"] == "new-project"
    assert data["technologies"] == []
    assert data["sections"] == []
    assert session.added is not None
    assert session.committed


def test_create_project_rejects_duplicate_slug() -> None:
    existing = make_project()
    override_db([existing], scalar_value=existing)

    response = client.post(
        "/api/v1/admin/projects",
        headers=auth_headers(),
        json={
            "title": "Duplicate",
            "slug": "vidnyan-bot",
            "category": "ai",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_create_project_validates_slug() -> None:
    override_db([])

    response = client.post(
        "/api/v1/admin/projects",
        headers=auth_headers(),
        json={
            "title": "Invalid",
            "slug": "Not A Slug",
            "category": "ai",
        },
    )

    assert response.status_code == 422


def test_get_admin_project_returns_detail() -> None:
    project = make_project(technologies=["Python"])
    override_db([project])

    response = client.get(
        f"/api/v1/admin/projects/{project.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["data"]["technologies"][0]["name"] == "Python"


def test_get_admin_project_returns_404_when_missing() -> None:
    override_db([])

    response = client.get(
        f"/api/v1/admin/projects/{uuid.uuid4()}",
        headers=auth_headers(),
    )

    assert response.status_code == 404


def test_patch_project_updates_fields() -> None:
    project = make_project()
    session = override_db([project])

    response = client.patch(
        f"/api/v1/admin/projects/{project.id}",
        headers=auth_headers(),
        json={"title": "Updated title", "status": "In progress"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Updated title"
    assert data["status"] == "In progress"
    assert data["slug"] == "vidnyan-bot"
    assert session.committed


def test_patch_project_rejects_slug_conflict() -> None:
    project = make_project()
    other = make_project(slug="other-project")
    override_db([project, other], scalar_value=other)

    response = client.patch(
        f"/api/v1/admin/projects/{project.id}",
        headers=auth_headers(),
        json={"slug": "other-project"},
    )

    assert response.status_code == 409


def test_patch_project_rejects_null_required_field() -> None:
    project = make_project()
    override_db([project])

    response = client.patch(
        f"/api/v1/admin/projects/{project.id}",
        headers=auth_headers(),
        json={"category": None},
    )

    assert response.status_code == 422


def test_publish_and_feature_flags_toggle() -> None:
    project = make_project(is_published=False, is_featured=False)
    session = override_db([project])

    published = client.patch(
        f"/api/v1/admin/projects/{project.id}/publish",
        headers=auth_headers(),
        json={"value": True},
    )
    featured = client.patch(
        f"/api/v1/admin/projects/{project.id}/feature",
        headers=auth_headers(),
        json={"value": True},
    )

    assert published.status_code == 200
    assert published.json()["data"]["is_published"] is True
    assert featured.status_code == 200
    assert featured.json()["data"]["is_featured"] is True
    assert session.committed


def test_delete_project_removes_project() -> None:
    project = make_project()
    session = override_db([project])

    response = client.delete(
        f"/api/v1/admin/projects/{project.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
    assert session.deleted is project
    assert session.committed


def test_reorder_projects_updates_display_order() -> None:
    first = make_project(slug="first-project", display_order=0)
    second = make_project(slug="second-project", display_order=1)
    session = override_db([first, second])

    response = client.patch(
        "/api/v1/admin/projects/reorder",
        headers=auth_headers(),
        json={
            "items": [
                {"id": str(first.id), "display_order": 1},
                {"id": str(second.id), "display_order": 0},
            ]
        },
    )

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["data"]] == [
        "second-project",
        "first-project",
    ]
    assert session.committed


def test_create_update_and_delete_project_section() -> None:
    project = make_project()
    session = override_db([project])

    created = client.post(
        f"/api/v1/admin/projects/{project.id}/sections",
        headers=auth_headers(),
        json={"overline": "01 / Problem", "title": "Problem framing"},
    )
    assert created.status_code == 201
    section_id = created.json()["data"]["id"]

    updated = client.patch(
        f"/api/v1/admin/projects/{project.id}/sections/{section_id}",
        headers=auth_headers(),
        json={"title": "Updated framing"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["title"] == "Updated framing"

    deleted = client.delete(
        f"/api/v1/admin/projects/{project.id}/sections/{section_id}",
        headers=auth_headers(),
    )
    assert deleted.status_code == 204
    assert session.committed


def test_section_returns_404_when_missing() -> None:
    project = make_project()
    override_db([project])

    response = client.patch(
        f"/api/v1/admin/projects/{project.id}/sections/{uuid.uuid4()}",
        headers=auth_headers(),
        json={"title": "Missing"},
    )

    assert response.status_code == 404


def test_create_and_delete_project_technology() -> None:
    project = make_project()
    session = override_db([project])

    created = client.post(
        f"/api/v1/admin/projects/{project.id}/technologies",
        headers=auth_headers(),
        json={"name": "Python"},
    )
    assert created.status_code == 201
    technology_id = created.json()["data"]["id"]

    deleted = client.delete(
        f"/api/v1/admin/projects/{project.id}/technologies/{technology_id}",
        headers=auth_headers(),
    )
    assert deleted.status_code == 204
    assert session.committed


def test_create_project_technology_rejects_duplicate() -> None:
    project = make_project(technologies=["Python"])
    override_db([project])

    response = client.post(
        f"/api/v1/admin/projects/{project.id}/technologies",
        headers=auth_headers(),
        json={"name": "python"},
    )

    assert response.status_code == 409
