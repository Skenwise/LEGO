"""IMailer - Driven Port for email notifications."""
from abc import ABC, abstractmethod
from typing import Optional


class IMailer(ABC):
    """Email sending port for welcome emails, password reset, etc."""
    
    @abstractmethod
    async def send_welcome_email(self, to_email: str, display_name: Optional[str] = None) -> bool:
        """Send welcome email after registration."""
        raise NotImplementedError
    
    @abstractmethod
    async def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        raise NotImplementedError
    
    @abstractmethod
    async def send_mfa_backup_codes(self, to_email: str, backup_codes: list[str]) -> bool:
        """Send MFA backup codes securely."""
        raise NotImplementedError
