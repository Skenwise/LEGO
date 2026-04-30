"""IPasswordHasher - Driven Port for password hashing (Argon2id)."""
from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Password hashing port (Argon2id with PBKDF2 fallback)."""
    
    @abstractmethod
    async def hash(self, password: str) -> str:
        """Hash password using Argon2id (or fallback)."""
        raise NotImplementedError
    
    @abstractmethod
    async def verify(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        raise NotImplementedError
    
    @abstractmethod
    def needs_rehash(self, hashed: str) -> bool:
        """Check if hash needs rehashing (parameter upgrade)."""
        raise NotImplementedError
