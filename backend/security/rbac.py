"""
security/rbac.py — Role-Based Access Control and Table/Column restrictions.
QuerySafe — Person 2: Security & Auth
"""

import re
from fastapi import HTTPException, status

# ---------------------------------------------------------------------------
# Access Maps
# ---------------------------------------------------------------------------

ROLE_TABLE_ACCESS = {
    "admin": ["*"],  # Wildcard allows all tables
    "hr": ["employees", "departments", "payroll", "attendance", "leave_requests", "performance_reviews"],
    "finance": ["invoices", "expenses", "budgets", "transactions", "accounts", "tax_records", "vendor_payments"],
    "sales": ["customers", "orders", "products", "leads", "deals", "sales_targets", "campaigns"],
    "support": ["tickets", "responses", "knowledge_base", "users"]
}

# Restricted columns and the roles they are hidden from
RESTRICTED_COLUMNS = {
    "employees": {
        "salary": ["support", "sales"],
        "ssn": ["support", "sales", "finance"]
    },
    "payroll": {
        "bank_account": ["support", "sales"]
    },
    "customers": {
        "credit_card": ["support", "hr"]
    },
    "users": {
        "password_hash": ["admin", "hr", "finance", "sales", "support"]  # hidden from everyone
    }
}


def get_allowed_tables(role: str) -> list[str]:
    """
    Returns the list of allowed tables for a role.
    """
    return ROLE_TABLE_ACCESS.get(role, [])


def check_table_access(role: str, table_names: list[str]) -> None:
    """
    Checks if a role has access to all tables in the list.
    Raises HTTP 403 Forbidden if not authorized.
    """
    allowed_tables = get_allowed_tables(role)
    if "*" in allowed_tables:
        return

    # Normalized allowed tables
    allowed_set = set(t.lower() for t in allowed_tables)

    for table in table_names:
        if table.lower() not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is not authorized to access table '{table}'."
            )


def extract_tables_from_sql(sql: str) -> list[str]:
    """
    Extracts all table names from a SELECT statement using regex.
    Looks for table names immediately following FROM or JOIN keywords.
    """
    # Find all words after FROM or JOIN
    matches = re.findall(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)
    # Deduplicate and return
    return list(set(matches))


def check_sql_access(role: str, sql: str) -> None:
    """
    Convenience:
    1. Extracts tables from the SQL query.
    2. Verifies table-level access permissions.
    3. Checks if the query references restricted columns or uses '*' on tables with restricted columns.
    Raises HTTP 403 if unauthorized.
    """
    tables = extract_tables_from_sql(sql)
    
    # 1. Table-level validation
    check_table_access(role, tables)

    # 2. Column-level validation
    for table_name, columns in RESTRICTED_COLUMNS.items():
        # Check if this table is in the query
        is_table_queried = any(t.lower() == table_name.lower() for t in tables)
        if not is_table_queried:
            continue

        for col_name, blocked_roles in columns.items():
            if role in blocked_roles:
                # Check if the restricted column is explicitly referenced
                col_pattern = rf"\b{col_name}\b"
                if re.search(col_pattern, sql, re.IGNORECASE):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access Denied: Column '{table_name}.{col_name}' is restricted for role '{role}'."
                    )

                # Check if wildcard * is used, which would leak the restricted column
                # E.g. SELECT * FROM employees
                if "*" in sql:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access Denied: Wildcard queries on table '{table_name}' are blocked for role '{role}' due to restricted columns. Please specify columns explicitly."
                    )
