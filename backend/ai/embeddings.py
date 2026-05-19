"""
embeddings.py — ChromaDB schema storage and semantic retrieval for QuerySafe.

Manages per-connection schema embeddings so the LLM pipeline can retrieve only
the most relevant tables for a given natural-language query, reducing token
usage and improving SQL accuracy.

Embedding model: sentence-transformers/all-MiniLM-L6-v2 (384-dim, MIT licensed)
Vector store   : ChromaDB (HTTP client pointing at CHROMA_URL)
"""

import os
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Singleton embedding model — loaded once at import time, shared across calls.
# ---------------------------------------------------------------------------
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


# ---------------------------------------------------------------------------
# ChromaDB client factory
# ---------------------------------------------------------------------------

def get_chroma_client() -> chromadb.HttpClient:
    """
    Returns a ChromaDB HttpClient connected to the CHROMA_URL env variable.
    Defaults to http://localhost:8001 for local development.
    """
    chroma_url = os.getenv("CHROMA_URL", "http://localhost:8001")
    # Parse host and port from URL (e.g. "http://chroma:8001")
    url = chroma_url.rstrip("/")
    if "://" in url:
        url = url.split("://", 1)[1]
    host, _, port_str = url.rpartition(":")
    host = host or "localhost"
    port = int(port_str) if port_str.isdigit() else 8001

    return chromadb.HttpClient(
        host=host,
        port=port,
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(connection_id: str) -> chromadb.Collection:
    """
    Returns (or lazily creates) a ChromaDB collection named
    f"schema_{connection_id}".  Uses cosine similarity.

    Args:
        connection_id: Unique DB connection identifier (e.g. "conn_abc123")

    Returns:
        chromadb.Collection ready for upsert / query
    """
    client = get_chroma_client()
    collection_name = f"schema_{connection_id}"
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


# ---------------------------------------------------------------------------
# Schema indexing
# ---------------------------------------------------------------------------

def _build_table_description(table: dict) -> str:
    """
    Converts a table schema dict into a single descriptive string for embedding.

    Input format (from Person 3 GET /database/schema/{id}):
        {
          "name": "customers",
          "columns": [{"name": "id", "type": "int", "nullable": false}, ...],
          "description": "Stores customer account information"
        }

    Returns:
        "Table customers has columns: id (int, not null), email (varchar, nullable).
         Description: Stores customer account information"
    """
    col_parts = []
    for col in table.get("columns", []):
        col_name = col.get("name", "unknown")
        col_type = col.get("type", "unknown")
        nullable = "nullable" if col.get("nullable", True) else "not null"
        col_parts.append(f"{col_name} ({col_type}, {nullable})")

    columns_str = ", ".join(col_parts) if col_parts else "no columns"
    description = table.get("description", "")
    desc_part = f" Description: {description}" if description else ""

    return f"Table {table.get('name', 'unknown')} has columns: {columns_str}.{desc_part}"


def index_schema(connection_id: str, schema: dict) -> None:
    """
    Takes the schema dict returned by Person 3's GET /database/schema/{id}
    and indexes every table into the ChromaDB collection for this connection.

    Schema format:
        {
          "tables": [
            {
              "name": "customers",
              "columns": [{"name": "id", "type": "int", "nullable": false}],
              "description": "Optional human-readable description"
            }
          ]
        }

    Each table is embedded with all-MiniLM-L6-v2 and upserted (idempotent).

    Args:
        connection_id: Unique DB connection identifier
        schema: Schema dict from Person 3's API
    """
    tables: list[dict] = schema.get("tables", [])
    if not tables:
        return

    model = _get_embedding_model()
    collection = get_or_create_collection(connection_id)

    documents: list[str] = []
    embeddings: list[list[float]] = []
    ids: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for table in tables:
        table_name = table.get("name", "")
        if not table_name:
            continue

        doc_text = _build_table_description(table)
        embedding = model.encode(doc_text).tolist()

        documents.append(doc_text)
        embeddings.append(embedding)
        ids.append(f"{connection_id}::{table_name}")
        metadatas.append(
            {
                "table_name": table_name,
                "connection_id": connection_id,
                "columns_json": str(table.get("columns", [])),
            }
        )

    if documents:
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )


# ---------------------------------------------------------------------------
# Semantic retrieval
# ---------------------------------------------------------------------------

def retrieve_relevant_schema(
    connection_id: str,
    user_prompt: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Embeds the user's natural-language prompt and queries ChromaDB for the
    top_k most semantically relevant table descriptions.

    Returns a list of dicts:
        [
          {
            "table_name": "customers",
            "description": "Table customers has columns: id (int), ...",
            "metadata": {"columns_json": "..."}
          },
          ...
        ]

    Returns an empty list if the collection doesn't exist or has no entries.
    """
    try:
        collection = get_or_create_collection(connection_id)
        if collection.count() == 0:
            return []

        model = _get_embedding_model()
        query_embedding = model.encode(user_prompt).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            where={"connection_id": connection_id},
            include=["documents", "metadatas", "distances"],
        )

        relevant = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for doc, meta in zip(documents, metadatas):
            relevant.append(
                {
                    "table_name": meta.get("table_name", "unknown"),
                    "description": doc,
                    "metadata": meta,
                }
            )

        return relevant

    except Exception:
        # Return empty context rather than crashing the pipeline
        return []


# ---------------------------------------------------------------------------
# Schema cleanup
# ---------------------------------------------------------------------------

def clear_schema(connection_id: str) -> None:
    """
    Deletes the ChromaDB collection for a given connection.
    Called when the user disconnects a database (Person 3's DELETE endpoint).

    Args:
        connection_id: Unique DB connection identifier to clean up
    """
    try:
        client = get_chroma_client()
        collection_name = f"schema_{connection_id}"
        client.delete_collection(name=collection_name)
    except Exception:
        # Collection may not exist — ignore
        pass
