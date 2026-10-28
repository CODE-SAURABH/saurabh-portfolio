from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password, verify_token
from app.db.deps import get_db
from app.main import app
from app.models.admin import AdminCredential

client = TestClient(app)
PASSWORD = "test-admin-password"
PASSWORD_HASH = hash_password(PASSWORD)


class FakeAdminSession:
    def __init__(self, credential: AdminCredential | None) -> None:
        self.credential = credential
        self.committed = False

    def scalar(self, statement: object) -> AdminCredential | None:
        return self.credential

    def commit(self) -> None:
        self.committed = True


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def override_db(credential: AdminCredential | None) -> FakeAdminSession:
    session = FakeAdminSession(credential)
    app.dependency_overrides[get_db] = lambda: session
    return session


def test_login_returns_token_for_valid_password() -> None:
    session = override_db(AdminCredential(password_hash=PASSWORD_HASH))

    response = client.post("/api/v1/admin/auth/login", json={"password": PASSWORD})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600
    assert verify_token(data["access_token"])
    assert session.committed


def test_login_rejects_invalid_password() -> None:
    override_db(AdminCredential(password_hash=PASSWORD_HASH))

    response = client.post(
        "/api/v1/admin/auth/login",
        json={"password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Invalid credentials",
            "detail": None,
        }
    }


def test_login_rejects_missing_credential() -> None:
    override_db(None)

    response = client.post("/api/v1/admin/auth/login", json={"password": PASSWORD})

    assert response.status_code == 401


def test_login_validates_empty_password() -> None:
    override_db(AdminCredential(password_hash=PASSWORD_HASH))

    response = client.post("/api/v1/admin/auth/login", json={"password": ""})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_me_requires_token() -> None:
    response = client.get("/api/v1/admin/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_me_returns_admin_for_valid_token() -> None:
    token = create_access_token()

    response = client.get(
        "/api/v1/admin/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"is_admin": True}}


def test_me_rejects_invalid_token() -> None:
    response = client.get(
        "/api/v1/admin/auth/me",
        headers={"Authorization": "Bearer invalid"},
    )

    assert response.status_code == 401


def test_logout_requires_and_accepts_token() -> None:
    token = create_access_token()

    response = client.post(
        "/api/v1/admin/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"message": "Logged out"}}
