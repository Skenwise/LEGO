"""RegisterUser Use Case - Creates new user account."""
from typing import Optional

from core.domain.entities import Identity, Credential
from core.domain.value_objects import Email, PasswordHash
from core.domain.events import UserRegistered
from core.ports.driven import (
    IIdentityRepository,
    ICredentialRepository,
    IPasswordHasher,
    ITokenService,
    IAuditLogger,
    IEventBus,
)
from shared.dtos import RegisterUserDto, TokenResponseDto
from shared.errors import EmailAlreadyExistsError


class RegisterUser:
    """Handles user registration with dual-schema persistence (ISO 8.27)."""
    
    def __init__(
        self,
        identity_repo: IIdentityRepository,
        credential_repo: ICredentialRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        audit_logger: IAuditLogger,
        event_bus: IEventBus,
    ):
        self._identity_repo = identity_repo
        self._credential_repo = credential_repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._audit_logger = audit_logger
        self._event_bus = event_bus
    
    async def execute(self, dto: RegisterUserDto, source_ip: Optional[str] = None) -> TokenResponseDto:
        """Register a new user and return JWT token pair."""
        
        # 1. Validate email doesn't exist
        email = Email.create(dto.email)
        if await self._identity_repo.email_exists(email):
            await self._audit_logger.log_auth_failure(
                email=dto.email,
                action="register.failed",
                source_ip=source_ip,
                reason="email_already_exists",
            )
            raise EmailAlreadyExistsError(f"Email {dto.email} already registered")
        
        # 2. Hash password
        hashed_password = await self._password_hasher.hash(dto.password)
        password_hash = PasswordHash.from_string(hashed_password)
        
        # 3. Create domain entities
        identity = Identity(email=email, display_name=dto.display_name)
        credential = Credential(identity_id=identity.id, password_hash=password_hash)
        
        # 4. Persist with compensating action (Architect requirement)
        saved_identity = None
        try:
            saved_identity = await self._identity_repo.save(identity)
            credential.identity_id = saved_identity.id
            await self._credential_repo.save(credential)
        except Exception as e:
            # COMPENSATING ACTION: Rollback identity if credential save fails
            if saved_identity:
                await self._identity_repo.delete(saved_identity.id)
            raise e
        
        # 5. Generate JWT tokens
        from core.domain.value_objects.token_claim import TokenClaim
        
        access_claim = TokenClaim.create_access(user_id=saved_identity.id)
        refresh_claim = TokenClaim.create_refresh(user_id=saved_identity.id)
        
        access_token = await self._token_service.create_access_token(access_claim)
        refresh_token, refresh_id = await self._token_service.create_refresh_token(refresh_claim)
        
        # 6. Emit domain event
        await self._event_bus.publish(UserRegistered(
            user_id=saved_identity.id,
            email=saved_identity.email.value,
        ))
        
        # 7. Audit log
        await self._audit_logger.log_auth_success(
            user_id=saved_identity.id,
            action="register.success",
            source_ip=source_ip,
        )
        
        return TokenResponseDto(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900,
            refresh_expires_in=604800,
        )
