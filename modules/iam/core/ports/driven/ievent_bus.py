"""IEventBus - Driven Port for domain event propagation."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable


class IEventBus(ABC):
    """Event bus for decoupled side effects (audit, email, notifications)."""
    
    @abstractmethod
    async def publish(self, event: Any) -> None:
        """Publish domain event to all subscribers."""
        raise NotImplementedError
    
    @abstractmethod
    def subscribe(self, event_type: type, handler: Callable[[Any], Awaitable[None]]) -> None:
        """Subscribe handler to event type."""
        raise NotImplementedError
