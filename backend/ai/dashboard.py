"""
dashboard.py — Auto dashboard chart config generation for QuerySafe.

Given a natural-language request like "Create monthly sales dashboard",
generates 2–4 Recharts-compatible chart configurations with valid read-only
SQL queries.  Each chart config is validated to ensure it only contains
SELECT statements before being returned to the frontend.
"""

import json
import os
import re
from typing import Any

from ai.pipeline import get_llm


# ---------------------------------------------------------------------------
# Role-to-tables access map (mirrors pipeline.py RBAC rules)
# ---------------------------------------------------------------------------
ROLE_TABLE_ACCESS: dict[str, list[str]] = {
    "hr": ["employees", "departments", "payroll"],
    "sales": ["customers", "orders", "products", "leads"],
    "finance": ["invoices", "expenses", "budgets", "transactions"],
    "support": ["tickets", "users", "responses"],
    "admin": [],  # admin has unrestricted access — no allow-list enforcement
}

# Predefined color palette for chart series
_CHART_COLORS = [
    "#6366f1",  # indigo
    "#22c55e",  # green
    "#f59e0b",  # amber
    "#ef4444",  # red
    "#06b6d4",  # cyan
    "#a855f7",  # purple
]


def _build_dashboard_system_prompt(
    user_prompt: str,
    schema_context: list[dict],
    role: str,
) -> str:
    """
    Builds a detailed system prompt that instructs the LLM to produce
    a JSON array of chart configurations for the user's dashboard request.
    """
    allowed_tables = ROLE_TABLE_ACCESS.get(role.lower(), [])
    table_restriction = (
        f"You may ONLY reference these tables: {', '.join(allowed_tables)}."
        if allowed_tables
        else "You have unrestricted read access to all tables."
    )

    schema_text = ""
    if schema_context:
        schema_lines = []
        for item in schema_context:
            schema_lines.append(
                f"  - {item.get('table_name', 'unknown')}: {item.get('description', '')}"
            )
        schema_text = "Available schema:\n" + "\n".join(schema_lines)
    else:
        schema_text = "No schema context available — infer reasonable column names."

    return f"""You are a data visualization expert for an enterprise analytics platform.
The user wants to generate a dashboard. Your job is to produce 2 to 4 chart configurations.

User request: "{user_prompt}"
User role: {role}
{table_restriction}

{schema_text}

CRITICAL RULES:
1. Every "sql" field MUST be a valid SELECT statement only.
   Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, EXEC, GRANT, or REVOKE.
2. SQL must be syntactically valid for PostgreSQL.
3. Respond ONLY with a valid JSON object — no prose, no markdown, no code fences.
4. Use the exact structure shown below.

Required JSON structure:
{{
  "charts": [
    {{
      "type": "LineChart | BarChart | PieChart | AreaChart",
      "title": "Human-readable chart title",
      "sql": "SELECT column1, column2 FROM table WHERE ... ORDER BY ...",
      "x_axis": "column_name_for_x_axis",
      "y_axis": "column_name_for_y_axis",
      "color": "#hexcode",
      "description": "One sentence describing what this chart shows"
    }}
  ]
}}

Produce exactly 2–4 charts that together give a comprehensive view of what the user asked for.
Choose appropriate chart types: use LineChart/AreaChart for time series, BarChart for comparisons,
PieChart for distributions/proportions.
Assign distinct colors from this palette: {', '.join(_CHART_COLORS)}.
"""


def _extract_json_from_response(raw: str) -> str:
    """
    Strips markdown fences and extracts the raw JSON string from an LLM response.
    Handles ```json ... ``` and ``` ... ``` wrappers.
    """
    # Remove markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    return cleaned


def _validate_chart_sql(sql: str) -> bool:
    """
    Returns True if the SQL string is a read-only SELECT statement.
    Blocks any DML/DDL keywords.
    """
    if not sql or not isinstance(sql, str):
        return False

    normalized = sql.strip().upper()

    # Must start with SELECT
    if not normalized.startswith("SELECT"):
        return False

    # Must not contain dangerous keywords
    blocked = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "TRUNCATE", "EXEC", "EXECUTE", "GRANT", "REVOKE",
        "CREATE", "REPLACE", "MERGE",
    ]
    for keyword in blocked:
        # Use word-boundary check to avoid false positives on column names
        if re.search(rf"\b{keyword}\b", normalized):
            return False

    return True


def generate_dashboard_config(
    user_prompt: str,
    schema_context: list[dict],
    role: str,
) -> dict[str, Any]:
    """
    Calls the configured LLM (OpenAI or Anthropic, set via AI_PROVIDER env)
    to generate a dashboard configuration with 2–4 Recharts chart specs.

    Each chart spec includes:
      - type: LineChart | BarChart | PieChart | AreaChart
      - title: Human-readable chart name
      - sql: A valid, read-only SELECT statement
      - x_axis / y_axis: Column names for chart axes
      - color: Hex color code
      - description: What the chart shows

    Invalid charts (non-SELECT SQL) are filtered out before returning.
    If all charts fail validation, raises a ValueError.

    Args:
        user_prompt:    The user's dashboard request in natural language
        schema_context: List of relevant table dicts from embeddings.py
        role:           The user's department role (hr/sales/finance/support/admin)

    Returns:
        Dict with "charts" key containing a list of validated chart configs
    """
    llm = get_llm()
    system_prompt = _build_dashboard_system_prompt(user_prompt, schema_context, role)

    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Generate the dashboard configuration for: {user_prompt}\n"
                "Respond with ONLY the JSON object."
            )
        ),
    ]

    response = llm.invoke(messages)
    raw_content = response.content if hasattr(response, "content") else str(response)

    # Extract and parse JSON
    json_str = _extract_json_from_response(raw_content)

    try:
        config = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON for dashboard config: {exc}\nRaw response: {raw_content[:500]}"
        ) from exc

    # Validate structure
    if "charts" not in config or not isinstance(config["charts"], list):
        raise ValueError("LLM response missing 'charts' list in dashboard config.")

    # Filter out any charts with unsafe SQL
    safe_charts = []
    for i, chart in enumerate(config["charts"]):
        sql = chart.get("sql", "")
        if _validate_chart_sql(sql):
            # Ensure color is present; assign from palette if missing
            if not chart.get("color"):
                chart["color"] = _CHART_COLORS[i % len(_CHART_COLORS)]
            safe_charts.append(chart)

    if not safe_charts:
        raise ValueError(
            "Dashboard generation produced no charts with valid SELECT statements."
        )

    return {"charts": safe_charts}
