import asyncio
from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any

from fastapi import Depends, Request
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import create_db_engine, create_session, normalize_database_url

_db_lock = asyncio.Lock()


def _read_binding(binding: Any, name: str) -> Any:
    if binding is None:
        return None
    if isinstance(binding, Mapping):
        return binding.get(name)
    return getattr(binding, name, None)


def _hyperdrive_database_url(binding: Any) -> str | URL:
    connection_string = _read_binding(binding, "connectionString")
    if connection_string:
        return normalize_database_url(connection_string)

    return URL.create(
        "postgresql+psycopg",
        username=_read_binding(binding, "user"),
        password=_read_binding(binding, "password"),
        host=_read_binding(binding, "host"),
        port=int(_read_binding(binding, "port")),
        database=_read_binding(binding, "database"),
        query={"sslmode": "disable"},
    )


def resolve_database_url(request: Request) -> str | URL:
    env = request.scope.get("env")
    hyperdrive = _read_binding(env, "HYPERDRIVE") if env is not None else None
    if hyperdrive is not None:
        return _hyperdrive_database_url(hyperdrive)

    database_url = get_settings().DATABASE_URL
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured and HYPERDRIVE is not bound")
    return normalize_database_url(database_url)


async def get_db(request: Request) -> AsyncIterator[Session]:
    engine = create_db_engine(resolve_database_url(request))
    try:
        async with _db_lock:
            with create_session(engine) as session:
                yield session
    finally:
        engine.dispose()


DatabaseSession = Annotated[Session, Depends(get_db)]
