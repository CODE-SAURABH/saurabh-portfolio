from datetime import UTC, datetime, timedelta

from jose import jwt

from app.core.config import get_settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    verify_token,
)


def test_hash_and_verify_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_verify_password_rejects_malformed_hash() -> None:
    assert not verify_password("password", "not-a-bcrypt-hash")


def test_access_token_round_trip() -> None:
    token = create_access_token()
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "admin"
    assert verify_token(token)


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(expire_minutes=-1)

    assert not verify_token(token)


def test_tampered_access_token_is_rejected() -> None:
    token = create_access_token()

    assert not verify_token(f"{token}tampered")


def test_token_with_wrong_subject_is_rejected() -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "someone-else",
            "iat": now,
            "exp": now + timedelta(minutes=60),
        },
        get_settings().SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert not verify_token(token)
