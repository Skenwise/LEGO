"""Argon2PasswordHasher - Implements IPasswordHasher port."""
import asyncio
from concurrent.futures import ThreadPoolExecutor

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from core.ports.driven.ipassword_hasher import IPasswordHasher


class Argon2PasswordHasher(IPasswordHasher):
    """Argon2id password hasher with configurable parameters.
    
    Parameters (per Security report):
    - memory_cost: 65536 (64 MB)
    - time_cost: 3 (iterations)
    - parallelism: 4 (threads)
    - hash_len: 32
    - salt_len: 32
    """
    
    def __init__(
        self,
        memory_cost: int = 65536,
        time_cost: int = 3,
        parallelism: int = 4,
        hash_len: int = 32,
        salt_len: int = 32,
    ):
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._ph = PasswordHasher(
            memory_cost=memory_cost,
            time_cost=time_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
        )
    
    async def hash(self, password: str) -> str:
        """Hash password using Argon2id."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._ph.hash,
            password
        )
    
    async def verify(self, password: str, hashed: str) -> bool:
        """Verify password against Argon2id hash."""
        loop = asyncio.get_event_loop()
        
        def _verify():
            try:
                self._ph.verify(hashed, password)
                return True
            except (VerifyMismatchError, VerificationError):
                return False
        
        return await loop.run_in_executor(self._executor, _verify)
    
    def needs_rehash(self, hashed: str) -> bool:
        """Check if hash needs rehashing (params changed)."""
        return self._ph.check_needs_rehash(hashed)
