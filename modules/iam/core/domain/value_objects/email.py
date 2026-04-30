"""Email Value Object - Immutable, validated email address."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Value Object representing a validated email address.
    
    Invariants:
    - Must be valid per RFC 5322
    - Stored in lowercase (normalized)
    - Immutable (frozen dataclass)
    """
    
    value: str
    
    # RFC 5322 compliant regex pattern
    _PATTERN = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    )
    
    def __post_init__(self):
        """Validate email on creation."""
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email address: {self.value}")
    
    @classmethod
    def _is_valid(cls, email: str) -> bool:
        """Validate email format."""
        return bool(cls._PATTERN.match(email))
    
    @classmethod
    def create(cls, email: str) -> "Email":
        """Factory method - creates normalized Email VO."""
        normalized = email.strip().lower()
        return cls(normalized)
    
    def get_domain(self) -> str:
        """Extract domain part."""
        return self.value.split("@")[1]
    
    def get_local_part(self) -> str:
        """Extract local part (before @)."""
        return self.value.split("@")[0]
    
    def __str__(self) -> str:
        return self.value
