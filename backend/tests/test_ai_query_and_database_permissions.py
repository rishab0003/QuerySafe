from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import create_app  # noqa: E402
from ai import pipeline as ai_pipeline  # noqa: E402
from ai import dashboard as ai_dashboard  # noqa: E402
from ai import routes as ai_routes  # noqa: E402
from database import routes as database_routes  # noqa: E402


def test_ai_query_returns_expected_payload_and_uses_authenticated_role(monkeypatch):
    app = create_app()

    async def fake_current_user():
        return SimpleNamespace(role="sales")

    async def fake_fetch_schema(connection_id: str, token: str):
        return {"tables": [{"name": "orders"}]}

    def fake_run_query_pipeline(**kwargs):
        assert kwargs["role"] == "sales"
        assert kwargs["connection_id"] == "conn-1"
        return {
            "sql": "SELECT id, total FROM orders LIMIT 5;",
            "confidence": 0.97,
            "tables_used": ["orders"],
            "reasoning": "Orders are needed to answer the sales question.",
        }

    async def fake_validate_sql_safety(sql: str, token: str):
        return {"is_safe": True}

    async def fake_execute_query(connection_id: str, sql: str, token: str, role: str):
        assert role == "sales"
        assert sql == "SELECT id, total FROM orders LIMIT 5;"
        return {"rows": [{"id": 1, "total": 120.0}], "row_count": 1}

    monkeypatch.setattr(ai_routes, "get_session_history", lambda session_id: [])
    monkeypatch.setattr(ai_routes, "format_history_for_prompt", lambda history: "")
    monkeypatch.setattr(ai_routes, "save_message", lambda *args, **kwargs: None)
    monkeypatch.setattr(ai_routes, "index_schema", lambda *args, **kwargs: None)
    monkeypatch.setattr(ai_routes, "run_query_pipeline", fake_run_query_pipeline)
    monkeypatch.setattr(ai_routes, "_fetch_schema", fake_fetch_schema)
    monkeypatch.setattr(ai_routes, "_validate_sql_safety", fake_validate_sql_safety)
    monkeypatch.setattr(ai_routes, "_execute_query", fake_execute_query)

    app.dependency_overrides[ai_routes.get_current_user] = fake_current_user
    client = TestClient(app)

    response = client.post(
        "/ai/query",
        json={
            "user_prompt": "Show recent orders",
            "connection_id": "conn-1",
            "session_id": "session-1",
            "role": "admin",
        },
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["sql_generated"] == "SELECT id, total FROM orders LIMIT 5;"
    assert payload["results"] == [{"id": 1, "total": 120.0}]
    assert payload["row_count"] == 1
    assert payload["tables_used"] == ["orders"]
    assert payload["confidence_score"] == 0.97


def test_mock_pipeline_fallback_generates_useful_sales_query(monkeypatch):
    original_graph = ai_pipeline._pipeline_graph
    ai_pipeline._pipeline_graph = None
    try:
        result = ai_pipeline.run_query_pipeline(
            user_prompt="Find revenue by city from sales",
            schema_context={},
            role="sales",
            session_history="",
            connection_id="conn-1",
        )
    finally:
        ai_pipeline._pipeline_graph = original_graph

    assert result["sql"] == "SELECT city, COUNT(*) AS sales_count, SUM(total_price) AS revenue FROM sales GROUP BY city ORDER BY revenue DESC LIMIT 5;"
    assert result["tables_used"] == ["sales"]
    assert result["reasoning"].startswith("Mock pipeline: AI dependencies not installed")


def test_mock_pipeline_handles_sales_by_city_prompt(monkeypatch):
    original_graph = ai_pipeline._pipeline_graph
    ai_pipeline._pipeline_graph = None
    try:
        result = ai_pipeline.run_query_pipeline(
            user_prompt="Give me the sales by city",
            schema_context={},
            role="sales",
            session_history="",
            connection_id="conn-1",
        )
    finally:
        ai_pipeline._pipeline_graph = original_graph

    assert result["sql"] == "SELECT city, COUNT(*) AS sales_count, SUM(total_price) AS revenue FROM sales GROUP BY city ORDER BY sales_count DESC LIMIT 5;"
    assert result["tables_used"] == ["sales"]


def test_dashboard_generation_falls_back_to_valid_sales_charts(monkeypatch):
    class BadLLM:
        def invoke(self, messages):
            return type("Resp", (), {"content": "not json"})()

    monkeypatch.setattr(ai_dashboard, "get_llm", lambda: BadLLM())

    config = ai_dashboard.generate_dashboard_config(
        user_prompt="Create a sales dashboard by city",
        schema_context=[{"table_name": "sales", "description": "sales table"}],
        role="sales",
    )

    assert len(config["charts"]) >= 2
    assert all(chart["sql"].strip().upper().startswith("SELECT") for chart in config["charts"])
    assert any("city" in chart["sql"].lower() for chart in config["charts"])


def test_database_execute_allows_read_only_select_for_authorized_table(monkeypatch):
    app = create_app()

    class FakeAdapter:
        def execute_readonly(self, query: str, timeout: int = 10, limit: int = 500):
            return ([{"id": 7, "name": "Acme"}], 1, 8.25)

    monkeypatch.setattr(database_routes.db_pool, "get_connection", lambda connection_id: FakeAdapter())
    client = TestClient(app)

    response = client.post(
        "/database/execute",
        json={
            "connection_id": "conn-1",
            "sql": "SELECT id, name FROM customers LIMIT 10;",
            "role": "sales",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["row_count"] == 1
    assert payload["rows"] == [{"id": 7, "name": "Acme"}]


def test_database_execute_rejects_update_statements(monkeypatch):
    app = create_app()

    class FakeAdapter:
        def execute_readonly(self, query: str, timeout: int = 10, limit: int = 500):
            pytest.fail("execute_readonly should not be called for UPDATE statements")

    monkeypatch.setattr(database_routes.db_pool, "get_connection", lambda connection_id: FakeAdapter())
    client = TestClient(app)

    response = client.post(
        "/database/execute",
        json={
            "connection_id": "conn-1",
            "sql": "UPDATE customers SET name = 'New Name' WHERE id = 7;",
            "role": "sales",
        },
    )

    assert response.status_code == 400, response.text
    assert "read-only queries" in response.json()["detail"]