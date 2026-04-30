"""IRevocationStore - Driven Port for token/session revocation storage."""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class IRevocationStore(ABC):
    """Revocation store for tokens and sessions.
    
    MVP: In-memory implementation.
    Production: Redis with TTL + PostgreSQL audit backup.
    """
    
    @abstractmethod
    async def revoke(self, key: str, expires_at: datetime) -> None:
        """Revoke a token or session by key."""
        raise NotImplementedError
    
    @abstractmethod
    async def is_revoked(self, key: str) -> bool:
        """Check if a key has been revoked."""
        raise NotImplementedError
    
    @abstractmethod
    async def revoke_all_for_user(self, user_id: str) -> None:
        """Revoke all tokens/sessions for a user."""
        raise NotImplementedError
