from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Iterator

logger = logging.getLogger("querysafe.auth.db")

_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
_pool = None
_db_available: bool | None = None


def database_url() -> str:
    return _DATABASE_URL


def is_db_configured() -> bool:
    return bool(_DATABASE_URL)


@contextmanager
def get_connection() -> Iterator:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    conn = psycopg2.connect(_DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_db_connection() -> bool:
    global _db_available
    if not is_db_configured():
        _db_available = False
        return False
    if _db_available is not None:
        return _db_available
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        _db_available = True
        logger.info("PostgreSQL auth store enabled.")
    except Exception as exc:
        _db_available = False
        logger.warning("PostgreSQL unavailable, using in-memory auth store: %s", exc)
    return _db_available


def init_auth_schema() -> None:
    """Apply migration 002 columns when DB is up but init script was skipped."""
    if not check_db_connection():
        return
    statements = [
        "ALTER TYPE user_department ADD VALUE IF NOT EXISTS 'general'",
        "ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'viewer'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password TEXT",
        """
        ALTER TABLE users
            ADD COLUMN IF NOT EXISTS approval_status TEXT NOT NULL DEFAULT 'approved'
                CHECK (approval_status IN ('pending', 'approved', 'rejected'))
        """,
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES users(id) ON DELETE SET NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ",
        "ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_jti TEXT",
        """
        CREATE TABLE IF NOT EXISTS oauth_accounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            provider TEXT NOT NULL CHECK (provider IN ('google', 'github')),
            provider_user_id TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (provider, provider_user_id)
        )
        """,
    ]
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
                cur.execute(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_name = 'users' AND column_name = 'password_hash'
                        ) THEN
                            UPDATE users
                            SET hashed_password = COALESCE(hashed_password, password_hash)
                            WHERE hashed_password IS NULL;
                        END IF;
                    END
                    $$;
                    """
                )
    except Exception as exc:
        logger.warning("Could not ensure auth schema: %s", exc)
