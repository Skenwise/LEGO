-- ISO 27001: 8-field audit schema (append-only)
CREATE TABLE IF NOT EXISTS audit_logs (
    event_id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    source_ip INET,
    result TEXT NOT NULL CHECK (result IN ('success', 'failure', 'denied')),
    metadata JSONB DEFAULT '{}',
    
    -- Indexes for forensic queries
    INDEX idx_audit_actor_time (actor_user_id, timestamp DESC),
    INDEX idx_audit_action_time (action, timestamp DESC),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_timestamp (timestamp)
);

-- Prevent deletion (application-level enforcement)
-- Production: Add RLS + separate read-only user for audit access
