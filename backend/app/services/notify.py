"""Best-effort Telegram notification for contact submissions.

Per ADR-011 this project notifies the owner via Telegram only. Failures are
logged and never block the contact form response.
"""

import asyncio
import json
import logging
from html import escape
from http import HTTPMethod
from typing import Any

from app.core.config import get_settings
from app.models.contact import ContactSubmission

logger = logging.getLogger(__name__)


def _build_text(submission: ContactSubmission) -> str:
    subject = escape(submission.subject or "-")
    message = escape(submission.message[:500])
    return (
        "<b>New portfolio message</b>\n\n"
        f"<b>From:</b> {escape(submission.name)} ({escape(submission.email)})\n"
        f"<b>Subject:</b> {subject}\n\n"
        f"{message}"
    )


def _post_json(url: str, payload: dict[str, Any]) -> bool:
    import urllib.request

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return 200 <= response.status < 300
    except Exception:
        logger.warning("Telegram notification failed", exc_info=True)
        return False


async def send_contact_notification(submission: ContactSubmission) -> bool:
    """Send a Telegram message. Returns True only when Telegram accepted it."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return False

    url = (
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": _build_text(submission),
        "parse_mode": "HTML",
    }

    try:
        from workers import fetch
    except Exception:
        return await asyncio.to_thread(_post_json, url, payload)

    try:
        response = await fetch(
            url,
            method=HTTPMethod.POST,
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
        )
        return bool(getattr(response, "ok", False))
    except Exception:
        logger.warning("Telegram notification failed", exc_info=True)
        return False
