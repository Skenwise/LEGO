"""IAuthStrategy - Driven Port for multi-provider authentication (Strategy Pattern)."""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class AuthResult:
    """Authentication result from strategy."""
    success: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class IAuthStrategy(ABC):
    """Authentication strategy interface (Local, Google, GitHub, SAML)."""
    
    @abstractmethod
    async def authenticate(self, credentials: dict) -> AuthResult:
        """Authenticate using provider-specific logic."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (e.g., 'local', 'google', 'github')."""
        raise NotImplementedError
