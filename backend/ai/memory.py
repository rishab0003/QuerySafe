"""
memory.py — Redis-based session memory for QuerySafe AI conversation history.

Stores and retrieves the last 5 user/assistant message pairs per session.
Keys follow pattern: session:{session_id}:messages
TTL: 3600 seconds (1 hour) of inactivity.
"""

import json
import os
from datetime import datetime, timezone

import redis


def get_redis_client() -> redis.Redis:
    """
    Returns a configured Redis client connected via REDIS_URL env variable.
    Falls back to localhost:6379 with no auth for local dev.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )


def _session_key(session_id: str) -> str:
    """Returns the Redis key for a given session."""
    return f"session:{session_id}:messages"


def get_session_history(session_id: str) -> list[dict]:
    """
    Retrieves the last 5 messages (up to 10 entries: 5 user + 5 assistant)
    for the given session_id from Redis.

    Each message is a dict: { role: "user"|"assistant", content: str, timestamp: str }
    Returns an empty list if the session does not exist or Redis is unavailable.
    """
    try:
        client = get_redis_client()
        key = _session_key(session_id)
        raw_messages = client.lrange(key, -10, -1)  # last 10 entries
        if not raw_messages:
            return []
        messages = []
        for raw in raw_messages:
            try:
                msg = json.loads(raw)
                messages.append(msg)
            except json.JSONDecodeError:
                continue
        return messages
    except redis.RedisError:
        # Graceful degradation — return empty history if Redis is unavailable
        return []


def save_message(session_id: str, role: str, content: str) -> None:
    """
    Appends a new message to the Redis list for the given session.
    Trims the list to the last 10 entries (5 user + 5 assistant).
    Sets / refreshes a TTL of 3600 seconds on the key.

    Args:
        session_id: Unique session identifier (e.g. "sess_xyz")
        role: "user" or "assistant"
        content: The message text
    """
    if role not in ("user", "assistant"):
        raise ValueError(f"Invalid role '{role}'. Must be 'user' or 'assistant'.")

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        client = get_redis_client()
        key = _session_key(session_id)

        pipe = client.pipeline()
        pipe.rpush(key, json.dumps(message))
        pipe.ltrim(key, -10, -1)   # keep only last 10 entries
        pipe.expire(key, 3600)     # reset TTL on every write
        pipe.execute()
    except redis.RedisError:
        # Non-fatal: memory persistence fails silently; query still proceeds
        pass


def clear_session(session_id: str) -> None:
    """
    Deletes all messages stored for the given session_id.
    Called on logout or explicit session reset.
    """
    try:
        client = get_redis_client()
        client.delete(_session_key(session_id))
    except redis.RedisError:
        pass


def format_history_for_prompt(history: list[dict]) -> str:
    """
    Converts the list of message dicts into a plain-text string
    suitable for injection into an LLM system/user prompt.

    Format:
        User: <content>
        Assistant: <content>
        ...

    Args:
        history: List of message dicts with 'role' and 'content' keys

    Returns:
        A newline-delimited conversation string, or empty string if no history.
    """
    if not history:
        return ""

    lines = []
    for msg in history:
        role_label = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        if content:
            lines.append(f"{role_label}: {content}")

    return "\n".join(lines)
