from sqlalchemy.engine import URL

from app.db.deps import _hyperdrive_database_url


def test_hyperdrive_uses_connection_string_when_present() -> None:
    url = _hyperdrive_database_url(
        {
            "connectionString": "postgres://user:pass@db.example.com:5432/portfolio",
            "host": "ignored",
        }
    )

    assert url == "postgresql+psycopg://user:pass@db.example.com:5432/portfolio"


def test_hyperdrive_builds_url_from_binding_fields() -> None:
    url = _hyperdrive_database_url(
        {
            "host": "db.example.com",
            "port": 5432,
            "user": "user",
            "password": "pass",
            "database": "portfolio",
        }
    )

    assert isinstance(url, URL)
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "db.example.com"
    assert url.port == 5432
    assert url.username == "user"
    assert url.password == "pass"
    assert url.database == "portfolio"
    assert url.query["sslmode"] == "disable"
