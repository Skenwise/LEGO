"""SessionRevoked Domain Event."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class SessionRevoked:
    """Emitted when a user session is revoked (logout or security)."""
    user_id: str
    session_id: str
    reason: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: str(uuid4()))
    
    def get_event_name(self) -> str:
        return "session.revoked"
