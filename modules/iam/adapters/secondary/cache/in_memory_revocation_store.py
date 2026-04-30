"""InMemoryRevocationStore - MVP implementation of IRevocationStore."""
from datetime import datetime
from typing import Dict, Set

from core.ports.driven.irevocation_store import IRevocationStore


class InMemoryRevocationStore(IRevocationStore):
    """In-memory revocation store (MVP only).
    
    WARNING: On server restart, all revocation records are lost.
    Production: Replace with Redis implementation.
    """
    
    def __init__(self):
        self._revoked: Dict[str, datetime] = {}
        self._user_revocations: Dict[str, Set[str]] = {}
    
    async def revoke(self, key: str, expires_at: datetime) -> None:
        """Revoke a key until expiration."""
        self._revoked[key] = expires_at
    
    async def is_revoked(self, key: str) -> bool:
        """Check if key is revoked and not expired."""
        if key not in self._revoked:
            return False
        
        expires_at = self._revoked[key]
        if datetime.utcnow() > expires_at:
            # Clean up expired
            del self._revoked[key]
            return False
        
        return True
    
    async def revoke_all_for_user(self, user_id: str) -> None:
        """Revoke all keys for a user (security incident)."""
        # Implementation: track keys per user
        if user_id in self._user_revocations:
            for key in self._user_revocations[user_id]:
                self._revoked[key] = datetime.utcnow()
