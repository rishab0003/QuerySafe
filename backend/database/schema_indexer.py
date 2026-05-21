"""
schema_indexer.py — Retrieves and indexes structured schemas for ChromaDB ingestion.
"""

import logging
from typing import Any, Dict
from database.pool import db_pool

logger = logging.getLogger("querysafe.database.schema_indexer")


def get_database_schema(connection_id: str) -> Dict[str, Any]:
    """
    Retrieve structured schema information for a specific database connection.
    This schema is formatted for ingestion by Person 1 (AI Engineer) into ChromaDB.

    Args:
        connection_id: The UUID of the active connection session.

    Returns:
        A dictionary containing database type and a list of table metadata:
        - database_type: "postgres", "mysql", "mongodb"
        - tables: list of dicts with name, columns, primary_keys, foreign_keys
    """
    logger.info(f"Indexing schema for connection_id: {connection_id}")
    try:
        adapter = db_pool.get_connection(connection_id)
        schema = adapter.get_schema()
        logger.info(f"Successfully retrieved schema for connection_id: {connection_id} ({schema['database_type']})")
        return schema
    except Exception as exc:
        logger.error(f"Failed to index schema for connection_id {connection_id}: {exc}")
        raise RuntimeError(f"Schema indexing failed: {exc}") from exc
