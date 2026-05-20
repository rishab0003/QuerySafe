"""
auth/models.py — SQLAlchemy ORM models for User and AuditLog tables.
QuerySafe — Person 2: Security & Auth
"""

import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, DateTime, Enum as SAEnum,
    create_engine, text
)
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/querysafe")

# Test PostgreSQL connection to check if it's available, otherwise fallback to SQLite
try:
    if DATABASE_URL.startswith("postgresql"):
        # Quick check for reachability
        temp_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 2})
        with temp_engine.connect() as conn:
            pass
        temp_engine.dispose()
        print("[QuerySafe] Connected to PostgreSQL successfully.")
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    else:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception:
    print("[QuerySafe] PostgreSQL connection failed. Falling back to local SQLite database: 'querysafe.db'.")
    DATABASE_URL = "sqlite:///./querysafe.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRole(str, enum.Enum):
    admin = "admin"
    hr = "hr"
    finance = "finance"
    sales = "sales"
    support = "support"


class User(Base):
    __tablename__ = "users"

    # Use String instead of Postgres-specific UUID for universal cross-DB compatibility
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.support)
    totp_secret = Column(String, nullable=True)          # stored encrypted
    is_2fa_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # Use String instead of Postgres-specific UUID for universal cross-DB compatibility
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_role = Column(String, nullable=True)
    action = Column(String, nullable=False)           # e.g. 'login_success', 'query_blocked'
    resource = Column(String, nullable=True)          # table name or endpoint hit
    details = Column(String, nullable=True)           # JSON-serialised extra context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

def get_db():
    """Yield a database session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables on startup if they do not already exist."""
    print("[QuerySafe] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[QuerySafe] Tables ready.")

