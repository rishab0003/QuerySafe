from __future__ import annotations

import re

from .constants import BLOCKED_KEYWORDS


def normalize_sql(sql: str) -> str:
    return re.sub(r'\s+', ' ', sql.strip()).lower()


def contains_blocked_keyword(sql: str) -> list[str]:
    s = normalize_sql(sql)
    found = [kw for kw in BLOCKED_KEYWORDS if kw in s]
    return found

