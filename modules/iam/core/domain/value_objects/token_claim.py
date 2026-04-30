"""TokenClaim Value Object - JWT claims wrapper."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

@dataclass(frozen=True)
class TokenClaim:
    """Value Object for JWT claims."""
    user_id: str
    expires_at: datetime
    token_type: str
    scopes: tuple[str, ...]
    
    @classmethod
    def create_access(cls, user_id: str, ttl_minutes: int = 15) -> "TokenClaim":
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        return cls(user_id, expires_at, "access", ("auth",))
    
    @classmethod
    def create_refresh(cls, user_id: str, ttl_days: int = 7) -> "TokenClaim":
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)
        return cls(user_id, expires_at, "refresh", ("refresh",))
    
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
