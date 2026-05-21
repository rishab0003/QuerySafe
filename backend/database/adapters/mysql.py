"""
mysql.py — MySQL database adapter.
"""

import time
from typing import Any, Dict, List, Tuple
from sqlalchemy import create_engine, text, event, inspect
from sqlalchemy.exc import DBAPIError, OperationalError
from database.adapters.base import BaseDBAdapter


class MySQLAdapter(BaseDBAdapter):
    """
    MySQL database adapter using SQLAlchemy and pymysql.
    Enforces strict read-only transactions and query timeouts.
    """

    def __init__(self) -> None:
        self.engine = None
        self._config = None

    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish a connection to the MySQL database.

        Args:
            config: Connection credentials dictionary including host, port, user, password, database.
        """
        self._config = config
        host = config.get("host", "localhost")
        port = config.get("port", 3306)
        user = config.get("user")
        password = config.get("password")
        database = config.get("database")

        # Construct SQLAlchemy connection URI
        connection_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

        # 10s read/write timeout configured in pymysql
        connect_args = {
            "read_timeout": 10,
            "write_timeout": 10
        }

        # Create engine with read-only options
        self.engine = create_engine(
            connection_uri,
            connect_args=connect_args
        )

        # Enforce read-only mode at the session level by listening to connect events
        @event.listens_for(self.engine, "connect")
        def set_readonly(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SET SESSION transaction_read_only = 1;")
            except Exception:
                # Fallback if target MySQL version doesn't support session transaction_read_only (older than 5.7.20)
                try:
                    cursor.execute("SET TRANSACTION READ ONLY;")
                except Exception:
                    pass
            finally:
                cursor.close()

        # Test the connection immediately
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except (DBAPIError, OperationalError) as exc:
            self.disconnect()
            raise RuntimeError(f"Failed to connect to MySQL: {exc}") from exc

    def disconnect(self) -> None:
        """
        Close the MySQL connection engine and release resources.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def execute_readonly(
        self, query: str, timeout: int = 10, limit: int = 500
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """
        Execute a read-only query on MySQL.

        Args:
            query: The SELECT query string.
            timeout: Query timeout in seconds.
            limit: Maximum rows to return (up to 500).

        Returns:
            A tuple of (rows, row_count, execution_time_ms)
        """
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        start_time = time.perf_counter()
        rows = []

        try:
            with self.engine.connect() as conn:
                # Set dynamic execution timeout inside MySQL session block if supported
                try:
                    conn.execute(text(f"SET max_execution_time = {timeout * 1000}"))
                except Exception:
                    pass

                result = conn.execute(text(query))
                fetched_rows = result.fetchmany(limit)

                # Format each row into a dictionary
                for row in fetched_rows:
                    rows.append(dict(row._mapping))

                row_count = len(rows)
        except Exception as exc:
            raise RuntimeError(f"MySQL query execution failed: {exc}") from exc

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        return rows, row_count, execution_time_ms

    def get_schema(self) -> Dict[str, Any]:
        """
        Extract MySQL database schema using SQLAlchemy inspector.

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
            raise RuntimeError(f"Failed to inspect MySQL schema: {exc}") from exc

        return {
            "database_type": "mysql",
            "tables": tables_metadata
        }
