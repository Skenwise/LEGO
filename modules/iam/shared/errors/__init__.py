"""Shared Errors - Cross-module exception types."""
from .domain_errors import (
    DomainError,
    UserNotFoundError,
    InvalidCredentialsError,
    AccountLockedError,
    EmailAlreadyExistsError,
    InvalidTokenError,
    TokenRevokedError,
    MFANotEnabledError,
    MFAVerificationError,
    UnsupportedProviderError,
)

__all__ = [
    "DomainError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "AccountLockedError",
    "EmailAlreadyExistsError",
    "InvalidTokenError",
    "TokenRevokedError",
    "MFANotEnabledError",
    "MFAVerificationError",
    "UnsupportedProviderError",
]
