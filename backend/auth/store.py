from __future__ import annotations

import logging
from datetime import UTC, datetime
from threading import RLock

from .db import check_db_connection, get_connection, init_auth_schema
from .models import StoredUser
from .password import hash_password, verify_password
from .utils import generate_user_id, normalize_email, utcnow

logger = logging.getLogger("querysafe.auth.store")

_LOCK = RLock()
_MEMORY_BY_EMAIL: dict[str, StoredUser] = {}
_MEMORY_BY_ID: dict[str, StoredUser] = {}

APPROVAL_PENDING = "pending"
APPROVAL_APPROVED = "approved"
APPROVAL_REJECTED = "rejected"


def _row_to_user(row: dict) -> StoredUser:
    created = row.get("created_at") or utcnow()
    updated = row.get("updated_at") or created
    if isinstance(created, datetime) and created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    if isinstance(updated, datetime) and updated.tzinfo is None:
        updated = updated.replace(tzinfo=UTC)
    approved_at = row.get("approved_at")
    if isinstance(approved_at, datetime) and approved_at.tzinfo is None:
        approved_at = approved_at.replace(tzinfo=UTC)
    return StoredUser(
        id=str(row["id"]),
        email=str(row["email"]).lower(),
        hashed_password=row.get("hashed_password") or "",
        full_name=row.get("full_name") or "",
        department=(row.get("department") or "general").lower(),
        role=(row.get("role") or "viewer").lower(),
        totp_secret=row.get("totp_secret"),
        is_2fa_enabled=bool(row.get("is_2fa_enabled")),
        is_active=bool(row.get("is_active", True)),
        approval_status=row.get("approval_status") or APPROVAL_APPROVED,
        approved_by=str(row["approved_by"]) if row.get("approved_by") else None,
        approved_at=approved_at,
        refresh_token_jti=row.get("refresh_token_jti"),
        created_at=created,
        updated_at=updated,
    )


def _use_postgres() -> bool:
    return check_db_connection()


def reset_registry() -> None:
    with _LOCK:
        _MEMORY_BY_EMAIL.clear()
        _MEMORY_BY_ID.clear()


def get_user_by_email(email: str) -> StoredUser | None:
    normalized = normalize_email(email)
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE LOWER(email::text) = %s", (normalized,))
                row = cur.fetchone()
                return _row_to_user(row) if row else None
    return _MEMORY_BY_EMAIL.get(normalized)


def get_user_by_id(user_id: str) -> StoredUser | None:
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                return _row_to_user(row) if row else None
    return _MEMORY_BY_ID.get(user_id)


def list_users(approval_status: str | None = None) -> list[StoredUser]:
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                if approval_status:
                    cur.execute("SELECT * FROM users WHERE approval_status = %s ORDER BY created_at DESC", (approval_status,))
                else:
                    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
                return [_row_to_user(r) for r in cur.fetchall()]
    users = list(_MEMORY_BY_ID.values())
    if approval_status:
        users = [u for u in users if u.approval_status == approval_status]
    return sorted(users, key=lambda u: u.created_at, reverse=True)


def register_user(
    email: str,
    password: str,
    department: str,
    role: str,
    *,
    full_name: str = "",
    approval_status: str = APPROVAL_PENDING,
    is_active: bool = False,
) -> StoredUser:
    normalized_email = normalize_email(email)
    hashed = hash_password(password)
    dept = department.strip().lower() or "general"
    user_role = role.strip().lower()

    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE LOWER(email::text) = %s", (normalized_email,))
                if cur.fetchone():
                    raise ValueError("Email already registered.")
                cur.execute(
                    """
                    INSERT INTO users (
                        email, hashed_password, full_name, role, department,
                        approval_status, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """,
                    (
                        normalized_email,
                        hashed,
                        full_name.strip() or normalized_email.split("@")[0],
                        user_role,
                        dept,
                        approval_status,
                        is_active,
                    ),
                )
                return _row_to_user(cur.fetchone())

    with _LOCK:
        if normalized_email in _MEMORY_BY_EMAIL:
            raise ValueError("Email already registered.")
        user = StoredUser(
            id=generate_user_id(),
            email=normalized_email,
            hashed_password=hashed,
            full_name=full_name.strip() or normalized_email.split("@")[0],
            department=dept,
            role=user_role,
            approval_status=approval_status,
            is_active=is_active,
        )
        _MEMORY_BY_EMAIL[normalized_email] = user
        _MEMORY_BY_ID[user.id] = user
        return user


def create_oauth_user(
    email: str,
    full_name: str,
    provider: str,
    provider_user_id: str,
) -> StoredUser:
    normalized_email = normalize_email(email)
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id FROM oauth_accounts WHERE provider = %s AND provider_user_id = %s",
                    (provider, provider_user_id),
                )
                link = cur.fetchone()
                if link:
                    return get_user_by_id(str(link["user_id"]))  # type: ignore[return-value]

                cur.execute(
                    "SELECT id FROM users WHERE LOWER(email::text) = %s",
                    (normalized_email,),
                )
                existing = cur.fetchone()
                if existing:
                    user_id = str(existing["id"])
                else:
                    cur.execute(
                        """
                            INSERT INTO users (
                                email, hashed_password, full_name, role, department,
                                approval_status, is_active
                            ) VALUES (%s, NULL, %s, 'viewer', 'general', %s, FALSE)
                                    RETURNING id
                        """,
                            (normalized_email, full_name or normalized_email.split("@")[0], APPROVAL_PENDING),
                        )
                    user_id = str(cur.fetchone()["id"])

                cur.execute(
                    """
                    INSERT INTO oauth_accounts (user_id, provider, provider_user_id, email)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (provider, provider_user_id) DO NOTHING
                    """,
                    (user_id, provider, provider_user_id, normalized_email),
                )
                user = get_user_by_id(user_id)
                if user is None:
                    raise ValueError("Failed to create OAuth user.")
                return user

    with _LOCK:
        user = _MEMORY_BY_EMAIL.get(normalized_email)
        if user is None:
            user = StoredUser(
                id=generate_user_id(),
                email=normalized_email,
                hashed_password="",
                full_name=full_name or normalized_email.split("@")[0],
                department="general",
                role="viewer",
                approval_status=APPROVAL_PENDING,
                is_active=False,
            )
            _MEMORY_BY_EMAIL[normalized_email] = user
            _MEMORY_BY_ID[user.id] = user
        return user


def authenticate_user(email: str, password: str) -> StoredUser | None:
    user = get_user_by_email(email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def approve_user(user_id: str, admin_id: str, role: str, department: str) -> StoredUser:
    dept = department.strip().lower() or "general"
    user_role = role.strip().lower()
    now = utcnow()

    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users SET
                        role = %s, department = %s,
                        approval_status = %s, is_active = TRUE,
                        approved_by = %s, approved_at = %s, updated_at = NOW()
                    WHERE id = %s
                          RETURNING id, email, hashed_password, full_name, role, department,
                                        totp_secret, is_2fa_enabled, is_active, approval_status,
                                        approved_by, approved_at, created_at, updated_at,
                                    refresh_token_jti
                    """,
                    (user_role, dept, APPROVAL_APPROVED, admin_id, now, user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError("User not found.")
                return _row_to_user(row)

    with _LOCK:
        user = _MEMORY_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.role = user_role
        user.department = dept
        user.approval_status = APPROVAL_APPROVED
        user.is_active = True
        user.approved_by = admin_id
        user.approved_at = now
        user.updated_at = now
        return user


def reject_user(user_id: str, admin_id: str) -> StoredUser:
    now = utcnow()
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users SET
                        approval_status = %s, is_active = FALSE,
                        approved_by = %s, approved_at = %s, updated_at = NOW()
                    WHERE id = %s
                          RETURNING id, email, hashed_password, full_name, role, department,
                                        totp_secret, is_2fa_enabled, is_active, approval_status,
                                        approved_by, approved_at, created_at, updated_at,
                                    refresh_token_jti
                    """,
                    (APPROVAL_REJECTED, admin_id, now, user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError("User not found.")
                return _row_to_user(row)

    with _LOCK:
        user = _MEMORY_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.approval_status = APPROVAL_REJECTED
        user.is_active = False
        user.approved_by = admin_id
        user.approved_at = now
        user.updated_at = now
        return user


def update_user_role(user_id: str, role: str, department: str | None = None) -> StoredUser:
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                if department is not None:
                    cur.execute(
                        """
                        UPDATE users SET role = %s, department = %s, updated_at = NOW()
                        WHERE id = %s
                        RETURNING id, email, password_hash, full_name, role, department,
                                      totp_secret, is_2fa_enabled, is_active, approval_status,
                                      approved_by, approved_at, created_at, updated_at,
                                  refresh_token_jti
                        """,
                        (role.strip().lower(), department.strip().lower(), user_id),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE users SET role = %s, updated_at = NOW()
                        WHERE id = %s
                        RETURNING id, email, password_hash, full_name, role, department,
                                  totp_secret, is_2fa_enabled, is_active, approval_status,
                                  approved_by, approved_at, created_at, updated_at,
                           refresh_token_jti
                        """,
                        (role.strip().lower(), user_id),
                    )
                row = cur.fetchone()
                if not row:
                    raise ValueError("User not found.")
                return _row_to_user(row)

    with _LOCK:
        user = _MEMORY_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.role = role.strip().lower()
        if department is not None:
            user.department = department.strip().lower()
        user.updated_at = utcnow()
        return user


def set_totp_secret(user_id: str, secret: str) -> StoredUser:
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET totp_secret = %s, updated_at = NOW() WHERE id = %s RETURNING *",
                    (secret, user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError("User not found.")
                return _row_to_user(row)

    with _LOCK:
        user = _MEMORY_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.totp_secret = secret
        user.updated_at = utcnow()
        return user


def mark_2fa_enabled(user_id: str, enabled: bool = True) -> StoredUser:
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_2fa_enabled = %s, updated_at = NOW() WHERE id = %s RETURNING *",
                    (enabled, user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError("User not found.")
                return _row_to_user(row)

    with _LOCK:
        user = _MEMORY_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.is_2fa_enabled = enabled
        user.updated_at = utcnow()
        return user


def set_refresh_token_state(user_id: str, jti: str | None, expires_at=None) -> StoredUser:
    if _use_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET refresh_token_jti = %s, updated_at = NOW() WHERE id = %s",
                    (jti, user_id),
                )
        user = get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        user.refresh_token_jti = jti
        user.refresh_token_expires_at = expires_at
        return user

    with _LOCK:
        user = _MEMORY_BY_ID.get(user_id)
        if not user:
            raise ValueError("User not found.")
        user.refresh_token_jti = jti
        user.refresh_token_expires_at = expires_at
        user.updated_at = utcnow()
        return user


def ensure_bootstrap_admin() -> None:
    """Create default admin when using in-memory store (dev)."""
    import os

    if _use_postgres():
        return
    admin_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@querysafe.io").strip().lower()
    if get_user_by_email(admin_email):
        return
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "QsBootstrap9!")
    try:
        user = register_user(
            admin_email,
            password,
            "general",
            "admin",
            full_name="QuerySafe Admin",
            approval_status=APPROVAL_APPROVED,
            is_active=True,
        )
        mark_2fa_enabled(user.id, False)
        logger.info("Bootstrap admin created: %s", admin_email)
    except ValueError:
        pass


def startup() -> None:
    init_auth_schema()
    ensure_bootstrap_admin()
