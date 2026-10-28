from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session, sessionmaker


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return f"postgresql+psycopg://{database_url.removeprefix('postgres://')}"
    if database_url.startswith("postgresql://"):
        return f"postgresql+psycopg://{database_url.removeprefix('postgresql://')}"
    return database_url


def create_db_engine(database_url: str | URL) -> Engine:
    return create_engine(
        database_url,
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )


def create_session(engine: Engine) -> Session:
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    return session_factory()
