"""AuthenticateUser Use Case - Verifies credentials and returns JWT."""
from typing import Optional

from core.domain.value_objects import Email
from core.ports.driven import (
    IIdentityRepository,
    ICredentialRepository,
    IPasswordHasher,
    ITokenService,
    IAuditLogger,
    IAuthStrategyRegistry,
)
from shared.dtos import AuthenticateUserDto, TokenResponseDto
from shared.errors import InvalidCredentialsError, AccountLockedError, UnsupportedProviderError
from core.domain.value_objects.token_claim import TokenClaim


class AuthenticateUser:
    """Handles user authentication with support for multiple providers (Strategy pattern)."""
    
    def __init__(
        self,
        identity_repo: IIdentityRepository,
        credential_repo: ICredentialRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        audit_logger: IAuditLogger,
        strategy_registry: IAuthStrategyRegistry,
    ):
        self._identity_repo = identity_repo
        self._credential_repo = credential_repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._audit_logger = audit_logger
        self._strategy_registry = strategy_registry
    
    async def execute(self, dto: AuthenticateUserDto, source_ip: Optional[str] = None) -> TokenResponseDto:
        """Authenticate user via provider strategy."""
        
        # Handle non-local providers (Google, GitHub, SAML)
        if dto.provider != "local":
            strategy = self._strategy_registry.get(dto.provider)
            if not strategy:
                await self._audit_logger.log_auth_failure(
                    email=dto.email,
                    action=f"auth.failed.{dto.provider}",
                    source_ip=source_ip,
                    reason="unsupported_provider",
                )
                raise UnsupportedProviderError(f"Provider {dto.provider} not supported")
            
            result = await strategy.authenticate({"token": dto.password})
            if not result.success:
                raise InvalidCredentialsError(result.error_message or "Authentication failed")
            
            identity = await self._identity_repo.get_by_email(Email.create(result.email))
            if not identity:
                raise InvalidCredentialsError("User not found")
            
            credential = await self._credential_repo.get_by_identity_id(identity.id)
        else:
            # Local authentication (email/password)
            email = Email.create(dto.email)
            identity = await self._identity_repo.get_by_email(email)
            if not identity:
                await self._audit_logger.log_auth_failure(
                    email=dto.email,
                    action="auth.failed",
                    source_ip=source_ip,
                    reason="user_not_found",
                )
                raise InvalidCredentialsError("Invalid email or password")
            
            credential = await self._credential_repo.get_by_identity_id(identity.id)
            if not credential:
                raise InvalidCredentialsError("Invalid credentials")
            
            # Check account lock
            if credential.is_locked():
                await self._audit_logger.log_auth_failure(
                    email=dto.email,
                    action="auth.failed",
                    source_ip=source_ip,
                    reason="account_locked",
                )
                raise AccountLockedError("Account is temporarily locked due to too many failed attempts")
            
            # Verify password
            is_valid = await self._password_hasher.verify(dto.password, str(credential.password_hash))
            if not is_valid:
                await self._credential_repo.update_failed_attempts(identity.id, credential.failed_attempts + 1)
                await self._audit_logger.log_auth_failure(
                    email=dto.email,
                    action="auth.failed",
                    source_ip=source_ip,
                    reason="invalid_password",
                )
                raise InvalidCredentialsError("Invalid email or password")
        
        # Reset failed attempts and lock on success (using correct method name)
        credential.reset_lock()
        credential.record_login()
        await self._credential_repo.save(credential)
        
        # Generate JWT tokens
        access_claim = TokenClaim.create_access(user_id=identity.id)
        refresh_claim = TokenClaim.create_refresh(user_id=identity.id)
        
        access_token = await self._token_service.create_access_token(access_claim)
        refresh_token, refresh_id = await self._token_service.create_refresh_token(refresh_claim)
        
        # Audit log success
        await self._audit_logger.log_auth_success(
            user_id=identity.id,
            action=f"auth.success.{dto.provider}",
            source_ip=source_ip,
        )
        
        return TokenResponseDto(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900,
            refresh_expires_in=604800,
        )
