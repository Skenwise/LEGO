"""AuthenticateUserDto - Input DTO for authentication."""
from pydantic import BaseModel, Field


class AuthenticateUserDto(BaseModel):
    """DTO for user authentication request."""
    
    email: str = Field(..., min_length=3, max_length=255)
    password: str
    provider: str = Field(default="local", pattern=r"^(local|google|github|saml)$")
    mfa_token: str | None = Field(None, min_length=6, max_length=8)
    
    model_config = {
        'extra': 'forbid',
        'str_strip_whitespace': True,
    }
