"""
security/audit.py — Database auditing logger for security events.
QuerySafe — Person 2: Security & Auth
"""

import json
from sqlalchemy.orm import Session
from auth.models import AuditLog


def log_action(
    db: Session,
    action: str,                  # e.g. 'login_success', 'query_blocked'
    user_id: str | None = None,
    user_email: str | None = None,
    user_role: str | None = None,
    resource: str | None = None,     # table name or endpoint
    details: str | dict | None = None,  # dict gets JSON serialized
    ip_address: str | None = None,
    user_agent: str | None = None,
    success: bool = True
) -> None:
    """
    Log an audit action to the database.
    Wrap DB commit in try/except so audit log failures do not disrupt the application flows.
    """
    try:
        # Convert dictionary to JSON string if details is a dict
        details_str = details
        if isinstance(details, dict):
            details_str = json.dumps(details)

        audit_entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            resource=resource,
            details=details_str,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        # Prevent logging failure from breaking core app logic
        print(f"[QuerySafe Error] Failed to write audit log: {e}")
        try:
            db.rollback()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def log_query_executed(db: Session, user_id: str | None, user_email: str | None, user_role: str | None, sql: str, tables: list[str], ip: str | None) -> None:
    """Convenience log wrapper for executed SQL queries."""
    details = {"sql": sql, "tables": tables}
    log_action(
        db=db,
        action="query_executed",
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        resource=", ".join(tables) if tables else None,
        details=details,
        ip_address=ip,
        success=True
    )


def log_query_blocked(db: Session, user_id: str | None, user_email: str | None, user_role: str | None, sql: str, reason: str, ip: str | None) -> None:
    """Convenience log wrapper for blocked SQL queries."""
    details = {"sql": sql, "reason": reason}
    log_action(
        db=db,
        action="query_blocked",
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        resource=None,
        details=details,
        ip_address=ip,
        success=False
    )


def log_access_denied(db: Session, user_id: str | None, user_email: str | None, user_role: str | None, resource: str | None, reason: str, ip: str | None) -> None:
    """Convenience log wrapper for RBAC / general access denials."""
    details = {"reason": reason}
    log_action(
        db=db,
        action="access_denied",
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        resource=resource,
        details=details,
        ip_address=ip,
        success=False
    )
