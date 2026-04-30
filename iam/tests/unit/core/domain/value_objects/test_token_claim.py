"""Unit tests for TokenClaim Value Object."""
from datetime import datetime, timedelta, timezone
from core.domain.value_objects import TokenClaim


class TestTokenClaim:
    def test_create_access_token_has_correct_defaults(self):
        claim = TokenClaim.create_access(user_id="user-123")
        assert claim.user_id == "user-123"
        assert claim.token_type == "access"
        assert "auth" in claim.scopes
    
    def test_create_access_token_expires_in_15_minutes(self):
        before = datetime.now(timezone.utc)
        claim = TokenClaim.create_access(user_id="user-123")
        after = datetime.now(timezone.utc)
        
        assert claim.expires_at > before + timedelta(minutes=14)
        assert claim.expires_at < after + timedelta(minutes=16)
    
    def test_create_refresh_token_expires_in_7_days(self):
        before = datetime.now(timezone.utc)
        claim = TokenClaim.create_refresh(user_id="user-123")
        after = datetime.now(timezone.utc)
        
        assert claim.expires_at > before + timedelta(days=6, hours=23)
        assert claim.expires_at < after + timedelta(days=7, hours=1)
    
    def test_is_expired_returns_false_for_future_token(self):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        claim = TokenClaim(
            user_id="user-123",
            expires_at=future,
            token_type="access",
            scopes=("auth",)
        )
        assert claim.is_expired() is False
    
    def test_is_expired_returns_true_for_past_token(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        claim = TokenClaim(
            user_id="user-123",
            expires_at=past,
            token_type="access",
            scopes=("auth",)
        )
        assert claim.is_expired() is True
    
    def test_custom_ttl_for_access_token(self):
        claim = TokenClaim.create_access(user_id="user-123", ttl_minutes=30)
        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
        assert abs((claim.expires_at - expected_expiry).total_seconds()) < 2
    
    def test_custom_ttl_for_refresh_token(self):
        claim = TokenClaim.create_refresh(user_id="user-123", ttl_days=14)
        expected_expiry = datetime.now(timezone.utc) + timedelta(days=14)
        assert abs((claim.expires_at - expected_expiry).total_seconds()) < 2
