from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

logger = logging.getLogger("querysafe.audit")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def log_event(user_id: str | None, action: str, ip: str | None = None, metadata: dict | None = None) -> None:
    payload = {
        "timestamp": _now_iso(),
        "user_id": user_id,
        "action": action,
        "ip": ip,
        "metadata": metadata or {},
    }
    logger.info("AUDIT %s", json.dumps(payload))


def log_security_violation(user_id: str | None, code: str, reason: str, ip: str | None = None, metadata: dict | None = None) -> None:
    payload = {
        "timestamp": _now_iso(),
        "user_id": user_id,
        "code": code,
        "reason": reason,
        "ip": ip,
        "metadata": metadata or {},
    }
    logger.warning("SEC_VIOLATION %s", json.dumps(payload))


def log_query_execution(user_id: str | None, sql: str, tables: list[str], row_count: int, ip: str | None = None) -> None:
    payload = {
        "timestamp": _now_iso(),
        "user_id": user_id,
        "sql": sql,
        "tables": tables,
        "row_count": row_count,
        "ip": ip,
    }
    logger.info("QUERY %s", json.dumps(payload))

