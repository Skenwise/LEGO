"""Integration test: Dual-schema transaction rollback (Architect requirement)."""
import pytest
from unittest.mock import AsyncMock

from core.use_cases.register_user import RegisterUser
from core.domain.entities import Identity, Credential
from core.domain.value_objects import Email, PasswordHash
from shared.dtos import RegisterUserDto


@pytest.mark.integration
class TestDualSchemaTransaction:
    """Critical scenario: If credential save fails, identity must be rolled back."""
    
    @pytest.mark.asyncio
    async def test_identity_rolled_back_when_credential_fails(self):
        """When credential_repo.save() fails, identity_repo.delete() must be called."""
        
        mock_identity_repo = AsyncMock()
        mock_credential_repo = AsyncMock()
        mock_hasher = AsyncMock()
        mock_token_service = AsyncMock()
        mock_audit_logger = AsyncMock()
        mock_event_bus = AsyncMock()
        
        saved_identity = Identity(email=Email.create("test@example.com"))
        saved_identity.id = "saved-identity-id"
        
        mock_identity_repo.save.return_value = saved_identity
        mock_identity_repo.email_exists.return_value = False
        mock_identity_repo.delete = AsyncMock()
        mock_credential_repo.save.side_effect = Exception("Database connection failed")
        mock_hasher.hash.return_value = "$argon2id$v=19$hash"
        mock_token_service.create_access_token.return_value = "access-token"
        mock_token_service.create_refresh_token.return_value = ("refresh-token", "refresh-id")
        
        register_user = RegisterUser(
            identity_repo=mock_identity_repo,
            credential_repo=mock_credential_repo,
            password_hasher=mock_hasher,
            token_service=mock_token_service,
            audit_logger=mock_audit_logger,
            event_bus=mock_event_bus
        )
        
        dto = RegisterUserDto(email="test@example.com", password="SecurePass123!")
        
        with pytest.raises(Exception, match="Database connection failed"):
            await register_user.execute(dto, None)
        
        # CRITICAL: Identity must be deleted (compensating action)
        mock_identity_repo.delete.assert_called_once()
        mock_credential_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_both_schemas_saved_on_success(self):
        """When both saves succeed, no rollback occurs."""
        
        mock_identity_repo = AsyncMock()
        mock_credential_repo = AsyncMock()
        mock_hasher = AsyncMock()
        mock_token_service = AsyncMock()
        mock_audit_logger = AsyncMock()
        mock_event_bus = AsyncMock()
        
        saved_identity = Identity(email=Email.create("test@example.com"))
        saved_identity.id = "saved-identity-id"
        
        mock_identity_repo.save.return_value = saved_identity
        mock_identity_repo.email_exists.return_value = False
        mock_credential_repo.save.return_value = Credential(
            identity_id="saved-identity-id",
            password_hash=PasswordHash.from_string("$argon2id$v=19$hash")
        )
        mock_hasher.hash.return_value = "$argon2id$v=19$hash"
        mock_token_service.create_access_token.return_value = "access-token"
        mock_token_service.create_refresh_token.return_value = ("refresh-token", "refresh-id")
        mock_identity_repo.delete = AsyncMock()
        
        register_user = RegisterUser(
            identity_repo=mock_identity_repo,
            credential_repo=mock_credential_repo,
            password_hasher=mock_hasher,
            token_service=mock_token_service,
            audit_logger=mock_audit_logger,
            event_bus=mock_event_bus
        )
        
        dto = RegisterUserDto(email="test@example.com", password="SecurePass123!")
        
        result = await register_user.execute(dto, None)
        
        # Verify delete was NOT called
        mock_identity_repo.delete.assert_not_called()
        
        # Verify tokens returned
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
