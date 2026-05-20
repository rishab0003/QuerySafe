"""
security/routes.py — Security API routes.
QuerySafe — Person 2: Security & Auth
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.models import get_db
from security.sql_validator import validate_sql
from security.audit import log_action

router = APIRouter(prefix="/security", tags=["Security"])


class ValidateSQLRequest(BaseModel):
    sql: str


class ValidateSQLResponse(BaseModel):
    is_safe: bool
    reason: str
    cleaned_sql: str
    blocked_keywords: list[str]


@router.post("/validate-sql", response_model=ValidateSQLResponse)
def validate_sql_endpoint(
    request: Request,
    body: ValidateSQLRequest,
    db: Session = Depends(get_db)
):
    """
    Validate an AI-generated SQL statement before executing it.
    Only allows read-only SELECT statements, restricts stacked queries, 
    scans for prompt injection, walks the AST, and enforces a maximum LIMIT of 500.
    """
    result = validate_sql(body.sql)
    
    # Log the action in the database audit logs
    action = "sql_validation_success" if result["is_safe"] else "sql_validation_blocked"
    
    log_action(
        db=db,
        action=action,
        user_id=None,  # This can be called anonymously by AI agent / other services
        user_email=None,
        user_role=None,
        resource="sql_validator",
        details={
            "original_sql": body.sql,
            "cleaned_sql": result["cleaned_sql"],
            "reason": result["reason"],
            "blocked_keywords": result["blocked_keywords"]
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=result["is_safe"]
    )
    
    return ValidateSQLResponse(
        is_safe=result["is_safe"],
        reason=result["reason"],
        cleaned_sql=result["cleaned_sql"],
        blocked_keywords=result["blocked_keywords"]
    )
