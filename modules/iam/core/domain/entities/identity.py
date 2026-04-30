"""Identity Entity - User profile information (profile_schema)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from ..value_objects import Email


@dataclass
class Identity:
    """User identity aggregate - stored in profile_schema (ISO 8.27)."""
    email: Email
    display_name: Optional[str] = None
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.email_verified = True
        self.updated_at = datetime.now(timezone.utc)
    
    def update_display_name(self, new_name: str) -> None:
        """Update display name."""
        self.display_name = new_name.strip()
        self.updated_at = datetime.now(timezone.utc)
