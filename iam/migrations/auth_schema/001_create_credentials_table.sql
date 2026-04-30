-- Auth Schema: Credentials (HIGHLY SENSITIVE - ISO 8.27 isolated)
CREATE SCHEMA IF NOT EXISTS auth_schema;

CREATE TABLE auth_schema.credentials (
    id UUID PRIMARY KEY,
    identity_id UUID NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    mfa_secret TEXT,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    backup_codes_hash TEXT,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_credentials_identity ON auth_schema.credentials(identity_id);
CREATE INDEX idx_credentials_locked ON auth_schema.credentials(locked_until);
