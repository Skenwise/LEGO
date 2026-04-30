"""RevokeSession Use Case - Logout and session invalidation."""
from typing import Optional

from core.ports.driven import ISessionStore, IAuditLogger, ITokenService
from shared.dtos import RevokeSessionDto
from shared.errors import DomainError


class RevokeSession:
    """Handles session revocation (logout, security events)."""
    
    def __init__(
        self,
        session_store: ISessionStore,
        token_service: ITokenService,
        audit_logger: IAuditLogger,
    ):
        self._session_store = session_store
        self._token_service = token_service
        self._audit_logger = audit_logger
    
    async def execute(self, user_id: str, dto: RevokeSessionDto, source_ip: Optional[str] = None) -> None:
        """Revoke a user session."""
        
        session = await self._session_store.get(dto.session_id)
        if not session:
            raise DomainError(f"Session {dto.session_id} not found")
        
        if session.user_id != user_id:
            raise DomainError("Cannot revoke another user's session")
        
        await self._session_store.revoke(dto.session_id)
        
        # Also revoke the associated refresh token
        await self._token_service.revoke_refresh_token(session.refresh_token_id)
        
        # Audit log
        await self._audit_logger.log(
            event=type('AuditEvent', (), {
                'event_id': None,
                'timestamp': None,
                'actor_user_id': user_id,
                'action': f"session.revoked.{dto.reason}",
                'resource_type': 'session',
                'resource_id': dto.session_id,
                'source_ip': source_ip,
                'result': 'success',
                'metadata': {'reason': dto.reason}
            })()
        )
