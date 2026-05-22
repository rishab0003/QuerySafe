from __future__ import annotations

import re
from typing import List

def detects_full_table_scan(sql: str) -> bool:
    s = sql.lower()
    if "select *" in s and "where" not in s:
        return True
    return False


def detects_sensitive_column_access(sql: str) -> List[str]:
    s = sql.lower()
    hits = []
    for col in ("password", "secret", "ssn", "credit_card"):
        if re.search(rf"\b{col}\b", s):
            hits.append(col)
    return hits

