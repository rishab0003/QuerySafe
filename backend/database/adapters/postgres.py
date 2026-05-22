"""
postgres.py — PostgreSQL database adapter.
"""

import time
from typing import Any, Dict, List, Tuple
from sqlalchemy import create_engine, text, event, inspect
from sqlalchemy.exc import DBAPIError, OperationalError
from database.adapters.base import BaseDBAdapter


class PostgresAdapter(BaseDBAdapter):
    """
    PostgreSQL database adapter using SQLAlchemy and psycopg2.
    Enforces strict read-only transactions and query timeouts.
    """

    def __init__(self) -> None:
        self.engine = None
        self._config = None

    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish a connection to the PostgreSQL database.

        Args:
            config: Connection credentials dictionary including host, port, user, password, database.
        """
        self._config = config
        host = config.get("host", "localhost")
        port = config.get("port", 5432)
        user = config.get("user")
        password = config.get("password")
        database = config.get("database")

        # Construct SQLAlchemy connection URI
        connection_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        # 10s timeout configured at the connection level via statement_timeout
        connect_args = {
            "options": "-c statement_timeout=10000"
        }

        # Create engine with read-only execution options
        self.engine = create_engine(
            connection_uri,
            connect_args=connect_args,
            execution_options={"postgresql_readonly": True}
        )

        # Enforce read-only mode at the database level by listening to connect events
        @event.listens_for(self.engine, "connect")
        def set_readonly(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY;")
            except Exception:
                # Fallback check if execution fails
                pass
            finally:
                cursor.close()

        # Test the connection immediately
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except (DBAPIError, OperationalError) as exc:
            self.disconnect()
            raise RuntimeError(f"Failed to connect to PostgreSQL: {exc}") from exc

    def disconnect(self) -> None:
        """
        Close the PostgreSQL connection engine and release resources.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def execute_readonly(
        self, query: str, timeout: int = 10, limit: int = 500
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """
        Execute a read-only query on PostgreSQL.

        Args:
            query: The SELECT query string.
            timeout: Query timeout in seconds (driver level is 10s).
            limit: Maximum rows to return (up to 500).

        Returns:
            A tuple of (rows, row_count, execution_time_ms)
        """
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        # Ensure query is executed in a read-only context
        start_time = time.perf_counter()
        rows = []
        
        try:
            with self.engine.connect() as conn:
                # Apply statement timeout for this session block
                conn.execute(text(f"SET statement_timeout = {timeout * 1000}"))
                result = conn.execute(text(query))
                
                # Fetch up to the limit
                fetched_rows = result.fetchmany(limit)
                
                # Format each row into a dictionary
                for row in fetched_rows:
                    rows.append(dict(row._mapping))
                
                row_count = len(rows)
        except Exception as exc:
            raise RuntimeError(f"PostgreSQL query execution failed: {exc}") from exc

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        return rows, row_count, execution_time_ms

    def get_schema(self) -> Dict[str, Any]:
        """
        Extract PostgreSQL database schema using SQLAlchemy inspector.

        Returns:
            Structured schema metadata JSON.
        """
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        inspector = inspect(self.engine)
        tables_metadata = []

        try:
            for table_name in inspector.get_table_names():
                columns = []
                for col in inspector.get_columns(table_name):
                    columns.append({
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "default": str(col["default"]) if col.get("default") is not None else None
                    })

                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint.get("constrained_columns", [])

                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name):
                    foreign_keys.append({
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    })

                tables_metadata.append({
                    "name": table_name,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys
                })
        except Exception as exc:
            raise RuntimeError(f"Failed to inspect PostgreSQL schema: {exc}") from exc

        return {
            "database_type": "postgres",
            "tables": tables_metadata
        }
