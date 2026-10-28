"""Resume storage backed by the Cloudflare R2 binding."""

import time
from typing import Any

from app.core.config import get_settings


class StorageUnavailableError(RuntimeError):
    """Raised when R2 is not configured in the current runtime."""


def _get_bucket() -> Any | None:
    try:
        from workers import env
    except Exception:
        return None

    try:
        return getattr(env, "RESUME_BUCKET", None)
    except Exception:
        return None


async def upload_resume_pdf(data: bytes) -> str:
    base_url = get_settings().R2_PUBLIC_BASE_URL.strip()
    if not base_url:
        raise StorageUnavailableError("R2_PUBLIC_BASE_URL is not configured")

    bucket = _get_bucket()
    if bucket is None:
        raise StorageUnavailableError("RESUME_BUCKET binding is not available")

    key = "resume/resume.pdf"
    try:
        await bucket.put(key, data)
    except Exception as exc:
        raise StorageUnavailableError("R2 upload failed") from exc

    version = int(time.time())
    return f"{base_url.rstrip('/')}/{key}?v={version}"
