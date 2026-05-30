"""
routes.py — FastAPI endpoints for multi-database management.
"""

import logging
import re
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database.pool import db_pool
from database.schema_indexer import get_database_schema

logger = logging.getLogger("querysafe.database.routes")

router = APIRouter(
    prefix="/database",
    tags=["Database"],
)

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------


class DBConnectRequest(BaseModel):
    """
    Request model for connecting to a database.
    """
    type: str = Field(..., description="Database type: 'postgres', 'mysql', or 'mongodb'")
    host: str = Field(..., description="Database server host address")
    port: int = Field(..., description="Database port number")
    user: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    database: str = Field(..., description="Database name")
    allow_write: bool = Field(default=False, description="Whether to allow data modification queries (UPDATE, INSERT, DELETE, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "user": "postgres",
                "password": "my-secret-password",
                "database": "employees_db"
            }
        }


class DBConnectResponse(BaseModel):
    """
    Response model for a successful database connection.
    """
    connection_id: str = Field(..., description="Unique UUID for the connection session")
    status: str = Field("connected", description="Connection status indicator")


class QueryExecuteRequest(BaseModel):
    """
    Request model for executing queries with role authorization.
    """
    connection_id: str = Field(..., description="UUID of the active connection session")
    sql: str = Field(..., description="SQL-like query to execute")
    role: str = Field(..., description="User role to enforce RBAC row-level checks (hr, finance, sales, support)")

    class Config:
        json_schema_extra = {
            "example": {
                "connection_id": "8ba8c1a6-5fa9-43c2-bfbe-d88e7b165b4c",
                "sql": "SELECT name, salary FROM employees WHERE salary > 50000 LIMIT 10",
                "role": "hr"
            }
        }


class QueryExecuteResponse(BaseModel):
    """
    Response model containing rows, row count, and execution performance metrics.
    """
    rows: List[Dict[str, Any]] = Field(..., description="List of dict rows returned by the query")
    row_count: int = Field(..., description="Number of rows returned (capped at 500)")
    execution_time_ms: float = Field(..., description="Time taken to execute the query in milliseconds")


class DBDisconnectResponse(BaseModel):
    """
    Response model for cleanly closing and removing a connection.
    """
    connection_id: str = Field(..., description="UUID of the disconnected session")
    status: str = Field("disconnected", description="Disconnection status indicator")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# RBAC Table Access Mappings
ROLE_ALLOWED_TABLES = {
    "hr": {"employees", "departments", "payroll"},
    "finance": {"invoices", "expenses", "budgets", "transactions", "sales"},
    "sales": {"customers", "orders", "products", "leads", "sales"},
    "support": {"tickets", "users", "responses"}
}


def is_read_only_query(sql: str) -> bool:
    """
    Verify that the SQL query is strictly a read-only SELECT/SHOW/EXPLAIN/DESCRIBE query.
    Removes comments and searches for destructive mutating keywords.
    """
    # Remove inline (-- comment) and block (/* comment */) SQL comments
    cleaned = re.sub(r"(--.*?$)|(/\*.*?\*/)", "", sql, flags=re.MULTILINE | re.DOTALL)
    cleaned = cleaned.strip()

    # Must start with SELECT, SHOW, EXPLAIN, or DESCRIBE
    if not re.match(r"^(SELECT|SHOW|EXPLAIN|DESCRIBE)\b", cleaned, re.IGNORECASE):
        return False

    # Check for mutating SQL keywords (enforce word boundaries to avoid false matches)
    mutating_keywords = [
        r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b", r"\bCREATE\b",
        r"\bALTER\b", r"\bREPLACE\b", r"\bTRUNCATE\b", r"\bGRANT\b", r"\bREVOKE\b",
        r"\bINTO\b", r"\bUPSERT\b"
    ]
    for keyword in mutating_keywords:
        if re.search(keyword, cleaned, re.IGNORECASE):
            return False

    return True


def extract_tables_from_sql(sql: str) -> set[str]:
    """
    Parse SQL statement to extract all target table/collection names referenced in FROM or JOIN.
    """
    # Remove comments and collapse spaces
    cleaned = re.sub(r"(--.*?$)|(/\*.*?\*/)", "", sql, flags=re.MULTILINE | re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned.strip())

    # Regular expression to extract tables following FROM or JOIN
    pattern = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_\.\"`']+)", re.IGNORECASE)
    matches = pattern.findall(cleaned)

    tables = set()
    for match in matches:
        # Strip brackets, backticks, double/single quotes, and schema prefix if present
        clean_name = match.replace("`", "").replace('"', "").replace("'", "").strip()
        if "." in clean_name:
            clean_name = clean_name.split(".")[-1]
        
        # Strip subquery parenthesis if any
        if clean_name.startswith("("):
            clean_name = clean_name[1:]
        if clean_name.endswith(")"):
            clean_name = clean_name[:-1]
            
        if clean_name:
            tables.add(clean_name.lower())

    return tables


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------


@router.post("/connect", response_model=DBConnectResponse, summary="Establish a new connection")
async def connect_database(request: DBConnectRequest):
    """
    Test connectivity, AES-256 encrypt credentials, register in Redis, and return a unique connection_id.
    """
    logger.info(f"Received connect request for DB type: {request.type}")
    try:
        config = request.model_dump()
        connection_id = db_pool.connect_database(config)
        return DBConnectResponse(connection_id=connection_id)
    except Exception as exc:
        logger.error(f"Error establishing database connection: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database connection failed: {str(exc)}"
        )


@router.get("/schema/{connection_id}", response_model=Dict[str, Any], summary="Get structured schema")
async def get_schema(connection_id: str):
    """
    Retrieve structured table, columns, types, and foreign keys JSON metadata for indexers.
    """
    logger.info(f"Received schema request for ID: {connection_id}")
    try:
        schema = get_database_schema(connection_id)
        return schema
    except Exception as exc:
        logger.error(f"Error retrieving database schema: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to fetch schema: {str(exc)}"
        )


@router.post("/execute", response_model=QueryExecuteResponse, summary="Execute a read-only query")
async def execute_query(request: QueryExecuteRequest):
    """
    Validate SELECT-only statement, perform RBAC check on tables based on role, execute query, and return results.
    """
    logger.info(f"Received execute request for connection: {request.connection_id}, role: {request.role}")
    
    # 1. Retrieve connection adapter first to inspect connection configurations
    try:
        adapter = db_pool.get_connection(request.connection_id)
    except Exception as exc:
        logger.error(f"Error fetching connection from pool: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database connection not found: {str(exc)}"
        )

    role_key = request.role.strip().lower()
    
    # Check if the connection allows write operations
    allow_write = False
    if hasattr(adapter, "_config") and adapter._config:
        allow_write = adapter._config.get("allow_write", False)

    # 2. Enforce strict read-only SELECT-only syntax unless it is admin and connection has write access
    if not (role_key == "admin" and allow_write):
        if not is_read_only_query(request.sql):
            logger.warning(f"Rejected non-read-only query: '{request.sql}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forbidden query: QuerySafe only executes read-only queries (e.g. SELECT, SHOW, EXPLAIN, DESCRIBE)."
            )

    # 3. RBAC access control check (admin has unrestricted access)
    if role_key != "admin":
        if role_key not in ROLE_ALLOWED_TABLES:
            logger.warning(f"Rejected query due to unrecognized role: '{request.role}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Unrecognized or unauthorized role '{request.role}'."
            )

        allowed_tables = ROLE_ALLOWED_TABLES[role_key]
        queried_tables = extract_tables_from_sql(request.sql)

        # Check for unauthorized table access
        unauthorized_tables = queried_tables - allowed_tables
        if unauthorized_tables:
            logger.warning(f"RBAC Blocked role '{request.role}' from accessing tables: {unauthorized_tables}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied: Role '{request.role}' is not authorized to access "
                    f"tables: {list(unauthorized_tables)}. Allowed tables are: {list(allowed_tables)}."
                )
            )

        # Verify referenced tables actually exist in the target database schema
        try:
            schema = get_database_schema(request.connection_id)
            existing_tables = {t.get("table_name", "").lower() for t in schema.get("tables", [])}
            missing_tables = {t for t in queried_tables if t not in existing_tables}
            if missing_tables:
                logger.warning(f"Query references missing tables for connection {request.connection_id}: {missing_tables}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(f"Query references tables not present in the database: {list(missing_tables)}.")
                )
        except HTTPException:
            # Re-raise HTTP exceptions (e.g., schema fetch failure)
            raise
        except Exception as exc:
            logger.error(f"Failed to validate referenced tables for connection {request.connection_id}: {exc}", exc_info=True)
            # If we cannot fetch schema for some reason, continue and let execution attempt to run (will surface DB error)
            existing_tables = set()

    # 4. Execute query through the adapter under strict limits
    try:
        rows, row_count, execution_time_ms = adapter.execute_readonly(
            query=request.sql,
            timeout=10,  # 10s query timeout constraint
            limit=500    # Max 500 rows constraint
        )
        return QueryExecuteResponse(
            rows=rows,
            row_count=row_count,
            execution_time_ms=execution_time_ms
        )
    except Exception as exc:
        logger.error(f"Error executing query: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(exc)}"
        )


@router.delete("/disconnect/{connection_id}", response_model=DBDisconnectResponse, summary="Disconnect database session")
async def disconnect_database(connection_id: str):
    """
    Cleanly close database sockets, remove metadata from Redis and active adapter caches.
    """
    logger.info(f"Received disconnect request for ID: {connection_id}")
    try:
        db_pool.disconnect_database(connection_id)
        return DBDisconnectResponse(connection_id=connection_id)
    except Exception as exc:
        logger.error(f"Error disconnecting database: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect database session: {str(exc)}"
        )
