"""E2E Tests - Full authentication flow with real HTTP calls."""
import pytest
from fastapi.testclient import TestClient
import sys
import os
import time

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app


@pytest.mark.e2e
class TestFullAuthFlow:
    """End-to-end tests for complete user journey."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint_works(self, client):
        """Test: Health endpoint returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
        print("✅ Health check passed")
    
    def test_register_new_user(self, client):
        """Test: Register a new user."""
        unique_email = f"e2e-{int(time.time())}@example.com"
        
        response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        print(f"✅ Registration passed for {unique_email}")
    
    def test_login_with_correct_password(self, client):
        """Test: Login with correct credentials."""
        unique_email = f"login-{int(time.time())}@example.com"
        
        # Register first
        client.post("/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        
        # Then login
        response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        print(f"✅ Login passed for {unique_email}")
    
    def test_login_with_wrong_password_fails(self, client):
        """Test: Wrong password returns 401."""
        unique_email = f"wrong-{int(time.time())}@example.com"
        
        # Register first
        client.post("/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        
        # Try wrong password
        response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": "WrongPassword!"}
        )
        assert response.status_code == 401
        print("✅ Wrong password correctly rejected")
    
    def test_duplicate_registration_fails(self, client):
        """Test: Cannot register with same email twice."""
        unique_email = f"dup-{int(time.time())}@example.com"
        
        # First registration
        response1 = client.post("/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = client.post("/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert response2.status_code == 400
        assert "already registered" in response2.text.lower()
        print("✅ Duplicate registration correctly blocked")
    
    def test_weak_password_rejected(self, client):
        """Test: Password must be strong."""
        response = client.post(
            "/auth/register",
            json={"email": "weak@example.com", "password": "weak"}
        )
        assert response.status_code == 400
        print("✅ Weak password correctly rejected")
    
    def test_refresh_token_works(self, client):
        """Test: Refresh token returns new tokens."""
        unique_email = f"refresh-{int(time.time())}@example.com"
        
        # Register
        register_response = client.post("/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert register_response.status_code == 201
        refresh_token = register_response.json()["refresh_token"]
        
        # Wait a moment
        time.sleep(1)
        
        # Refresh
        refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        print("✅ Token refresh passed")
    
    def test_complete_user_journey(self, client):
        """Test: Complete flow - Register → Login → Refresh."""
        unique_email = f"journey-{int(time.time())}@example.com"
        
        # Step 1: Register
        register_resp = client.post("/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert register_resp.status_code == 201
        refresh_token = register_resp.json()["refresh_token"]
        print("✅ Step 1: Registration")
        
        # Step 2: Login
        login_resp = client.post("/auth/login", json={"email": unique_email, "password": "SecurePass123!"})
        assert login_resp.status_code == 200
        print("✅ Step 2: Login")
        
        # Step 3: Refresh
        refresh_resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 200
        print("✅ Step 3: Token Refresh")
        
        print("🎉 Complete user journey passed!")
