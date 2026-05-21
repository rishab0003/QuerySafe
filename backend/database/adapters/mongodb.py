"""
mongodb.py — MongoDB database adapter.
"""

import re
import time
from typing import Any, Dict, List, Tuple
from pymongo import MongoClient
from database.adapters.base import BaseDBAdapter


class MongoDBAdapter(BaseDBAdapter):
    """
    MongoDB database adapter using pymongo.
    Translates basic SQL-like queries into aggregation pipelines,
    enforcing strict read-only query execution and query timeouts.
    """

    def __init__(self) -> None:
        self.client = None
        self.db = None
        self._config = None

    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish a connection to the MongoDB database.

        Args:
            config: Connection credentials dictionary including host, port, user, password, database.
        """
        self._config = config
        host = config.get("host", "localhost")
        port = config.get("port", 27017)
        user = config.get("user")
        password = config.get("password")
        database = config.get("database")

        # Construct MongoDB URI
        if user and password:
            uri = f"mongodb://{user}:{password}@{host}:{port}/{database}?authSource=admin"
        else:
            uri = f"mongodb://{host}:{port}/{database}"

        try:
            # 10s server selection timeout
            self.client = MongoClient(uri, serverSelectionTimeoutMS=10000, socketTimeoutMS=10000)
            self.db = self.client[database]
            
            # Test the connection immediately by calling server_info()
            self.client.server_info()
        except Exception as exc:
            self.disconnect()
            raise RuntimeError(f"Failed to connect to MongoDB: {exc}") from exc

    def disconnect(self) -> None:
        """
        Close the MongoDB client connection and release resources.
        """
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def _translate_sql_to_pipeline(self, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Translate a basic SQL SELECT statement into a MongoDB collection name and aggregation pipeline.

        Supported SQL:
        SELECT col1, col2 / SELECT *
        FROM collection_name
        WHERE col1 = 'val' AND col2 > 10
        LIMIT 50

        Returns:
            A tuple of (collection_name, pipeline_stages_list)
        """
        # Clean the query: replace newlines/tabs with spaces and trim
        cleaned_query = re.sub(r"\s+", " ", query.strip())
        
        # Regex to capture: SELECT, FROM, WHERE (optional), LIMIT (optional)
        # Supports ending semi-colons or whitespaces
        pattern = re.compile(
            r"^SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*?))?(?:\s+LIMIT\s+(\d+))?\s*;?\s*$",
            re.IGNORECASE
        )
        
        match = pattern.match(cleaned_query)
        if not match:
            raise ValueError(
                "Unsupported SQL query format for MongoDB translation. "
                "Ensure it follows: SELECT [fields] FROM [collection] [WHERE conditions] [LIMIT n]"
            )

        select_clause, collection_name, where_clause, limit_clause = match.groups()
        pipeline = []

        # 1. WHERE clause ($match stage)
        if where_clause:
            match_stage = self._parse_where_clause(where_clause)
            if match_stage:
                pipeline.append({"$match": match_stage})

        # 2. SELECT clause ($project stage)
        select_fields = [f.strip() for f in select_clause.split(",")]
        if len(select_fields) == 1 and select_fields[0] == "*":
            # No projection stage required, return all fields
            pass
        else:
            project_stage = {}
            for field in select_fields:
                project_stage[field] = 1
            # Exclude _id if it's not explicitly requested
            if "_id" not in select_fields:
                project_stage["_id"] = 0
            pipeline.append({"$project": project_stage})

        # 3. LIMIT clause ($limit stage)
        if limit_clause:
            limit_val = min(int(limit_clause), 500)
        else:
            limit_val = 500
        pipeline.append({"$limit": limit_val})

        return collection_name, pipeline

    def _parse_where_clause(self, where_clause: str) -> Dict[str, Any]:
        """
        Parse WHERE SQL conditions and translate them to a MongoDB query dictionary.
        Supports: =, !=, >, >=, <, <=, IN, AND operators.
        """
        # Split conditions by " AND " (case-insensitive)
        conditions = re.split(r"\s+AND\s+", where_clause, flags=re.IGNORECASE)
        match_dict = {}

        for cond in conditions:
            # Match operator and operands: field, operator, value
            # Regex captures operators: =, !=, >=, <=, >, <, IN
            op_pattern = re.compile(
                r"^(\w+)\s*(=|!=|>=|<=|>|<|\bIN\b)\s*(.+)$",
                re.IGNORECASE
            )
            cond_match = op_pattern.match(cond.strip())
            if not cond_match:
                continue

            field, operator, raw_value = cond_match.groups()
            field = field.strip()
            operator = operator.strip().upper()
            raw_value = raw_value.strip()

            # Parse python type
            value = self._parse_literal_value(raw_value, operator)

            # Map SQL operators to MongoDB query operators
            if operator == "=":
                match_dict[field] = value
            elif operator == "!=":
                match_dict[field] = {"$ne": value}
            elif operator == ">":
                match_dict[field] = {"$gt": value}
            elif operator == ">=":
                match_dict[field] = {"$gte": value}
            elif operator == "<":
                match_dict[field] = {"$lt": value}
            elif operator == "<=":
                match_dict[field] = {"$lte": value}
            elif operator == "IN":
                match_dict[field] = {"$in": value}

        return match_dict

    def _parse_literal_value(self, val_str: str, operator: str) -> Any:
        """
        Helper to parse a SQL literal string value into a python type (int, float, str, bool, list).
        """
        val_str = val_str.strip()

        # Handle IN operator list e.g., (1, 2, 'HR') or ('Finance', 'HR')
        if operator == "IN":
            # Extract content inside parentheses
            in_match = re.match(r"^\((.*)\)$", val_str)
            if in_match:
                list_items = [item.strip() for item in in_match.group(1).split(",")]
                return [self._parse_literal_value(item, "=") for item in list_items]
            return [val_str]

        # Handle quoted strings
        if (val_str.startswith("'") and val_str.endswith("'")) or (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]

        # Handle numeric values
        try:
            if "." in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            pass

        # Handle Booleans and Nulls
        lower_val = val_str.lower()
        if lower_val == "true":
            return True
        if lower_val == "false":
            return False
        if lower_val == "null":
            return None

        # Default fallback is string
        return val_str

    def execute_readonly(
        self, query: str, timeout: int = 10, limit: int = 500
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """
        Execute a read-only query (aggregation pipeline) on MongoDB.

        Args:
            query: SQL SELECT query string.
            timeout: Query timeout in seconds.
            limit: Maximum rows to return (up to 500).

        Returns:
            A tuple of (rows, row_count, execution_time_ms)
        """
        if not self.db:
            raise RuntimeError("Database not connected. Call connect() first.")

        start_time = time.perf_counter()
        rows = []

        try:
            # Translate SQL to MongoDB Aggregation Pipeline
            collection_name, pipeline = self._translate_sql_to_pipeline(query)

            # Cap the final limit stage in pipeline at parameter limit
            for stage in pipeline:
                if "$limit" in stage:
                    stage["$limit"] = min(stage["$limit"], limit)
                    break
            else:
                # Append a limit stage if none exists
                pipeline.append({"$limit": limit})

            # Run aggregation pipeline (read-only by nature)
            # maxTimeMS enforces query timeout at the MongoDB server level
            cursor = self.db[collection_name].aggregate(pipeline, maxTimeMS=timeout * 1000)
            
            for doc in cursor:
                # Convert ObjectId to string to make it JSON serializable
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                rows.append(doc)

            row_count = len(rows)
        except Exception as exc:
            raise RuntimeError(f"MongoDB query execution failed: {exc}") from exc

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        return rows, row_count, execution_time_ms

    def get_schema(self) -> Dict[str, Any]:
        """
        Extract MongoDB schema by listing collections and sampling documents to infer types.

        Returns:
            Structured schema metadata JSON.
        """
        if not self.db:
            raise RuntimeError("Database not connected. Call connect() first.")

        tables_metadata = []

        try:
            collections = self.db.list_collection_names()
            for coll_name in collections:
                # Ignore system collections
                if coll_name.startswith("system."):
                    continue

                # Sample up to 5 documents from the collection
                sample_docs = list(self.db[coll_name].find().limit(5))
                
                # Dictionary to track discovered fields and their inferred types
                discovered_fields = {}

                for doc in sample_docs:
                    for key, val in doc.items():
                        # Map Python type to structured JSON type description
                        py_type = type(val).__name__
                        type_mapping = {
                            "str": "VARCHAR",
                            "int": "INTEGER",
                            "float": "FLOAT",
                            "bool": "BOOLEAN",
                            "list": "ARRAY",
                            "dict": "OBJECT",
                            "NoneType": "NULL",
                            "ObjectId": "OBJECT_ID"
                        }
                        inferred_type = type_mapping.get(py_type, "VARCHAR")
                        discovered_fields[key] = inferred_type

                columns = []
                for field_name, field_type in discovered_fields.items():
                    columns.append({
                        "name": field_name,
                        "type": field_type,
                        "nullable": True,
                        "default": None
                    })

                primary_keys = ["_id"] if "_id" in discovered_fields else []

                tables_metadata.append({
                    "name": coll_name,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": []  # No foreign keys in standard MongoDB
                })
        except Exception as exc:
            raise RuntimeError(f"Failed to inspect MongoDB schema: {exc}") from exc

        return {
            "database_type": "mongodb",
            "tables": tables_metadata
        }
