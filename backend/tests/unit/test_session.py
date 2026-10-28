from app.db.session import normalize_database_url


def test_normalize_postgres_scheme() -> None:
    assert normalize_database_url("postgres://user:pass@localhost:5432/db") == (
        "postgresql+psycopg://user:pass@localhost:5432/db"
    )


def test_normalize_postgresql_scheme() -> None:
    assert normalize_database_url("postgresql://user:pass@localhost:5432/db") == (
        "postgresql+psycopg://user:pass@localhost:5432/db"
    )


def test_normalize_psycopg_scheme_is_unchanged() -> None:
    url = "postgresql+psycopg://user:pass@localhost:5432/db"

    assert normalize_database_url(url) == url
