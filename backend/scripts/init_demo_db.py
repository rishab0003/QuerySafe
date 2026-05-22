"""Create a small demo SQLite database with sample data.

This script exposes `init_db(path=None)` so tests can create the DB programmatically.
"""
from pathlib import Path
import sqlite3
from typing import Optional


def init_db(path: Optional[str] = None):
    base = Path(__file__).resolve().parents[1] / 'demo'
    base.mkdir(parents=True, exist_ok=True)
    db_path = Path(path) if path else base / 'demo.sqlite'
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    # Create employees table
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            email TEXT,
            full_name TEXT,
            department TEXT,
            role TEXT,
            approval_status TEXT,
            is_active INTEGER
        )
        '''
    )
    # Create signups table for chart demo
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS signups (
            day TEXT,
            count INTEGER
        )
        '''
    )

    # Insert sample employees
    cur.execute("DELETE FROM employees")
    employees = [
        ("1", "alice@example.com", "Alice Admin", "engineering", "admin", "approved", 1),
        ("2", "bob@example.com", "Bob HR", "hr", "hr", "approved", 1),
        ("3", "carol@example.com", "Carol Pending", "sales", "viewer", "pending", 0),
    ]
    cur.executemany("INSERT OR REPLACE INTO employees VALUES (?,?,?,?,?,?,?)", employees)

    # Insert sample signups (7 days)
    cur.execute("DELETE FROM signups")
    signups = [(f"Day {i+1}", (i + 1) * 5 + 10) for i in range(7)]
    cur.executemany("INSERT INTO signups VALUES (?,?)", signups)

    conn.commit()
    conn.close()
    return str(db_path)


if __name__ == '__main__':
    print('Creating demo DB at', init_db())
