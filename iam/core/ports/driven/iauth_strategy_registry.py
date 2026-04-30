"""IAuthStrategyRegistry - Driven Port for strategy lookup (Registry pattern)."""
from abc import ABC, abstractmethod
from typing import Optional

from .iauth_strategy import IAuthStrategy


class IAuthStrategyRegistry(ABC):
    """Registry for authentication strategies."""
    
    @abstractmethod
    def register(self, strategy: IAuthStrategy) -> None:
        """Register an authentication strategy."""
        raise NotImplementedError
    
    @abstractmethod
    def get(self, provider_name: str) -> Optional[IAuthStrategy]:
        """Get strategy by provider name."""
        raise NotImplementedError
