"""ISecretManagerPort - Driven Port for secret management (Vault/Env)."""
from abc import ABC, abstractmethod
from typing import Optional


class ISecretManagerPort(ABC):
    """Secret management port - MVP: env vars, Production: HashiCorp Vault."""
    
    @abstractmethod
    async def get_secret(self, name: str) -> str:
        """Retrieve secret by name."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_secret_or_none(self, name: str) -> Optional[str]:
        """Retrieve secret, return None if not found."""
        raise NotImplementedError
    
    @abstractmethod
    async def rotate_secret(self, name: str) -> bool:
        """Trigger secret rotation (Vault integration)."""
        raise NotImplementedError
