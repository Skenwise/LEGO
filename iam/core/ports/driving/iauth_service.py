"""IAuthService - Driving Port (called by HTTP/CLI adapters)."""
from abc import ABC, abstractmethod
from typing import Optional

from shared.dtos import RegisterUserDto, AuthenticateUserDto, TokenResponseDto, RefreshTokenDto


class IAuthService(ABC):
    """Primary port for authentication operations."""
    
    @abstractmethod
    async def register(self, dto: RegisterUserDto) -> TokenResponseDto:
        """Register new user and return token pair."""
        raise NotImplementedError
    
    @abstractmethod
    async def authenticate(self, dto: AuthenticateUserDto) -> TokenResponseDto:
        """Authenticate user (supports multiple strategies via provider field)."""
        raise NotImplementedError
    
    @abstractmethod
    async def refresh(self, dto: RefreshTokenDto) -> TokenResponseDto:
        """Refresh access token using refresh token (with rotation)."""
        raise NotImplementedError
    
    @abstractmethod
    async def revoke(self, user_id: str, session_id: str) -> None:
        """Revoke user session (logout)."""
        raise NotImplementedError
