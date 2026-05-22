from __future__ import annotations

import re
from typing import List

JAILBREAK_PATTERNS = [
    r"ignore previous instructions",
    r"reveal system prompt",
    r"bypass security",
    r"act as admin",
    r"delete database",
    r"or\s+1=1",
    r"union\s+select",
    r"--",
    r"xp_cmdshell",
]


def detect_prompt_injection(text: str) -> dict:
    hits: List[str] = []
    lowered = text.lower()
    for p in JAILBREAK_PATTERNS:
        if re.search(p, lowered):
            hits.append(p)
    return {"injection": bool(hits), "patterns": hits}

