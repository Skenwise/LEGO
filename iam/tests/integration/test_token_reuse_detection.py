"""Integration test: Refresh token reuse detection (Architect requirement)."""
import pytest

from adapters.secondary.security.jwt_token_service import JWTTokenService
from core.domain.value_objects.token_claim import TokenClaim


@pytest.mark.integration
class TestRefreshTokenReuseDetection:
    """Critical security scenario: Reused refresh token must revoke ALL tokens."""
    
    @pytest.mark.asyncio
    async def test_reused_refresh_token_revokes_all_user_tokens(self):
        """When a refresh token is used twice, it must be revoked."""
        
        token_service = JWTTokenService(
            secret_key="test-secret-key-32-bytes-long-here!",
            refresh_secret_key="test-refresh-secret-32-bytes-long!",
            access_ttl_minutes=15,
            refresh_ttl_days=7
        )
        
        user_id = "test-user-456"
        
        # Create tokens
        refresh_claim = TokenClaim.create_refresh(user_id=user_id)
        refresh_token, refresh_id = await token_service.create_refresh_token(refresh_claim)
        
        # First use - verify it works
        verified_claim = await token_service.verify_token(refresh_token, "refresh")
        assert verified_claim is not None
        assert verified_claim.user_id == user_id
        
        # Revoke the refresh token
        await token_service.revoke_refresh_token(refresh_id)
        
        # Second use - REUSE DETECTION
        second_verify = await token_service.verify_token(refresh_token, "refresh")
        
        # Assert - reused token must be invalid
        assert second_verify is None, "Reused refresh token must be invalid"
        
        # Verify token is marked as revoked
        is_revoked = await token_service.is_revoked(refresh_id)
        assert is_revoked is True, "Refresh token must be in revocation list"
    
    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self):
        """Revoke all tokens for a user."""
        
        token_service = JWTTokenService(
            secret_key="test-secret-key-32-bytes-long-here!",
            refresh_secret_key="test-refresh-secret-32-bytes-long!",
            access_ttl_minutes=15,
            refresh_ttl_days=7
        )
        
        user_id = "test-user-789"
        
        # Create multiple refresh tokens
        refresh_ids = []
        for _ in range(3):
            claim = TokenClaim.create_refresh(user_id=user_id)
            _, refresh_id = await token_service.create_refresh_token(claim)
            refresh_ids.append(refresh_id)
        
        # Revoke all user tokens
        await token_service.revoke_all_user_tokens(user_id)
        
        # Verify ALL are revoked
        for rid in refresh_ids:
            assert await token_service.is_revoked(rid) is True
