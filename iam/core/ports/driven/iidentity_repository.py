"""IIdentityRepository - Driven Port for profile_schema operations."""
from abc import ABC, abstractmethod
from typing import Optional

from core.domain.entities import Identity
from core.domain.value_objects import Email


class IIdentityRepository(ABC):
    """Repository for Identity aggregate (profile_schema - ISO 8.27)."""
    
    @abstractmethod
    async def get_by_id(self, identity_id: str) -> Optional[Identity]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[Identity]:
        raise NotImplementedError
    
    @abstractmethod
    async def email_exists(self, email: Email) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, identity: Identity) -> Identity:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, identity_id: str) -> None:
        """Delete identity (compensating action for rollback)."""
        raise NotImplementedError
