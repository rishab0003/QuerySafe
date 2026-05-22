from __future__ import annotations

import os
import time
from typing import Any

try:
    from redis import Redis
except Exception:  # pragma: no cover
    Redis = Any  # type: ignore[misc,assignment]

_LOCAL_STATE: dict[str, list[float]] = {}


def _redis_client() -> Any:
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    try:
        from redis import Redis

        return Redis.from_url(url, decode_responses=True)
    except Exception:
        return None


def allow_request(key: str, identity: str, limit: int = 30, window_seconds: int = 60) -> bool:
    client = _redis_client()
    now = time.time()
    redis_key = f"rl:{key}:{identity}"
    if client is not None:
        try:
            count = client.get(redis_key)
            if not count:
                client.setex(redis_key, window_seconds, 1)
                return True
            if int(count) >= limit:
                return False
            client.incr(redis_key)
            return True
        except Exception:
            pass
    # fallback local
    arr = _LOCAL_STATE.setdefault(redis_key, [])
    arr[:] = [t for t in arr if t > now - window_seconds]
    if len(arr) >= limit:
        return False
    arr.append(now)
    return True

