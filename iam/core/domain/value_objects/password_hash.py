"""PasswordHash Value Object - Argon2id hash wrapper."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordHash:
    """Value Object for Argon2id password hash."""
    hash_value: str
    
    def __post_init__(self):
        if not self.hash_value or not self.hash_value.startswith('$argon2id'):
            raise ValueError("Invalid Argon2id hash format")
    
    @classmethod
    def from_string(cls, hash_str: str) -> "PasswordHash":
        return cls(hash_str)
    
    def __str__(self) -> str:
        return self.hash_value
