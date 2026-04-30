"""LocalStrategy - Email/password authentication."""
from typing import Optional

from core.domain.value_objects import Email
from core.ports.driven import IIdentityRepository, ICredentialRepository, IPasswordHasher, IAuthStrategy, AuthResult


class LocalStrategy(IAuthStrategy):
    """Local email/password authentication strategy."""
    
    def __init__(
        self,
        identity_repo: IIdentityRepository,
        credential_repo: ICredentialRepository,
        password_hasher: IPasswordHasher,
    ):
        self._identity_repo = identity_repo
        self._credential_repo = credential_repo
        self._password_hasher = password_hasher
    
    @property
    def provider_name(self) -> str:
        return "local"
    
    async def authenticate(self, credentials: dict) -> AuthResult:
        """Authenticate with email and password."""
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            return AuthResult(success=False, error_message="Missing email or password")
        
        identity = await self._identity_repo.get_by_email(Email.create(email))
        if not identity:
            return AuthResult(success=False, error_message="Invalid credentials")
        
        credential = await self._credential_repo.get_by_identity_id(identity.id)
        if not credential:
            return AuthResult(success=False, error_message="Invalid credentials")
        
        is_valid = await self._password_hasher.verify(password, str(credential.password_hash))
        if not is_valid:
            return AuthResult(success=False, error_message="Invalid credentials")
        
        return AuthResult(
            success=True,
            user_id=identity.id,
            email=identity.email.value,
        )
