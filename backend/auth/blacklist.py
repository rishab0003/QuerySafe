from __future__ import annotations

import hashlib
import os
import time
from typing import Any

from jose import jwt

try:
    from redis import Redis
except Exception:  # pragma: no cover
    Redis = Any  # type: ignore[misc,assignment]

_LOCAL_BLACKLIST: dict[str, float] = {}


def _redis_client() -> Any:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None
    try:
        from redis import Redis

        return Redis.from_url(redis_url, decode_responses=True)
    except Exception:
        return None


def _token_key(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _token_ttl_seconds(token: str, default_ttl: int = 60 * 60 * 24 * 7) -> int:
    try:
        claims = jwt.get_unverified_claims(token)
        exp = int(claims.get("exp", 0))
        ttl = exp - int(time.time())
        return max(ttl, 1)
    except Exception:
        return default_ttl


def add_to_blacklist(token: str, ttl_seconds: int | None = None) -> None:
    ttl = ttl_seconds or _token_ttl_seconds(token)
    key = _token_key(token)
    client = _redis_client()
    if client is not None:
        client.setex(key, ttl, "1")
        return
    _LOCAL_BLACKLIST[key] = time.time() + ttl


def is_blacklisted(token: str) -> bool:
    key = _token_key(token)
    client = _redis_client()
    if client is not None:
        return bool(client.get(key))
    expiry = _LOCAL_BLACKLIST.get(key)
    if expiry is None:
        return False
    if expiry < time.time():
        _LOCAL_BLACKLIST.pop(key, None)
        return False
    return True


def remove_blacklisted_token(token: str) -> None:
    key = _token_key(token)
    client = _redis_client()
    if client is not None:
        client.delete(key)
        return
    _LOCAL_BLACKLIST.pop(key, None)

