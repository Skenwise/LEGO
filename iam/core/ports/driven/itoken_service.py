"""ITokenService - Driven Port for JWT operations."""
from abc import ABC, abstractmethod
from typing import Optional

from core.domain.value_objects import TokenClaim


class ITokenService(ABC):
    """JWT token service port."""
    
    @abstractmethod
    async def create_access_token(self, claim: TokenClaim) -> str:
        """Create JWT access token."""
        raise NotImplementedError
    
    @abstractmethod
    async def create_refresh_token(self, claim: TokenClaim) -> tuple[str, str]:
        """Create refresh token and return (token, token_id)."""
        raise NotImplementedError
    
    @abstractmethod
    async def verify_token(self, token: str, token_type: str) -> Optional[TokenClaim]:
        """Verify and decode token, return claims if valid."""
        raise NotImplementedError
    
    @abstractmethod
    async def revoke_refresh_token(self, refresh_token_id: str) -> None:
        """Add refresh token to revocation list."""
        raise NotImplementedError
    
    @abstractmethod
    async def is_revoked(self, refresh_token_id: str) -> bool:
        """Check if refresh token is revoked."""
        raise NotImplementedError
