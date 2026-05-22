"""
pool.py — Redis-backed connection pool and credential manager.
"""

import base64
import hashlib
import json
import logging
import os
import time
import uuid
from typing import Any, Dict, Tuple
from cryptography.fernet import Fernet
import redis

from database.adapters.postgres import PostgresAdapter
from database.adapters.mysql import MySQLAdapter
from database.adapters.mongodb import MongoDBAdapter

logger = logging.getLogger("querysafe.database.pool")


class ConnectionPool:
    """
    Redis-backed connection manager.
    Stores encrypted database credentials in Redis and maintains an in-memory
    cache of active database adapter instances. Auto-evicts idle connections after 30 minutes.
    """

    def __init__(self) -> None:
        # In-memory cache of active adapter instances:
        # {connection_id: (adapter_instance, last_used_timestamp)}
        self._cache: Dict[str, Tuple[Any, float]] = {}
        
        # Initialize Redis connection
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self.redis.ping()
            logger.info("Connected to Redis successfully for ConnectionPool.")
        except Exception as exc:
            logger.warning(f"Could not connect to Redis: {exc}. Falling back to in-memory metadata storage.")
            self.redis = None

        # Local fallback database for metadata when Redis is not running (e.g., local development/tests)
        self._local_redis_fallback: Dict[str, Dict[str, Any]] = {}

    def _get_fernet(self) -> Fernet:
        """
        Derive a stable 32-byte URL-safe base64 Fernet encryption key from the environment.
        """
        secret = (
            os.getenv("DATABASE_ENCRYPTION_KEY")
            or os.getenv("SECRET_KEY")
            or "querysafe-default-secret-encryption-key-phrase-32b"
        )
        # Use SHA-256 to ensure exactly 32 bytes, then base64 encode for Fernet
        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
        return Fernet(key)

    def _encrypt(self, data: str) -> str:
        """
        Encrypt a plaintext string using AES-256 (Fernet).
        """
        fernet = self._get_fernet()
        return fernet.encrypt(data.encode()).decode()

    def _decrypt(self, token: str) -> str:
        """
        Decrypt a ciphertext token using AES-256 (Fernet).
        """
        fernet = self._get_fernet()
        return fernet.decrypt(token.encode()).decode()

    def _get_adapter_class(self, db_type: str) -> Any:
        """
        Map a database type string to its corresponding adapter class.
        """
        db_type = db_type.lower()
        if db_type == "postgres" or db_type == "postgresql":
            return PostgresAdapter
        elif db_type == "mysql":
            return MySQLAdapter
        elif db_type == "mongodb" or db_type == "mongo":
            return MongoDBAdapter
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def connect_database(self, config: Dict[str, Any]) -> str:
        """
        Verify database credentials, establish a connection, and persist the encrypted metadata.

        Args:
            config: Database connection configuration dictionary.

        Returns:
            A unique connection_id (UUID string).
        """
        db_type = config.get("type")
        if not db_type:
            raise ValueError("Database 'type' is required in configuration.")

        # 1. Instantiate the adapter and test connection
        adapter_class = self._get_adapter_class(db_type)
        adapter = adapter_class()
        
        try:
            adapter.connect(config)
        except Exception as exc:
            logger.error(f"Failed to connect to database of type {db_type}: {exc}")
            raise RuntimeError(f"Connection test failed: {exc}") from exc

        # 2. Generate a unique connection ID
        connection_id = str(uuid.uuid4())
        current_time = time.time()

        # 3. Encrypt the connection metadata
        config_json = json.dumps(config)
        encrypted_config = self._encrypt(config_json)

        # 4. Save metadata to Redis (or fallback) with a 30-minute TTL (1800s)
        redis_key = f"querysafe:connection:{connection_id}"
        metadata = {
            "config": encrypted_config,
            "type": db_type,
            "last_active": str(current_time)
        }

        if self.redis:
            try:
                self.redis.hset(redis_key, mapping=metadata)
                self.redis.expire(redis_key, 1800)
            except Exception as exc:
                logger.error(f"Failed to save metadata to Redis: {exc}")
                self._local_redis_fallback[redis_key] = metadata
        else:
            self._local_redis_fallback[redis_key] = metadata

        # 5. Cache the active adapter instance in-memory
        self._cache[connection_id] = (adapter, current_time)
        logger.info(f"Database connection successfully established and cached. ID: {connection_id}")

        return connection_id

    def get_connection(self, connection_id: str) -> Any:
        """
        Retrieve an active database adapter by its connection_id.
        Re-establishes the connection if cached metadata is present but adapter is closed.
        Auto-evicts idle connections.
        """
        current_time = time.time()
        
        # Run cleanup routine before checking
        self._cleanup_idle()

        # 1. Check in-memory cache first
        if connection_id in self._cache:
            adapter, last_used = self._cache[connection_id]
            # Check for 30 minutes idle timeout
            if current_time - last_used > 1800:
                logger.info(f"Connection {connection_id} has been idle for > 30 minutes. Closing.")
                self.disconnect_database(connection_id)
                raise RuntimeError("Connection session expired due to inactivity (30 minutes).")

            # Update last used timestamp in cache
            self._cache[connection_id] = (adapter, current_time)
            
            # Reset Redis TTL to 30 minutes
            redis_key = f"querysafe:connection:{connection_id}"
            if self.redis:
                try:
                    self.redis.hset(redis_key, "last_active", str(current_time))
                    self.redis.expire(redis_key, 1800)
                except Exception as exc:
                    logger.warning(f"Failed to update last_active in Redis: {exc}")
            
            return adapter

        # 2. If not cached, fetch encrypted configuration from Redis (or local fallback)
        redis_key = f"querysafe:connection:{connection_id}"
        metadata = None

        if self.redis:
            try:
                metadata = self.redis.hgetall(redis_key)
            except Exception as exc:
                logger.error(f"Failed to fetch metadata from Redis: {exc}")
                metadata = self._local_redis_fallback.get(redis_key)
        else:
            metadata = self._local_redis_fallback.get(redis_key)

        if not metadata or "config" not in metadata:
            raise RuntimeError("Connection session expired or is invalid.")

        # 3. Decrypt credentials and connect
        try:
            decrypted_config_json = self._decrypt(metadata["config"])
            config = json.loads(decrypted_config_json)
        except Exception as exc:
            raise RuntimeError(f"Failed to decrypt database credentials: {exc}") from exc

        db_type = metadata["type"]
        adapter_class = self._get_adapter_class(db_type)
        adapter = adapter_class()

        logger.info(f"Re-connecting to database session: {connection_id} ({db_type})")
        try:
            adapter.connect(config)
        except Exception as exc:
            raise RuntimeError(f"Re-connection failed: {exc}") from exc

        # 4. Put back in in-memory cache and reset Redis TTL
        self._cache[connection_id] = (adapter, current_time)
        if self.redis:
            try:
                self.redis.hset(redis_key, "last_active", str(current_time))
                self.redis.expire(redis_key, 1800)
            except Exception as exc:
                logger.warning(f"Failed to reset Redis TTL: {exc}")

        return adapter

    def disconnect_database(self, connection_id: str) -> None:
        """
        Close a database adapter, remove it from the cache, and delete credentials from Redis.
        """
        # 1. Clean up in-memory adapter
        if connection_id in self._cache:
            adapter, _ = self._cache.pop(connection_id)
            try:
                adapter.disconnect()
                logger.info(f"Successfully disconnected database adapter for ID: {connection_id}")
            except Exception as exc:
                logger.warning(f"Error disconnecting database adapter {connection_id}: {exc}")

        # 2. Clean up Redis metadata
        redis_key = f"querysafe:connection:{connection_id}"
        if self.redis:
            try:
                self.redis.delete(redis_key)
            except Exception as exc:
                logger.warning(f"Failed to delete Redis metadata for {connection_id}: {exc}")
        
        if redis_key in self._local_redis_fallback:
            self._local_redis_fallback.pop(redis_key)

    def _cleanup_idle(self) -> None:
        """
        Iterate through the cached connections and close any that have been idle
        for more than 30 minutes (1800 seconds).
        """
        current_time = time.time()
        idle_ids = []

        for conn_id, (_, last_used) in self._cache.items():
            if current_time - last_used > 1800:
                idle_ids.append(conn_id)

        for conn_id in idle_ids:
            logger.info(f"Running auto-cleanup on idle connection ID: {conn_id}")
            self.disconnect_database(conn_id)


# Global singleton instance of the connection pool
db_pool = ConnectionPool()
