"""EnvSecretManager - Implements ISecretManagerPort using environment variables (MVP)."""
import os
from typing import Optional

from core.ports.driven.isecret_manager import ISecretManagerPort


class EnvSecretManager(ISecretManagerPort):
    """Secret manager backed by environment variables.
    
    MVP implementation. Production: Replace with HashiCorp Vault.
    """
    
    async def get_secret(self, name: str) -> str:
        """Get secret from environment variable. Raises error if missing."""
        value = os.environ.get(name)
        if value is None:
            raise ValueError(f"Secret '{name}' not found in environment")
        return value
    
    async def get_secret_or_none(self, name: str) -> Optional[str]:
        """Get secret or return None if not found."""
        return os.environ.get(name)
    
    async def rotate_secret(self, name: str) -> bool:
        """Trigger secret rotation.
        
        Note: MVP version doesn't support rotation.
        Production: Integrate with Vault's auto-rotation.
        """
        return False
