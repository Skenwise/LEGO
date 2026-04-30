"""Domain Errors - Shared exception types."""


class DomainError(Exception):
    """Base domain exception."""
    pass


class UserNotFoundError(DomainError):
    """User not found in identity repository."""
    pass


class InvalidCredentialsError(DomainError):
    """Invalid email or password."""
    pass


class AccountLockedError(DomainError):
    """Account is locked due to too many failed attempts."""
    pass


class EmailAlreadyExistsError(DomainError):
    """Email already registered."""
    pass


class InvalidTokenError(DomainError):
    """Invalid or expired token."""
    pass


class TokenRevokedError(DomainError):
    """Token has been revoked (reuse detected)."""
    pass


class MFANotEnabledError(DomainError):
    """MFA not enabled for this user."""
    pass


class MFAVerificationError(DomainError):
    """Invalid MFA token."""
    pass


class UnsupportedProviderError(DomainError):
    """Authentication provider not supported."""
    pass
