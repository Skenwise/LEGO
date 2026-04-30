"""PostgresAuditLogger - Implements IAuditLogger port with append-only storage."""
import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from core.ports.driven.iaudit_logger import IAuditLogger, AuditEvent, AuditResult


class PostgresAuditLogger(IAuditLogger):
    """PostgreSQL append-only audit logger with 8-field schema."""
    
    def __init__(self, db_pool):
        """Initialize with asyncpg connection pool."""
        self._pool = db_pool
    
    def _convert_uuid_to_str(self, value):
        """Convert UUID to string for PostgreSQL."""
        if isinstance(value, UUID):
            return str(value)
        return value
    
    async def log(self, event: AuditEvent) -> None:
        """Write immutable audit record."""
        # Convert UUIDs to strings
        actor_id = self._convert_uuid_to_str(event.actor_user_id)
        resource_id = self._convert_uuid_to_str(event.resource_id)
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_logs (
                    event_id, timestamp, actor_user_id, action,
                    resource_type, resource_id, source_ip, result, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                self._convert_uuid_to_str(event.event_id),
                event.timestamp,
                actor_id,
                event.action,
                event.resource_type,
                resource_id,
                event.source_ip,
                event.result.value,
                json.dumps(event.metadata or {}),
            )
    
    async def log_auth_success(
        self,
        user_id: str,
        action: str,
        source_ip: Optional[str] = None,
    ) -> None:
        """Log successful authentication."""
        event = AuditEvent(
            action=action,
            resource_type="auth",
            resource_id=user_id,
            result=AuditResult.SUCCESS,
            actor_user_id=user_id,
            source_ip=source_ip,
            metadata={"auth_method": "password"},
        )
        await self.log(event)
    
    async def log_auth_failure(
        self,
        email: str,
        action: str,
        source_ip: Optional[str] = None,
        reason: str = "",
    ) -> None:
        """Log failed authentication attempt."""
        event = AuditEvent(
            action=action,
            resource_type="auth",
            result=AuditResult.FAILURE,
            actor_user_id=None,
            source_ip=source_ip,
            metadata={"email": email, "reason": reason},
        )
        await self.log(event)
    
    async def log_mfa_event(
        self,
        user_id: str,
        action: str,
        result: AuditResult,
        source_ip: Optional[str] = None,
    ) -> None:
        """Log MFA verification events."""
        event = AuditEvent(
            action=f"mfa.{action}",
            resource_type="mfa",
            resource_id=user_id,
            result=result,
            actor_user_id=user_id,
            source_ip=source_ip,
        )
        await self.log(event)
    
    async def log_token_refresh(
        self,
        user_id: str,
        old_token_id: str,
        new_token_id: str,
        source_ip: Optional[str] = None,
    ) -> None:
        """Log token refresh with rotation."""
        event = AuditEvent(
            action="token.refresh",
            resource_type="token",
            resource_id=user_id,
            result=AuditResult.SUCCESS,
            actor_user_id=user_id,
            source_ip=source_ip,
            metadata={"old_token_id": old_token_id, "new_token_id": new_token_id},
        )
        await self.log(event)
