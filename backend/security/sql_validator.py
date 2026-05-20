"""
security/sql_validator.py — The SQL Safety Engine.
QuerySafe — Person 2: Security & Auth
"""

import re
import sqlparse

BLOCKED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "EXEC", "EXECUTE", "GRANT", "REVOKE", "MERGE",
    "REPLACE", "UPSERT", "CALL", "LOAD", "IMPORT"
}

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:previous|the)?\s*instruction",
    r"override\s+(?:security|rule)",
    r"system\s*prompt",
    r"union\s+select",
    r"\bpg_sleep\b",
    r"\bdelay\b",
    r"\bxp_cmdshell\b"
]


def enforce_limit(sql: str) -> str:
    """
    Enforce LIMIT 500. Add LIMIT 500 if missing, reduce if higher than 500.
    """
    # Clean SQL string and strip trailing semicolons for modification
    cleaned_sql = sql.strip().rstrip(";")
    
    # Regex to find LIMIT followed by an integer
    limit_match = re.search(r"\bLIMIT\s+(\d+)\b", cleaned_sql, re.IGNORECASE)
    
    if limit_match:
        limit_val = int(limit_match.group(1))
        if limit_val > 500:
            cleaned_sql = re.sub(r"\bLIMIT\s+\d+\b", "LIMIT 500", cleaned_sql, flags=re.IGNORECASE)
    else:
        # Check if there is an OFFSET, append LIMIT 500 before or just at the end.
        cleaned_sql = f"{cleaned_sql} LIMIT 500"
        
    return cleaned_sql + ";"


def walk_tokens(tokens) -> list[str]:
    """
    Recursively traverse sqlparse tokens to check if any blocked keyword or DDL/DML appears.
    """
    blocked_found = []
    for token in tokens:
        if token.is_group:
            blocked_found.extend(walk_tokens(token.tokens))
        else:
            val_upper = token.value.upper()
            if val_upper in BLOCKED_KEYWORDS:
                blocked_found.append(val_upper)
            elif token.ttype in [sqlparse.tokens.Keyword.DDL, sqlparse.tokens.Keyword.DML]:
                # Allow SELECT, but block other DDL/DML operations
                if val_upper not in ["SELECT", "FROM", "WHERE", "JOIN", "ON", "GROUP", "ORDER", "BY", "HAVING", "LIMIT", "OFFSET"]:
                    if val_upper in BLOCKED_KEYWORDS:
                        blocked_found.append(val_upper)
    return blocked_found


def validate_sql(sql: str) -> dict:
    """
    Validate every AI-generated query against security rules.
    Steps:
    1. Reject if query length > 2000 chars.
    2. Regex scan for prompt injection patterns.
    3. Keyword blocklist scan on uppercase words.
    4. Parse with sqlparse — confirm statement.get_type() == 'SELECT'.
    5. Walk AST tokens — reject any DDL or blocked DML tokens.
    6. Reject if more than 1 statement (stacked queries).
    7. Enforce LIMIT 500 — add if missing, reduce if higher.
    """
    if not sql or not sql.strip():
        return {
            "is_safe": False,
            "reason": "Empty SQL query.",
            "cleaned_sql": "",
            "blocked_keywords": []
        }

    # Step 1: Query length check
    if len(sql) > 2000:
        return {
            "is_safe": False,
            "reason": "Query exceeds maximum length of 2000 characters.",
            "cleaned_sql": "",
            "blocked_keywords": []
        }

    # Step 2: Prompt Injection Regex scan
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return {
                "is_safe": False,
                "reason": "Potential prompt injection or suspicious pattern detected.",
                "cleaned_sql": "",
                "blocked_keywords": []
            }

    # Step 3: Standalone word blocklist check
    found_blocked = []
    for keyword in BLOCKED_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, sql, re.IGNORECASE):
            found_blocked.append(keyword)

    if found_blocked:
        return {
            "is_safe": False,
            "reason": "Query contains unauthorized or dangerous keywords.",
            "cleaned_sql": "",
            "blocked_keywords": found_blocked
        }

    # Step 4 & 6: Stacked queries check (more than 1 statement)
    parsed = sqlparse.parse(sql)
    if len(parsed) != 1:
        return {
            "is_safe": False,
            "reason": "Multiple or stacked queries are not allowed.",
            "cleaned_sql": "",
            "blocked_keywords": []
        }

    statement = parsed[0]

    # Confirm it's a SELECT statement
    if statement.get_type() != "SELECT":
        return {
            "is_safe": False,
            "reason": f"Only read-only SELECT statements are allowed. Got {statement.get_type()}.",
            "cleaned_sql": "",
            "blocked_keywords": []
        }

    # Step 5: Walk AST tokens recursively
    ast_blocked = walk_tokens(statement.tokens)
    if ast_blocked:
        return {
            "is_safe": False,
            "reason": "Query contains unauthorized terms in the Abstract Syntax Tree.",
            "cleaned_sql": "",
            "blocked_keywords": list(set(ast_blocked))
        }

    # Step 7: Enforce LIMIT 500
    cleaned_sql = enforce_limit(sql)

    return {
        "is_safe": True,
        "reason": "Query passed all safety checks.",
        "cleaned_sql": cleaned_sql,
        "blocked_keywords": []
    }
