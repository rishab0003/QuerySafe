"""
base.py — Abstract base class for database adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class BaseDBAdapter(ABC):
    """
    Abstract base class defining the interface for QuerySafe database adapters.
    All database adapters must implement this interface to support connection,
    disconnection, read-only query execution, and schema metadata discovery.
    """

    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish a connection or engine using the provided configuration.

        Args:
            config: A dictionary containing connection credentials:
                    (type, host, port, user, password, database, etc.)
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Cleanly close the database connection and release resources.
        """
        pass

    @abstractmethod
    def execute_readonly(
        self, query: str, timeout: int = 10, limit: int = 500
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """
        Execute a read-only query on the database.

        Args:
            query: The SQL-like or database-native query string to execute.
            timeout: The query execution timeout in seconds. Default is 10.
            limit: The maximum number of rows to return. Default is 500.

        Returns:
            A tuple of (rows, row_count, execution_time_ms) where:
            - rows is a list of dictionaries, each mapping column/field names to values.
            - row_count is the total number of rows returned.
            - execution_time_ms is the time taken to run the query in milliseconds.
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Retrieve database schema metadata.

        Returns:
            A structured dictionary containing:
            - database_type: The type of database (e.g. postgres, mysql, mongodb)
            - tables: A list of table/collection schemas including columns, types, and constraints.
        """
        pass
