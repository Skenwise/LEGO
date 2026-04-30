"""Credential Entity - Authentication secrets (auth_schema - ISO 8.27)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import uuid4

from ..value_objects import PasswordHash


@dataclass
class Credential:
    """User credentials - stored in separate auth_schema per ISO 8.27."""
    identity_id: str
    password_hash: PasswordHash
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False
    backup_codes_hash: Optional[str] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))
    
    MAX_FAILED_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 15
    
    def increment_failed_attempts(self) -> None:
        """Increment failed login counter and lock if threshold reached."""
        self.failed_attempts += 1
        self.updated_at = datetime.now(timezone.utc)
        
        if self.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.LOCK_DURATION_MINUTES)
    
    def reset_lock(self) -> None:
        """Reset failed attempts and unlock account."""
        self.failed_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.now(timezone.utc)
    
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        if datetime.now(timezone.utc) >= self.locked_until:
            self.reset_lock()
            return False
        return True
    
    def record_login(self) -> None:
        """Record successful login timestamp."""
        self.last_login_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def enable_mfa(self, secret: str, backup_codes_hash: str) -> None:
        """Enable MFA for this credential."""
        self.mfa_secret = secret
        self.mfa_enabled = True
        self.backup_codes_hash = backup_codes_hash
        self.updated_at = datetime.now(timezone.utc)
    
    def disable_mfa(self) -> None:
        """Disable MFA."""
        self.mfa_secret = None
        self.mfa_enabled = False
        self.backup_codes_hash = None
        self.updated_at = datetime.now(timezone.utc)
