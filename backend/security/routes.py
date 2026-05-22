from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .sql_validator import validate_sql, enforce_limit
from .constants import MAX_QUERY_ROWS

router = APIRouter(prefix="/security", tags=["Security"])


class ValidateRequest(BaseModel):
    sql: str


class ValidateResponse(BaseModel):
    is_safe: bool
    reason: str
    blocked_keywords: list[str] = []


@router.post("/validate-sql", response_model=ValidateResponse)
async def validate_sql_endpoint(body: ValidateRequest):
    result = validate_sql(body.sql)
    if not result.get("is_safe"):
        return ValidateResponse(is_safe=False, reason=result.get("reason", "blocked"), blocked_keywords=result.get("blocked_keywords", []))
    # enforce row limit injection (call for side-effects)
    enforce_limit(body.sql, MAX_QUERY_ROWS)
    return ValidateResponse(is_safe=True, reason="OK", blocked_keywords=[])
