from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.db.deps import get_db
from app.main import app

client = TestClient(app)


class HealthySession:
    def execute(self, statement: object) -> None:
        return None


class FailingSession:
    def execute(self, statement: object) -> None:
        raise RuntimeError("database unavailable")


def override_healthy_db() -> Iterator[HealthySession]:
    yield HealthySession()


def override_failing_db() -> Iterator[FailingSession]:
    yield FailingSession()


def test_live_returns_ok() -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ok_when_database_responds() -> None:
    app.dependency_overrides[get_db] = override_healthy_db
    try:
        response = client.get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "connected"}


def test_ready_returns_503_when_database_fails() -> None:
    app.dependency_overrides[get_db] = override_failing_db
    try:
        response = client.get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "db": "error"}


def test_cors_allows_local_frontend() -> None:
    response = client.get(
        "/api/v1/health/live",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
