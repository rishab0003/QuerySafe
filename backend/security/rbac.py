from __future__ import annotations

ROLE_TABLE_ACCESS: dict[str, list[str]] = {
    "hr": ["employees", "departments", "payroll"],
    "sales": ["customers", "orders", "products", "leads", "sales"],
    "finance": ["invoices", "expenses", "budgets", "transactions"],
    "support": ["tickets", "users", "responses"],
    "admin": [],
}


def check_table_access(role: str, table: str) -> bool:
    allowed = ROLE_TABLE_ACCESS.get(role.lower(), [])
    if not allowed:
        return True  # admin or unrestricted
    return table.lower() in allowed


def filter_query_tables(role: str, tables: list[str]) -> list[str]:
    return [t for t in tables if check_table_access(role, t)]

