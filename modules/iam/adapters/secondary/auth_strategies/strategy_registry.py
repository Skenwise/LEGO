"""StrategyRegistry - Implements IAuthStrategyRegistry."""
from typing import Dict, Optional

from core.ports.driven import IAuthStrategy, IAuthStrategyRegistry


class StrategyRegistry(IAuthStrategyRegistry):
    """Registry for authentication strategies."""
    
    def __init__(self):
        self._strategies: Dict[str, IAuthStrategy] = {}
    
    def register(self, strategy: IAuthStrategy) -> None:
        self._strategies[strategy.provider_name] = strategy
    
    def get(self, provider_name: str) -> Optional[IAuthStrategy]:
        return self._strategies.get(provider_name)
