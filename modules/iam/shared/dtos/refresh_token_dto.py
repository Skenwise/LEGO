"""RefreshTokenDto - Input DTO for token refresh."""
from pydantic import BaseModel, Field


class RefreshTokenDto(BaseModel):
    """DTO for refresh token request."""
    
    refresh_token: str
    
    model_config = {
        'extra': 'forbid',
    }
