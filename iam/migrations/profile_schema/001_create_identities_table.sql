-- Profile Schema: User identities (less sensitive data)
CREATE SCHEMA IF NOT EXISTS profile_schema;

CREATE TABLE profile_schema.identities (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_identities_email ON profile_schema.identities(email);
CREATE INDEX idx_identities_active ON profile_schema.identities(is_active);
