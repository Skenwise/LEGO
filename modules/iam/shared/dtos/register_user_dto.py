"""RegisterUserDto - Input DTO for user registration."""
from pydantic import BaseModel, EmailStr, Field, model_validator
import re


class RegisterUserDto(BaseModel):
    """DTO for user registration request."""
    
    email: EmailStr
    password: str = Field(..., min_length=12)
    display_name: str | None = Field(None, max_length=100)
    
    @model_validator(mode='after')
    def validate_password_strength(self) -> 'RegisterUserDto':
        """Enforce password complexity per Security report."""
        pwd = self.password
        
        if not re.search(r'[A-Z]', pwd):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', pwd):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', pwd):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValueError('Password must contain at least one special character')
        
        return self
    
    model_config = {
        'extra': 'forbid',
        'str_strip_whitespace': True,
    }
