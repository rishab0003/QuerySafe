-- OAuth accounts and admin approval workflow for employees

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS approval_status TEXT NOT NULL DEFAULT 'approved'
        CHECK (approval_status IN ('pending', 'approved', 'rejected'));

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;

-- OAuth users may not have a local password
ALTER TABLE users
    ALTER COLUMN password_hash DROP NOT NULL;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS refresh_token_jti TEXT;

CREATE TABLE IF NOT EXISTS oauth_accounts (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider          TEXT NOT NULL CHECK (provider IN ('google', 'github')),
    provider_user_id  TEXT NOT NULL,
    email             CITEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_user_id)
);

CREATE INDEX IF NOT EXISTS idx_oauth_accounts_user_id ON oauth_accounts (user_id);

-- Ensure seeded admin is approved
UPDATE users SET approval_status = 'approved', is_active = TRUE WHERE role = 'admin';
