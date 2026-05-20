"""
auth/jwt.py — JWT creation, validation, and Redis-backed blacklisting.
QuerySafe — Person 2: Security & Auth
"""

import os
from datetime import datetime, timedelta, timezone

import redis
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JWT_SECRET: str = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is not set.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Test Redis connection to see if it is running, fallback to MockRedis if not
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("[QuerySafe] Connected to Redis successfully.")
except Exception:
    import time
    print("[QuerySafe] Redis connection failed. Falling back to In-Memory token blacklist.")
    
    class MockRedis:
        def __init__(self):
            self.store = {}
        def setex(self, name: str, time_sec: int, value: str):
            self.store[name] = (value, time.time() + time_sec)
        def exists(self, name: str) -> bool:
            if name in self.store:
                val, expiry = self.store[name]
                if time.time() < expiry:
                    return True
                del self.store[name]
            return False
            
    redis_client = MockRedis()

bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

def create_access_token(data: dict) -> str:
    """Sign a JWT access token with a 30-minute expiry."""
    payload = data.copy()
    payload.update({
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Sign a JWT refresh token with a 7-day expiry."""
    payload = data.copy()
    payload.update({
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    })
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------

def verify_token(token: str, token_type: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises ValueError if the token is invalid, expired, blacklisted,
    or of the wrong type.
    """
    if is_blacklisted(token):
        raise ValueError("Token has been revoked.")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc

    if payload.get("type") != token_type:
        raise ValueError(f"Expected token type '{token_type}', got '{payload.get('type')}'.")

    return payload


# ---------------------------------------------------------------------------
# Redis blacklist
# ---------------------------------------------------------------------------

def blacklist_token(token: str, expires_in_seconds: int) -> None:
    """Store the token in Redis so it can never be reused after logout."""
    redis_client.setex(f"blacklist:{token}", expires_in_seconds, "1")


def is_blacklisted(token: str) -> bool:
    """Return True if the token is present in the Redis blacklist."""
    return redis_client.exists(f"blacklist:{token}") == 1


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI Depends() function.
    Reads the Bearer token from the Authorization header,
    validates it and returns the decoded payload.

    Returned dict shape: { user_id, email, role }
    """
    token = credentials.credentials
    try:
        payload = verify_token(token, "access")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("user_id")
    email = payload.get("email")
    role = payload.get("role")

    if not user_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is incomplete.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": user_id, "email": email, "role": role, "_raw_token": token}
