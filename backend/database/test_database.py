"""
test_database.py — Comprehensive unit tests for the QuerySafe database module.
"""

import unittest
from unittest.mock import MagicMock, patch
from database.pool import db_pool, ConnectionPool
from database.routes import is_read_only_query, extract_tables_from_sql, ROLE_ALLOWED_TABLES
from database.adapters.mongodb import MongoDBAdapter


class TestDBRoutesSecurity(unittest.TestCase):
    """
    Tests for SQL read-only validation and RBAC table extraction.
    """

    def test_is_read_only_query(self) -> None:
        """
        Test that only read-only statements are allowed and mutating queries are blocked.
        """
        # Valid read-only statements
        self.assertTrue(is_read_only_query("SELECT * FROM employees"))
        self.assertTrue(is_read_only_query("select first_name, last_name from users where id = 1"))
        self.assertTrue(is_read_only_query("SHOW TABLES"))
        self.assertTrue(is_read_only_query("EXPLAIN SELECT * FROM payroll"))
        self.assertTrue(is_read_only_query("DESCRIBE departments"))
        self.assertTrue(is_read_only_query("  SELECT  1  "))
        self.assertTrue(is_read_only_query("/* comment */ SELECT * FROM employees"))
        self.assertTrue(is_read_only_query("SELECT * FROM employees -- simple comment"))

        # Mutating or forbidden statements
        self.assertFalse(is_read_only_query("INSERT INTO employees (name) VALUES ('John')"))
        self.assertFalse(is_read_only_query("UPDATE employees SET salary = 100000"))
        self.assertFalse(is_read_only_query("DELETE FROM employees WHERE id = 5"))
        self.assertFalse(is_read_only_query("DROP TABLE employees"))
        self.assertFalse(is_read_only_query("CREATE TABLE test (id INT)"))
        self.assertFalse(is_read_only_query("ALTER TABLE employees ADD COLUMN phone VARCHAR"))
        self.assertFalse(is_read_only_query("TRUNCATE TABLE logs"))
        self.assertFalse(is_read_only_query("REPLACE INTO users VALUES (1, 'Jane')"))
        self.assertFalse(is_read_only_query("GRANT ALL PRIVILEGES ON db TO user"))
        self.assertFalse(is_read_only_query("SELECT * INTO new_table FROM old_table"))

    def test_extract_tables_from_sql(self) -> None:
        """
        Test table extraction from SQL SELECT statements.
        """
        self.assertEqual(extract_tables_from_sql("SELECT * FROM employees"), {"employees"})
        self.assertEqual(
            extract_tables_from_sql("SELECT e.name, p.amount FROM employees e JOIN payroll p ON e.id = p.employee_id"),
            {"employees", "payroll"}
        )
        self.assertEqual(
            extract_tables_from_sql("SELECT * FROM schema.departments JOIN public.employees ON id"),
            {"departments", "employees"}
        )
        self.assertEqual(
            extract_tables_from_sql("SELECT * FROM `invoices` JOIN `transactions`"),
            {"invoices", "transactions"}
        )
        self.assertEqual(
            extract_tables_from_sql("SELECT * FROM \"customers\" WHERE active = 1"),
            {"customers"}
        )


class TestDBCredentialsEncryption(unittest.TestCase):
    """
    Tests for database credentials encryption and decryption inside ConnectionPool.
    """

    def test_encryption_decryption(self) -> None:
        """
        Test encrypting and decrypting configuration.
        """
        pool = ConnectionPool()
        test_plaintext = '{"host": "localhost", "password": "super-secret-password-123"}'
        
        encrypted = pool._encrypt(test_plaintext)
        self.assertNotEqual(encrypted, test_plaintext)
        
        decrypted = pool._decrypt(encrypted)
        self.assertEqual(decrypted, test_plaintext)


class TestMongoDBTranslation(unittest.TestCase):
    """
    Tests for SQL-like to MongoDB aggregation pipeline translation.
    """

    def test_sql_to_pipeline_translation(self) -> None:
        """
        Test translation of SELECT queries into pymongo pipelines.
        """
        adapter = MongoDBAdapter()

        # Test simple SELECT *
        coll, pipeline = adapter._translate_sql_to_pipeline("SELECT * FROM employees")
        self.assertEqual(coll, "employees")
        # pipeline should contain only the limit stage (default 500)
        self.assertEqual(pipeline, [{"$limit": 500}])

        # Test SELECT with projection, WHERE, and LIMIT
        coll, pipeline = adapter._translate_sql_to_pipeline(
            "SELECT name, salary, age FROM employees WHERE age > 30 AND department = 'HR' LIMIT 10"
        )
        self.assertEqual(coll, "employees")
        
        # Verify stages
        self.assertEqual(len(pipeline), 3)
        
        # 1. Match stage
        self.assertEqual(
            pipeline[0],
            {"$match": {"age": {"$gt": 30}, "department": "HR"}}
        )
        
        # 2. Project stage
        self.assertEqual(
            pipeline[1],
            {"$project": {"name": 1, "salary": 1, "age": 1, "_id": 0}}
        )
        
        # 3. Limit stage
        self.assertEqual(pipeline[2], {"$limit": 10})

    def test_sql_to_pipeline_in_operator(self) -> None:
        """
        Test translation of WHERE IN condition.
        """
        adapter = MongoDBAdapter()
        coll, pipeline = adapter._translate_sql_to_pipeline(
            "SELECT * FROM users WHERE status IN ('active', 'pending')"
        )
        self.assertEqual(coll, "users")
        self.assertEqual(
            pipeline[0],
            {"$match": {"status": {"$in": ["active", "pending"]}}}
        )


class TestConnectionPoolEviction(unittest.TestCase):
    """
    Tests for connection pool active adapter cache management and cleanup.
    """

    @patch("database.pool.PostgresAdapter")
    def test_pool_connection_caching_and_cleanup(self, mock_postgres_class) -> None:
        """
        Test connection registration, retrieval from cache, and cleanup of idle connections.
        """
        mock_adapter = MagicMock()
        mock_postgres_class.return_value = mock_adapter

        pool = ConnectionPool()
        # Avoid trying to save to real Redis in this unit test
        pool.redis = None

        config = {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "user": "test",
            "password": "pwd",
            "database": "db"
        }

        # Connect
        conn_id = pool.connect_database(config)
        self.assertIn(conn_id, pool._cache)
        
        # Verify in-memory adapter is stored and connect was called
        cached_adapter, first_time = pool._cache[conn_id]
        self.assertEqual(cached_adapter, mock_adapter)
        mock_adapter.connect.assert_called_once_with(config)

        # Get connection (hits cache)
        retrieved_adapter = pool.get_connection(conn_id)
        self.assertEqual(retrieved_adapter, mock_adapter)

        # Force idle connection (> 1800s in the past)
        pool._cache[conn_id] = (mock_adapter, first_time - 1900)

        # Trigger cleanup
        pool._cleanup_idle()

        # Connection should have been evicted and disconnect called
        self.assertNotIn(conn_id, pool._cache)
        mock_adapter.disconnect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
