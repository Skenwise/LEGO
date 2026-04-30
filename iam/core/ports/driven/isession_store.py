"""ISessionStore - Driven Port for session management (Redis/DB)."""
from abc import ABC, abstractmethod
from typing import Optional

from core.domain.entities import Session


class ISessionStore(ABC):
    """Session storage port (Redis implementation for production)."""
    
    @abstractmethod
    async def create(self, session: Session) -> Session:
        """Create new session."""
        raise NotImplementedError
    
    @abstractmethod
    async def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_refresh_token(self, refresh_token_id: str) -> Optional[Session]:
        """Get session by refresh token ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def revoke(self, session_id: str) -> None:
        """Revoke session."""
        raise NotImplementedError
    
    @abstractmethod
    async def revoke_all_for_user(self, user_id: str) -> None:
        """Revoke all user sessions."""
        raise NotImplementedError
