"""Unit tests for PasswordHash Value Object."""
import pytest
from core.domain.value_objects import PasswordHash


class TestPasswordHash:
    def test_valid_argon2id_hash_creates_successfully(self):
        hash_str = "$argon2id$v=19$m=65536,t=3,p=4$salt$hash"
        ph = PasswordHash.from_string(hash_str)
        assert str(ph) == hash_str
    
    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError, match="Invalid Argon2id hash"):
            PasswordHash.from_string("not-a-valid-hash")
    
    def test_empty_hash_raises_error(self):
        with pytest.raises(ValueError):
            PasswordHash.from_string("")
    
    def test_string_representation(self):
        hash_str = "$argon2id$v=19$m=65536,t=3,p=4$salt$hash"
        ph = PasswordHash.from_string(hash_str)
        assert str(ph) == hash_str
    
    def test_equality_same_hash(self):
        hash_str = "$argon2id$v=19$m=65536,t=3,p=4$salt$hash"
        ph1 = PasswordHash.from_string(hash_str)
        ph2 = PasswordHash.from_string(hash_str)
        assert ph1 == ph2
