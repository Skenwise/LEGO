"""Shared Contracts - Public interfaces exposed to other modules.
Other modules import ONLY from this folder (Lego studs).
"""
from shared.dtos import (
    RegisterUserDto,
    AuthenticateUserDto,
    TokenResponseDto,
    RefreshTokenDto,
    RevokeSessionDto,
)
from shared.errors import DomainError

__all__ = [
    "RegisterUserDto",
    "AuthenticateUserDto",
    "TokenResponseDto", 
    "RefreshTokenDto",
    "RevokeSessionDto",
    "DomainError",
]
