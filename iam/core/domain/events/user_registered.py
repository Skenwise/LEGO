"""UserRegistered Domain Event."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class UserRegistered:
    """Emitted when a new user registers successfully."""
    user_id: str
    email: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: str(uuid4()))
    
    def get_event_name(self) -> str:
        return "user.registered"
