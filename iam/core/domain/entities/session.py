"""Session Entity - Active user sessions."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class Session:
    """User session - stored in Redis or auth_schema."""
    user_id: str
    refresh_token_id: str
    expires_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_revoked: bool = False
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def revoke(self) -> None:
        """Revoke this session."""
        self.is_revoked = True
    
    def is_active(self) -> bool:
        """Check if session is active (not expired and not revoked)."""
        return not self.is_expired() and not self.is_revoked
