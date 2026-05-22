from __future__ import annotations

import sqlparse
from typing import Dict

from .constants import ALLOWED_STATEMENTS, MAX_QUERY_LENGTH
from .utils import normalize_sql, contains_blocked_keyword


def contains_multiple_statements(sql: str) -> bool:
    parsed = sqlparse.parse(sql)
    return len(parsed) > 1


def enforce_limit(sql: str, max_rows: int) -> str:
    s = normalize_sql(sql)
    if 'limit' in s:
        return sql
    return f"{sql.rstrip('; ')} LIMIT {max_rows};"


def validate_sql(query: str) -> Dict:
    if not query or not isinstance(query, str):
        return {"is_safe": False, "reason": "Empty or invalid query.", "blocked_keywords": []}
    if len(query) > MAX_QUERY_LENGTH:
        return {"is_safe": False, "reason": "Query too long.", "blocked_keywords": []}
    s = normalize_sql(query)
    first = s.split(' ', 1)[0]
    if first not in ALLOWED_STATEMENTS:
        return {"is_safe": False, "reason": "Non-SELECT statements are not allowed.", "blocked_keywords": [first]}
    if contains_multiple_statements(query):
        return {"is_safe": False, "reason": "Multiple statements detected.", "blocked_keywords": []}
    blocked = contains_blocked_keyword(query)
    if blocked:
        return {"is_safe": False, "reason": "Blocked keyword detected.", "blocked_keywords": blocked}
    # Passed basic checks — enforce limit later in pipeline
    return {"is_safe": True, "reason": "OK", "blocked_keywords": []}

