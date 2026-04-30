"""RevokeSessionDto - Input DTO for session revocation."""
from pydantic import BaseModel, Field


class RevokeSessionDto(BaseModel):
    """DTO for logout/revoke session request."""
    
    session_id: str
    reason: str = Field(default="logout", pattern=r"^(logout|password_change|security_alert)$")
    
    model_config = {
        'extra': 'forbid',
    }
