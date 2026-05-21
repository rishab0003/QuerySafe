-- migrations/001_init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_department AS ENUM ('engineering','hr','finance','sales','support');
CREATE TYPE user_role AS ENUM ('admin','hr','finance','sales','support');

CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  department user_department NOT NULL,
  role user_role NOT NULL,
  totp_secret TEXT,
  is_2fa_enabled BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS database_connections (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  db_type TEXT NOT NULL,
  encrypted_credentials TEXT,
  connection_status TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  connection_id uuid REFERENCES database_connections(id),
  natural_query TEXT,
  generated_sql TEXT,
  execution_time_ms INTEGER,
  row_count INTEGER,
  was_blocked BOOLEAN DEFAULT FALSE,
  block_reason TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  session_token TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_dbconns_user_id ON database_connections(user_id);
-- ============================================================
-- QuerySafe — PostgreSQL Migration: 001_init.sql
-- Initializes the internal metadata database schema.
-- Run automatically by postgres:16 via docker-entrypoint-initdb.d/
-- ============================================================

-- ── Extensions ───────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";     -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "citext";       -- case-insensitive text for emails

-- ── Users ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           CITEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'viewer'
                        CHECK (role IN ('admin', 'hr', 'finance', 'sales', 'support', 'viewer')),
    department      TEXT,
    totp_secret     TEXT,                    -- encrypted TOTP secret (AES-256)
    is_2fa_enabled  BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users (role);

-- ── Database Connections ──────────────────────────────────────
-- Stores encrypted connection metadata per user.
-- Credentials are never stored in plaintext — encrypted_credentials
-- holds an AES-256-GCM encrypted JSON blob.
CREATE TABLE IF NOT EXISTS database_connections (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connection_name       TEXT NOT NULL,
    db_type               TEXT NOT NULL
                              CHECK (db_type IN ('postgresql', 'mysql', 'mongodb',
                                                  'sqlserver', 'snowflake', 'bigquery')),
    host                  TEXT NOT NULL,
    port                  INTEGER NOT NULL,
    database_name         TEXT NOT NULL,
    encrypted_credentials TEXT NOT NULL,     -- AES-256-GCM encrypted JSON
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at          TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_db_connections_user_id ON database_connections (user_id);
CREATE INDEX IF NOT EXISTS idx_db_connections_active  ON database_connections (is_active);

-- ── Query Audit Log ───────────────────────────────────────────
-- Every AI-generated and executed query is recorded here for compliance.
CREATE TABLE IF NOT EXISTS query_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    connection_id   UUID REFERENCES database_connections(id) ON DELETE SET NULL,
    session_id      TEXT NOT NULL,
    user_prompt     TEXT NOT NULL,
    generated_sql   TEXT NOT NULL,
    is_safe         BOOLEAN NOT NULL DEFAULT TRUE,
    safety_reason   TEXT,
    row_count       INTEGER,
    query_time_ms   NUMERIC(10, 2),
    confidence      NUMERIC(4, 3),
    tables_used     TEXT[],
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user_id     ON query_audit_log (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at  ON query_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_session_id  ON query_audit_log (session_id);
CREATE INDEX IF NOT EXISTS idx_audit_is_safe     ON query_audit_log (is_safe)
    WHERE is_safe = FALSE;  -- partial index for fast blocked-query lookup

-- ── Refresh Token Store ───────────────────────────────────────
-- JWT refresh tokens (complements Redis blacklist for revocation).
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT NOT NULL UNIQUE,          -- SHA-256 hash of the raw token
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id    ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens (expires_at);

-- ── Role-Based Access Control Policies ───────────────────────
-- Stores which tables each role may access per connection type.
-- Seeded with defaults; admin can update via API.
CREATE TABLE IF NOT EXISTS rbac_policies (
    id              SERIAL PRIMARY KEY,
    role            TEXT NOT NULL
                        CHECK (role IN ('admin', 'hr', 'finance', 'sales', 'support', 'viewer')),
    allowed_tables  TEXT[] NOT NULL DEFAULT '{}',
    db_type         TEXT NOT NULL DEFAULT 'all',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (role, db_type)
);

-- Seed default RBAC policies
INSERT INTO rbac_policies (role, allowed_tables, db_type) VALUES
    ('hr',      ARRAY['employees', 'departments', 'payroll'],                      'all'),
    ('sales',   ARRAY['customers', 'orders', 'products', 'leads'],                 'all'),
    ('finance', ARRAY['invoices', 'expenses', 'budgets', 'transactions'],          'all'),
    ('support', ARRAY['tickets', 'users', 'responses'],                            'all'),
    ('viewer',  ARRAY[]::TEXT[],                                                   'all'),
    ('admin',   ARRAY[]::TEXT[],                                                   'all')  -- empty = unrestricted
ON CONFLICT (role, db_type) DO NOTHING;

-- ── Schema Cache ──────────────────────────────────────────────
-- Lightweight cache of the last-known schema per connection.
-- Used as fallback if ChromaDB is unavailable.
CREATE TABLE IF NOT EXISTS schema_cache (
    connection_id   UUID PRIMARY KEY REFERENCES database_connections(id) ON DELETE CASCADE,
    schema_json     JSONB NOT NULL,
    indexed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Automatic updated_at trigger ─────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ── Seed admin user (change password immediately in production) ──
-- Password hash below is bcrypt for "AdminPass123!" — REPLACE IN PROD
INSERT INTO users (email, password_hash, full_name, role)
VALUES (
    'admin@querysafe.io',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewplde8aFtO5rSDe',
    'QuerySafe Admin',
    'admin'
) ON CONFLICT (email) DO NOTHING;
