"""
routes.py — FastAPI router for QuerySafe AI endpoints.

Exposes three endpoints consumed by Person 4 (Frontend):
  POST /ai/query     → Natural language → SQL → database results
  POST /ai/explain   → Plain-English explanation of a SQL query
  POST /ai/dashboard → Auto chart config generation for Recharts

All routes require a valid Bearer JWT issued by Person 2 (Auth service).
Internal service calls use httpx with configurable timeouts.
"""

import os
import time
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from ai.dashboard import generate_dashboard_config
from ai.embeddings import index_schema, retrieve_relevant_schema
from ai.memory import (
    format_history_for_prompt,
    get_session_history,
    save_message,
)
from ai.pipeline import run_query_pipeline

# ---------------------------------------------------------------------------
# Router & security
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/ai", tags=["AI"])
bearer_scheme = HTTPBearer()

# ---------------------------------------------------------------------------
# Internal service URLs (from env)
# ---------------------------------------------------------------------------

SECURITY_SERVICE_URL = os.getenv("SECURITY_SERVICE_URL", "http://backend:8000")
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://backend:8000")

# Timeout for internal service calls (seconds)
_INTERNAL_TIMEOUT = 15.0


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class QueryRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, max_length=2000, description="Natural language question")
    connection_id: str = Field(..., description="Active DB connection ID from Person 3")
    session_id: str = Field(..., description="User session identifier for Redis memory")
    role: str = Field(default="viewer", description="User department role: hr|sales|finance|support|admin")


class QueryResponse(BaseModel):
    sql_generated: str
    results: list[Any]
    confidence_score: float
    tables_used: list[str]
    reasoning: str
    row_count: int
    truncated: bool = False
    query_time_ms: float = 0.0


class ExplainRequest(BaseModel):
    sql: str = Field(..., min_length=1, description="The SQL query to explain")
    user_prompt: str = Field(default="", description="The original natural language question")


class ExplainResponse(BaseModel):
    explanation: str
    why_these_tables: str
    assumptions_made: str


class DashboardRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, max_length=2000)
    connection_id: str
    role: str = Field(default="viewer")


class DashboardResponse(BaseModel):
    charts: list[dict]


# ---------------------------------------------------------------------------
# Internal service helpers
# ---------------------------------------------------------------------------


async def _validate_sql_safety(sql: str, token: str) -> dict:
    """
    Calls Person 2's POST /security/validate-sql endpoint.
    Returns { is_safe: bool, reason: str, blocked_keywords: list }.
    Raises HTTPException on service errors.
    """
    async with httpx.AsyncClient(timeout=_INTERNAL_TIMEOUT) as client:
        try:
            resp = await client.post(
                f"{SECURITY_SERVICE_URL}/security/validate-sql",
                json={"sql": sql},
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Security service returned {exc.response.status_code}: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Security service unavailable: {exc}",
            ) from exc


async def _fetch_schema(connection_id: str, token: str) -> dict:
    """
    Calls Person 3's GET /database/schema/{connection_id} endpoint.
    Returns the schema dict with a 'tables' key.
    Raises HTTPException on service errors.
    """
    async with httpx.AsyncClient(timeout=_INTERNAL_TIMEOUT) as client:
        try:
            resp = await client.get(
                f"{DATABASE_SERVICE_URL}/database/schema/{connection_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Database service returned {exc.response.status_code}: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database service unavailable: {exc}",
            ) from exc


async def _execute_query(connection_id: str, sql: str, token: str) -> dict:
    """
    Calls Person 3's POST /database/execute endpoint.
    Returns { rows: list, metadata: dict }.
    Raises HTTPException on service errors.
    """
    async with httpx.AsyncClient(timeout=_INTERNAL_TIMEOUT) as client:
        try:
            resp = await client.post(
                f"{DATABASE_SERVICE_URL}/database/execute",
                json={"connection_id": connection_id, "sql": sql},
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Database execute returned {exc.response.status_code}: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database service unavailable: {exc}",
            ) from exc


# ---------------------------------------------------------------------------
# GET /ai/health  (lightweight health check, no auth required)
# ---------------------------------------------------------------------------


@router.get("/health", include_in_schema=True)
async def ai_health():
    """Health check for the AI module."""
    return {"status": "ok", "module": "ai"}


# ---------------------------------------------------------------------------
# POST /ai/query
# ---------------------------------------------------------------------------


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Natural language → SQL → database results",
    description=(
        "Converts a plain-English question into a safe SELECT query, validates it "
        "through the security service, executes it against the user's database, "
        "and returns structured results with full explainability metadata."
    ),
)
async def query_endpoint(
    body: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> QueryResponse:
    token = credentials.credentials
    start_time = time.perf_counter()

    # ── Step 1: Load Redis session memory ──────────────────────────────────
    history_list = get_session_history(body.session_id)
    session_history_str = format_history_for_prompt(history_list)

    # ── Step 2: Fetch schema from Database service ──────────────────────────
    schema = await _fetch_schema(body.connection_id, token)

    # Opportunistically index schema into ChromaDB (idempotent upsert)
    try:
        index_schema(body.connection_id, schema)
    except Exception:
        pass  # Non-fatal: ChromaDB indexing failure doesn't block query

    # ── Step 3: Run LangGraph AI pipeline ──────────────────────────────────
    pipeline_result = run_query_pipeline(
        user_prompt=body.user_prompt,
        schema_context=schema,
        role=body.role,
        session_history=session_history_str,
        connection_id=body.connection_id,
    )

    # If pipeline detected an unsafe intent, abort immediately
    if pipeline_result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pipeline_result["error"],
        )

    generated_sql = pipeline_result["sql"]

    # ── Step 4: Validate SQL safety via Security service ───────────────────
    safety_result = await _validate_sql_safety(generated_sql, token)

    if not safety_result.get("is_safe", False):
        blocked = safety_result.get("blocked_keywords", [])
        reason = safety_result.get("reason", "SQL failed safety validation.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": reason,
                "blocked_keywords": blocked,
                "sql_generated": generated_sql,
            },
        )

    # ── Step 5: Execute validated SQL against the database ─────────────────
    execution_result = await _execute_query(body.connection_id, generated_sql, token)

    raw_rows: list = execution_result.get("rows", [])

    # ── Step 6: Save conversation to Redis session memory ──────────────────
    save_message(body.session_id, "user", body.user_prompt)
    save_message(
        body.session_id,
        "assistant",
        f"Generated SQL: {generated_sql}\nReturned {len(raw_rows)} rows.",
    )

    # ── Step 7: Build and return response ──────────────────────────────────
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    truncated = len(raw_rows) > 500
    results = raw_rows[:500] if truncated else raw_rows

    return QueryResponse(
        sql_generated=generated_sql,
        results=results,
        confidence_score=pipeline_result["confidence"],
        tables_used=pipeline_result["tables_used"],
        reasoning=pipeline_result["reasoning"],
        row_count=len(results),
        truncated=truncated,
        query_time_ms=elapsed_ms,
    )


# ---------------------------------------------------------------------------
# POST /ai/explain
# ---------------------------------------------------------------------------

_EXPLAIN_SYSTEM_PROMPT = """You are a database expert who helps non-technical employees understand SQL queries.
Your audience has no SQL knowledge — explain clearly, concisely, and in plain English.

Given a SQL query and the user's original question, respond with ONLY a JSON object with these three fields:
{
  "explanation": "A clear 2–3 sentence explanation of what the query does in plain English.",
  "why_these_tables": "Explain why these specific tables were queried and what data they contain.",
  "assumptions_made": "List any assumptions the query makes about the data or the user's intent."
}

Do not include any text outside the JSON object.
"""


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Explain a SQL query in plain English",
    description=(
        "Takes a generated SQL query and the user's original question, then uses "
        "the LLM to produce a non-technical explanation of what the query does, "
        "why specific tables were chosen, and what assumptions were made."
    ),
)
async def explain_endpoint(
    body: ExplainRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> ExplainResponse:
    from ai.pipeline import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    import json

    llm = get_llm()

    user_content = (
        f"SQL Query:\n{body.sql}\n\n"
        f"User's original question: {body.user_prompt or 'Not provided'}"
    )

    messages = [
        SystemMessage(content=_EXPLAIN_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    raw = response.content if hasattr(response, "content") else str(response)

    # Strip markdown fences if present
    import re
    cleaned = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: return the raw text as explanation
        return ExplainResponse(
            explanation=raw.strip(),
            why_these_tables="Unable to parse structured response from AI.",
            assumptions_made="Response format was unexpected.",
        )

    return ExplainResponse(
        explanation=parsed.get("explanation", "No explanation available."),
        why_these_tables=parsed.get("why_these_tables", "Not specified."),
        assumptions_made=parsed.get("assumptions_made", "None specified."),
    )


# ---------------------------------------------------------------------------
# POST /ai/dashboard
# ---------------------------------------------------------------------------


@router.post(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Generate Recharts dashboard config from natural language",
    description=(
        "Converts a natural-language dashboard request into 2–4 Recharts chart "
        "configurations, each with a valid read-only SQL query, axes config, "
        "color, and description. The frontend (Person 4) renders these directly."
    ),
)
async def dashboard_endpoint(
    body: DashboardRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> DashboardResponse:
    token = credentials.credentials

    # Fetch schema for context
    schema = await _fetch_schema(body.connection_id, token)

    # Opportunistically index schema into ChromaDB
    try:
        index_schema(body.connection_id, schema)
    except Exception:
        pass

    # Retrieve most relevant tables for the dashboard request
    relevant_schema = retrieve_relevant_schema(
        body.connection_id, body.user_prompt, top_k=8
    )

    # If ChromaDB has no data yet, fall back to raw schema tables
    if not relevant_schema:
        tables = schema.get("tables", [])
        relevant_schema = [
            {
                "table_name": t.get("name", "unknown"),
                "description": (
                    f"Table {t.get('name', 'unknown')} has columns: "
                    + ", ".join(
                        f"{c.get('name')} ({c.get('type')})"
                        for c in t.get("columns", [])
                    )
                ),
                "metadata": {},
            }
            for t in tables[:8]
        ]

    try:
        config = generate_dashboard_config(
            user_prompt=body.user_prompt,
            schema_context=relevant_schema,
            role=body.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DashboardResponse(charts=config["charts"])
