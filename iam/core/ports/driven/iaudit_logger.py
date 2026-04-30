"""IAuditLogger - Driven Port for security audit logging (ISO 27001)."""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
from uuid import uuid4


class AuditResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


@dataclass
class AuditEvent:
    """Audit event with 8 mandatory fields per Security report."""
    action: str
    resource_type: str
    result: AuditResult
    actor_user_id: Optional[str] = None
    resource_id: Optional[str] = None
    source_ip: Optional[str] = None
    metadata: Optional[dict] = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)


class IAuditLogger(ABC):
    """Audit logger port - append-only, immutable storage."""
    
    @abstractmethod
    async def log(self, event: AuditEvent) -> None:
        """Write immutable audit record."""
        raise NotImplementedError
    
    @abstractmethod
    async def log_auth_success(self, user_id: str, action: str, source_ip: Optional[str] = None) -> None:
        """Convenience: log successful authentication."""
        pass
    
    @abstractmethod
    async def log_auth_failure(self, email: str, action: str, source_ip: Optional[str] = None, reason: str = "") -> None:
        """Convenience: log failed authentication attempt."""
        pass
