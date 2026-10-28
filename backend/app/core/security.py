from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

ALGORITHM = "HS256"
ADMIN_SUBJECT = "admin"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def create_access_token(expire_minutes: int | None = None) -> str:
    settings = get_settings()
    expires_in = (
        expire_minutes
        if expire_minutes is not None
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    now = datetime.now(UTC)
    payload = {
        "sub": ADMIN_SUBJECT,
        "iat": now,
        "exp": now + timedelta(minutes=expires_in),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            get_settings().SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        return None

    if payload.get("sub") != ADMIN_SUBJECT:
        return None
    return payload


def verify_token(token: str) -> bool:
    return decode_access_token(token) is not None
