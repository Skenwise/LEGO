"""SimpleEventBus - In-memory domain event bus (MVP)."""
import asyncio
from typing import Dict, List, Callable, Awaitable, Any

from core.ports.driven.ievent_bus import IEventBus


class SimpleEventBus(IEventBus):
    """In-memory event bus for domain events.
    
    MVP implementation. Production: Replace with Redis Streams or RabbitMQ.
    """
    
    def __init__(self):
        self._subscribers: Dict[type, List[Callable[[Any], Awaitable[None]]]] = {}
    
    async def publish(self, event: Any) -> None:
        """Publish event to all registered subscribers."""
        event_type = type(event)
        if event_type in self._subscribers:
            await asyncio.gather(
                *[handler(event) for handler in self._subscribers[event_type]]
            )
    
    def subscribe(self, event_type: type, handler: Callable[[Any], Awaitable[None]]) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
