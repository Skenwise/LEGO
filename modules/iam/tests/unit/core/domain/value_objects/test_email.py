"""Unit tests for Email Value Object."""
import pytest
from core.domain.value_objects import Email


class TestEmail:
    def test_valid_email_creates_successfully(self):
        email = Email.create("test@example.com")
        assert email.value == "test@example.com"
    
    def test_email_normalized_to_lowercase(self):
        email = Email.create("Test@Example.COM")
        assert email.value == "test@example.com"
    
    def test_email_stripped(self):
        email = Email.create("  test@example.com  ")
        assert email.value == "test@example.com"
    
    def test_invalid_email_raises_error(self):
        with pytest.raises(ValueError, match="Invalid email"):
            Email.create("not-an-email")
    
    def test_email_without_at_raises_error(self):
        with pytest.raises(ValueError):
            Email.create("testexample.com")
    
    def test_email_with_double_at_raises_error(self):
        with pytest.raises(ValueError):
            Email.create("test@@example.com")
    
    def test_get_domain_returns_correct_part(self):
        email = Email.create("user@domain.com")
        assert email.get_domain() == "domain.com"
    
    def test_get_local_part_returns_correct_part(self):
        email = Email.create("user@domain.com")
        assert email.get_local_part() == "user"
    
    def test_string_representation(self):
        email = Email.create("test@example.com")
        assert str(email) == "test@example.com"
    
    def test_emails_with_subdomains_valid(self):
        email = Email.create("user@mail.subdomain.com")
        assert email.value == "user@mail.subdomain.com"
    
    def test_emails_with_plus_addressing_valid(self):
        email = Email.create("user+tag@example.com")
        assert email.value == "user+tag@example.com"
