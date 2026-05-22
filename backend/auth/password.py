from __future__ import annotations

import re

from passlib.context import CryptContext

# Use pbkdf2_sha256 for portability in dev/test environments
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

_WEAK_PASSWORDS = {
    "password123",
    "admin123",
    "qwerty",
    "12345678",
    "password",
    "admin",
}


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if password.lower() in _WEAK_PASSWORDS or any(word in password.lower() for word in _WEAK_PASSWORDS):
        return False, "Password is too weak."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain a number."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain a special character."
    return True, "Password strength is acceptable."


def hash_password(password: str) -> str:
    ok, reason = validate_password_strength(password)
    if not ok:
        raise ValueError(reason)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass
    # Support legacy bcrypt hashes from SQL seed data
    if hashed_password.startswith("$2"):
        try:
            import bcrypt

            return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
        except Exception:
            return False
    return False

