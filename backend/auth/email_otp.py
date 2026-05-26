from __future__ import annotations

import os
import smtplib
import logging
from datetime import datetime, timedelta, UTC
from email.message import EmailMessage
from random import randint
from threading import RLock

logger = logging.getLogger("querysafe.auth.email_otp")

_LOCK = RLock()
# user_id -> (code, expires_at, email)
_OTPS: dict[str, tuple[str, datetime, str]] = {}


def _now() -> datetime:
    return datetime.now(tz=UTC)


def generate_otp_for_user(user_id: str, email: str, ttl_seconds: int = 300) -> str:
    with _LOCK:
        code = f"{randint(0,999999):06d}"
        expires = _now() + timedelta(seconds=ttl_seconds)
        _OTPS[user_id] = (code, expires, email)
        return code


def verify_otp_for_user(user_id: str, code: str) -> bool:
    with _LOCK:
        entry = _OTPS.get(user_id)
        if not entry:
            return False
        stored_code, expires, _ = entry
        if _now() > expires:
            del _OTPS[user_id]
            return False
        if stored_code != code:
            return False
        # consume
        del _OTPS[user_id]
        return True


def is_smtp_configured() -> bool:
    return bool(os.getenv("SMTP_HOST"))


def send_otp_via_smtp(email: str, code: str) -> bool:
    host = os.getenv("SMTP_HOST")
    if not host:
        return False
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_addr = os.getenv("SMTP_FROM", "no-reply@querysafe.io")
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your QuerySafe One-Time 2FA Code"
        msg["From"] = from_addr
        msg["To"] = email
        msg.set_content(f"Your one-time 2FA code is: {code}\nIt will expire in 5 minutes.")
        if user and password:
            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            server.quit()
        else:
            # try unauthenticated
            server = smtplib.SMTP(host, port, timeout=10)
            server.send_message(msg)
            server.quit()
        logger.info("Sent OTP to %s via SMTP", email)
        return True
    except Exception as exc:
        logger.exception("Failed to send OTP via SMTP: %s", exc)
        return False
