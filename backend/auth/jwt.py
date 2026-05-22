from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from .blacklist import add_to_blacklist, is_blacklisted

JWT_SECRET = os.getenv("JWT_SECRET", "querysafe-dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    payload = data.copy()
    now = datetime.now(UTC)
    payload.update(
        {
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
            "jti": uuid4().hex,
            "type": token_type,
        }
    )
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        data,
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        data,
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def create_temp_token(data: dict, expires_delta: timedelta | None = None) -> str:
    return _create_token(data, expires_delta or timedelta(minutes=10), "temp")


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def verify_token(token: str, expected_type: str | None = None) -> dict:
    if is_blacklisted(token):
        raise JWTError("Token is blacklisted.")
    payload = decode_token(token)
    if expected_type and payload.get("type") != expected_type:
        raise JWTError(f"Expected {expected_type} token.")
    return payload


def blacklist_token(token: str, ttl_seconds: int | None = None) -> None:
    add_to_blacklist(token, ttl_seconds=ttl_seconds)

