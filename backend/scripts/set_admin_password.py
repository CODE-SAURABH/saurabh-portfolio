import getpass
import os

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import create_db_engine, create_session
from app.models.admin import AdminCredential


def main() -> None:
    password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Set admin password: ")
    if len(password) < 12:
        raise SystemExit("Admin password must be at least 12 characters")
    if len(password.encode("utf-8")) > 72:
        raise SystemExit("Admin password must be at most 72 bytes")

    database_url = get_settings().DATABASE_URL
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    engine = create_db_engine(database_url)
    try:
        with create_session(engine) as session:
            credential = session.scalar(select(AdminCredential).limit(1))
            password_hash = hash_password(password)
            if credential is None:
                session.add(AdminCredential(password_hash=password_hash))
            else:
                credential.password_hash = password_hash
            session.commit()
    finally:
        engine.dispose()

    print("Admin password updated.")


if __name__ == "__main__":
    main()
