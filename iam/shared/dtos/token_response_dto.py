"""TokenResponseDto - Output DTO for authentication responses."""
from pydantic import BaseModel, Field


class TokenResponseDto(BaseModel):
    """DTO for token response after auth/refresh."""
    
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(default=900, description="Access token TTL in seconds (15 min)")
    refresh_expires_in: int = Field(default=604800, description="Refresh token TTL in seconds (7 days)")
    
    model_config = {
        'frozen': True,
        'json_schema_extra': {
            'example': {
                'access_token': 'eyJhbGciOiJIUzI1NiIs...',
                'refresh_token': 'eyJhbGciOiJIUzI1NiIs...',
                'token_type': 'Bearer',
                'expires_in': 900,
                'refresh_expires_in': 604800,
            }
        }
    }
