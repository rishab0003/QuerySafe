"""
dashboard.py — Auto dashboard chart config generation for QuerySafe.

Given a natural-language request like "Create monthly sales dashboard",
generates 2–4 Recharts-compatible chart configurations with valid read-only
SQL queries.  Each chart config is validated to ensure it only contains
SELECT statements before being returned to the frontend.
"""

import json
import re
from typing import Any

from ai.pipeline import get_llm

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except Exception:
    class HumanMessage:
        def __init__(self, content):
            self.content = content


    class SystemMessage:
        def __init__(self, content):
            self.content = content


# ---------------------------------------------------------------------------
# Role-to-tables access map (mirrors pipeline.py RBAC rules)
# ---------------------------------------------------------------------------
ROLE_TABLE_ACCESS: dict[str, list[str]] = {
    "hr": ["employees", "departments", "payroll"],
    "sales": ["customers", "orders", "products", "leads", "sales"],
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


def _chart_spec(
    chart_type: str,
    title: str,
    sql: str,
    x_axis: str,
    y_axis: str,
    color: str,
    description: str,
) -> dict[str, str]:
    return {
        "type": chart_type,
        "title": title,
        "sql": sql,
        "x_axis": x_axis,
        "y_axis": y_axis,
        "color": color,
        "description": description,
    }


def _fallback_dashboard_config(user_prompt: str, schema_context: list[dict], role: str) -> dict[str, Any]:
    prompt = user_prompt.lower()
    role_lower = role.lower()

    def charts_for_sales() -> list[dict[str, str]]:
        charts: list[dict[str, str]] = []
        if any(keyword in prompt for keyword in ("city", "location", "branch")):
            group_col = "city" if "city" in prompt or "location" in prompt else "branch"
            charts.append(_chart_spec(
                "BarChart",
                f"Revenue by {group_col.title()}",
                f"SELECT {group_col}, SUM(total_price) AS revenue FROM sales GROUP BY {group_col} ORDER BY revenue DESC LIMIT 10;",
                group_col,
                "revenue",
                _CHART_COLORS[0],
                f"Compares sales revenue across {group_col}s.",
            ))
        else:
            charts.append(_chart_spec(
                "BarChart",
                "Revenue by City",
                "SELECT city, SUM(total_price) AS revenue FROM sales GROUP BY city ORDER BY revenue DESC LIMIT 10;",
                "city",
                "revenue",
                _CHART_COLORS[0],
                "Compares sales revenue across cities.",
            ))

        charts.append(_chart_spec(
            "PieChart",
            "Revenue by Product Category",
            "SELECT product_category, SUM(total_price) AS revenue FROM sales GROUP BY product_category ORDER BY revenue DESC LIMIT 8;",
            "product_category",
            "revenue",
            _CHART_COLORS[1],
            "Shows which product categories contribute most to revenue.",
        ))
        charts.append(_chart_spec(
            "BarChart",
            "Orders by Customer Type",
            "SELECT customer_type, COUNT(*) AS order_count FROM sales GROUP BY customer_type ORDER BY order_count DESC LIMIT 10;",
            "customer_type",
            "order_count",
            _CHART_COLORS[2],
            "Breaks down order volume by customer segment.",
        ))
        return charts[:4]

    def charts_for_finance() -> list[dict[str, str]]:
        return [
            _chart_spec(
                "BarChart",
                "Expenses by Category",
                "SELECT category, SUM(amount) AS total_amount FROM expenses GROUP BY category ORDER BY total_amount DESC LIMIT 10;",
                "category",
                "total_amount",
                _CHART_COLORS[0],
                "Shows where the organization spends the most.",
            ),
            _chart_spec(
                "PieChart",
                "Invoice Status Mix",
                "SELECT status, COUNT(*) AS invoice_count FROM invoices GROUP BY status ORDER BY invoice_count DESC LIMIT 10;",
                "status",
                "invoice_count",
                _CHART_COLORS[1],
                "Shows how invoices are distributed by status.",
            ),
            _chart_spec(
                "BarChart",
                "Budget by Department",
                "SELECT department, SUM(amount) AS budget_total FROM budgets GROUP BY department ORDER BY budget_total DESC LIMIT 10;",
                "department",
                "budget_total",
                _CHART_COLORS[2],
                "Compares budget allocation across departments.",
            ),
        ]

    def charts_for_support() -> list[dict[str, str]]:
        return [
            _chart_spec(
                "BarChart",
                "Tickets by Status",
                "SELECT status, COUNT(*) AS ticket_count FROM tickets GROUP BY status ORDER BY ticket_count DESC LIMIT 10;",
                "status",
                "ticket_count",
                _CHART_COLORS[0],
                "Shows the current support workload by ticket status.",
            ),
            _chart_spec(
                "BarChart",
                "Users by Role",
                "SELECT role, COUNT(*) AS user_count FROM users GROUP BY role ORDER BY user_count DESC LIMIT 10;",
                "role",
                "user_count",
                _CHART_COLORS[1],
                "Highlights the distribution of user roles.",
            ),
            _chart_spec(
                "PieChart",
                "Responses by Ticket",
                "SELECT ticket_id, COUNT(*) AS response_count FROM responses GROUP BY ticket_id ORDER BY response_count DESC LIMIT 10;",
                "ticket_id",
                "response_count",
                _CHART_COLORS[2],
                "Shows which tickets are driving the most back-and-forth.",
            ),
        ]

    def charts_for_hr() -> list[dict[str, str]]:
        return [
            _chart_spec(
                "BarChart",
                "Employees by Department",
                "SELECT department, COUNT(*) AS headcount FROM employees GROUP BY department ORDER BY headcount DESC LIMIT 10;",
                "department",
                "headcount",
                _CHART_COLORS[0],
                "Shows how headcount is distributed across departments.",
            ),
            _chart_spec(
                "BarChart",
                "Departments",
                "SELECT name, COUNT(*) AS department_count FROM departments GROUP BY name ORDER BY department_count DESC LIMIT 10;",
                "name",
                "department_count",
                _CHART_COLORS[1],
                "Lists the active departments in the organization.",
            ),
            _chart_spec(
                "PieChart",
                "Payroll by Employee",
                "SELECT employee_id, SUM(salary) AS total_salary FROM payroll GROUP BY employee_id ORDER BY total_salary DESC LIMIT 10;",
                "employee_id",
                "total_salary",
                _CHART_COLORS[2],
                "Shows payroll concentration by employee.",
            ),
        ]

    if role_lower == "finance" or any(table.get("table_name") in {"invoices", "expenses", "budgets", "transactions"} for table in schema_context):
        charts = charts_for_finance()
    elif role_lower == "support" or any(table.get("table_name") in {"tickets", "users", "responses"} for table in schema_context):
        charts = charts_for_support()
    elif role_lower == "hr" or any(table.get("table_name") in {"employees", "departments", "payroll"} for table in schema_context):
        charts = charts_for_hr()
    else:
        charts = charts_for_sales()

    return {"charts": charts[:4]}


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

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Generate the dashboard configuration for: {user_prompt}\n"
                "Respond with ONLY the JSON object."
            )
        ),
    ]

    try:
        response = llm.invoke(messages)
        raw_content = response.content if hasattr(response, "content") else str(response)

        # Extract and parse JSON
        json_str = _extract_json_from_response(raw_content)
        config = json.loads(json_str)
    except Exception:
        config = _fallback_dashboard_config(user_prompt, schema_context, role)

    # Validate structure
    if "charts" not in config or not isinstance(config["charts"], list):
        config = _fallback_dashboard_config(user_prompt, schema_context, role)

    # Filter out any charts with unsafe SQL
    safe_charts = []
    for i, chart in enumerate(config["charts"]):
        sql = chart.get("sql", "")
        if _validate_chart_sql(sql):
            # Ensure the chart only references tables that exist in the provided schema_context
            # Build a set of available tables from schema_context (lowercased)
            available_tables = {t.get("table_name", "").lower() for t in schema_context or []}

            # If no schema_context is provided, allow the chart (fallbacks will be safe)
            if available_tables:
                # Extract referenced tables using a simple FROM/JOIN regex
                referenced = {
                    m.lower()
                    for m in re.findall(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_\.\"`']+)", sql, flags=re.IGNORECASE)
                }
                # Normalize referenced names (strip schema, quotes)
                normalized = set()
                for r in referenced:
                    clean = r.replace('`', '').replace('"', '').replace("'", "")
                    if '.' in clean:
                        clean = clean.split('.')[-1]
                    normalized.add(clean.lower())

                # If any referenced table is not in available_tables, skip this chart
                if not normalized.issubset(available_tables):
                    continue

            # Ensure color is present; assign from palette if missing
            if not chart.get("color"):
                chart["color"] = _CHART_COLORS[i % len(_CHART_COLORS)]
            safe_charts.append(chart)

    if not safe_charts:
        safe_charts = _fallback_dashboard_config(user_prompt, schema_context, role)["charts"]
        safe_charts = [chart for chart in safe_charts if _validate_chart_sql(chart.get("sql", ""))]

    if not safe_charts:
        raise ValueError(
            "Dashboard generation produced no charts with valid SELECT statements."
        )

    return {"charts": safe_charts}
