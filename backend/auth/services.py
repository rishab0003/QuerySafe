from __future__ import annotations

from threading import RLock

from .models import StoredUser
from .password import hash_password, verify_password
from .utils import generate_user_id, normalize_email, utcnow

_LOCK = RLock()
_USERS_BY_EMAIL: dict[str, StoredUser] = {}
_USERS_BY_ID: dict[str, StoredUser] = {}


def reset_registry() -> None:
    with _LOCK:
        _USERS_BY_EMAIL.clear()
        _USERS_BY_ID.clear()


def get_user_by_email(email: str) -> StoredUser | None:
    return _USERS_BY_EMAIL.get(normalize_email(email))


def get_user_by_id(user_id: str) -> StoredUser | None:
    return _USERS_BY_ID.get(user_id)


def register_user(email: str, password: str, department: str, role: str) -> StoredUser:
    normalized_email = normalize_email(email)
    with _LOCK:
        if normalized_email in _USERS_BY_EMAIL:
            raise ValueError("Email already registered.")
        user = StoredUser(
            id=generate_user_id(),
            email=normalized_email,
            hashed_password=hash_password(password),
            department=department.strip().lower(),
            role=role.strip().lower(),
        )
        _USERS_BY_EMAIL[normalized_email] = user
        _USERS_BY_ID[user.id] = user
        return user


def authenticate_user(email: str, password: str) -> StoredUser | None:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def set_totp_secret(user_id: str, secret: str) -> StoredUser:
    with _LOCK:
        user = _USERS_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.totp_secret = secret
        user.updated_at = utcnow()
        return user


def mark_2fa_enabled(user_id: str, enabled: bool = True) -> StoredUser:
    with _LOCK:
        user = _USERS_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.is_2fa_enabled = enabled
        user.updated_at = utcnow()
        return user


def set_refresh_token_state(user_id: str, jti: str | None, expires_at=None) -> StoredUser:
    with _LOCK:
        user = _USERS_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.refresh_token_jti = jti
        user.refresh_token_expires_at = expires_at
        user.updated_at = utcnow()
        return user

