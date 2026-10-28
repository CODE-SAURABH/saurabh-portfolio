import pytest

from app.core.config import Settings

BASE_SETTINGS = {
    "DATABASE_URL": "postgresql+psycopg://user:pass@localhost:5432/portfolio",
    "SECRET_KEY": "test-secret",
}


def create_settings(**overrides: object) -> Settings:
    values = {**BASE_SETTINGS, **overrides}
    return Settings.model_validate(values)


def test_cors_origins_parses_json_list() -> None:
    settings = create_settings(CORS_ORIGINS='["http://localhost:5173", "https://example.com"]')

    assert settings.CORS_ORIGINS == ["http://localhost:5173", "https://example.com"]


def test_cors_origins_parses_comma_separated_list() -> None:
    settings = create_settings(CORS_ORIGINS="http://localhost:5173, https://example.com")

    assert settings.CORS_ORIGINS == ["http://localhost:5173", "https://example.com"]


def test_cors_origins_accepts_empty_value() -> None:
    settings = create_settings(CORS_ORIGINS="")

    assert settings.CORS_ORIGINS == []


def test_database_url_can_be_empty_for_hyperdrive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None, SECRET_KEY="test-secret")  # type: ignore[call-arg]

    assert settings.DATABASE_URL == ""
