"""ICredentialRepository - Driven Port for auth_schema (ISO 8.27 isolation)."""
from abc import ABC, abstractmethod
from typing import Optional

from core.domain.entities import Credential


class ICredentialRepository(ABC):
    """Repository for Credential aggregate (isolated auth_schema)."""
    
    @abstractmethod
    async def get_by_identity_id(self, identity_id: str) -> Optional[Credential]:
        """Get credentials by identity ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, credential: Credential) -> Credential:
        """Save or update credentials."""
        raise NotImplementedError
    
    @abstractmethod
    async def update_failed_attempts(self, identity_id: str, attempts: int) -> None:
        """Update failed login counter."""
        raise NotImplementedError
    
    @abstractmethod
    async def lock_account(self, identity_id: str, locked_until) -> None:
        """Lock account due to too many failed attempts."""
        raise NotImplementedError
