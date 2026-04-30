"""E2E Tests - Direct HTTP API calls to running server."""
import pytest
import requests
import time

API_URL = "http://localhost:8005"


@pytest.mark.e2e
class TestAPIDirect:
    """End-to-end tests making real HTTP calls to the running server."""
    
    def test_health_endpoint_works(self):
        """Test: Health endpoint returns status."""
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
        print("\n✅ Health check passed")
    
    def test_register_new_user(self):
        """Test: Register a new user."""
        unique_email = f"e2e-{int(time.time())}@example.com"
        
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        print(f"\n✅ Registration passed for {unique_email}")
    
    def test_login_with_correct_password(self):
        """Test: Login with correct credentials."""
        unique_email = f"login-{int(time.time())}@example.com"
        
        # Register first
        requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        
        # Then login
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        print(f"\n✅ Login passed for {unique_email}")
    
    def test_login_with_wrong_password_fails(self):
        """Test: Wrong password returns 401."""
        unique_email = f"wrong-{int(time.time())}@example.com"
        
        # Register first
        requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        
        # Try wrong password
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": unique_email, "password": "WrongPassword!"}
        )
        assert response.status_code == 401
        print("\n✅ Wrong password correctly rejected")
    
    def test_duplicate_registration_fails(self):
        """Test: Cannot register with same email twice."""
        unique_email = f"dup-{int(time.time())}@example.com"
        
        # First registration
        response1 = requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert response2.status_code == 400
        assert "already registered" in response2.text.lower()
        print("\n✅ Duplicate registration correctly blocked")
    
    def test_weak_password_rejected(self):
        """Test: Password must be strong."""
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": "weak@example.com", "password": "weak"}
        )
        assert response.status_code == 422
        print("\n✅ Weak password correctly rejected")
    
    def test_refresh_token_works(self):
        """Test: Refresh token returns new tokens."""
        unique_email = f"refresh-{int(time.time())}@example.com"
        
        # Register
        register_response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert register_response.status_code == 201
        refresh_token = register_response.json()["refresh_token"]
        
        # Wait a moment
        time.sleep(1)
        
        # Refresh
        refresh_response = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        print("\n✅ Token refresh passed")
    
    def test_complete_user_journey(self):
        """Test: Complete flow - Register → Login → Refresh."""
        unique_email = f"journey-{int(time.time())}@example.com"
        
        # Step 1: Register
        register_resp = requests.post(
            f"{API_URL}/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert register_resp.status_code == 201
        refresh_token = register_resp.json()["refresh_token"]
        print("\n✅ Step 1: Registration")
        
        # Step 2: Login
        login_resp = requests.post(
            f"{API_URL}/auth/login",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert login_resp.status_code == 200
        print("✅ Step 2: Login")
        
        # Step 3: Refresh
        refresh_resp = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_resp.status_code == 200
        print("✅ Step 3: Token Refresh")
        
        print("\n🎉 Complete user journey passed!")
