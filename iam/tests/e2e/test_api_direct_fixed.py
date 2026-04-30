"""E2E Tests - Direct HTTP API calls with rate limit handling."""
import pytest
import requests
import time

API_URL = "http://localhost:8005"


@pytest.mark.e2e
class TestAPIDirect:
    """End-to-end tests with rate limit awareness."""
    
    def test_health_endpoint_works(self):
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        print("\n✅ Health check passed")
    
    def test_register_new_user(self):
        unique_email = f"e2e-{int(time.time())}@example.com"
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert response.status_code == 201
        print(f"\n✅ Registration passed for {unique_email}")
        time.sleep(1)  # Avoid rate limit
    
    def test_login_with_correct_password(self):
        unique_email = f"login-{int(time.time())}@example.com"
        requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        time.sleep(0.5)
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert response.status_code == 200
        print(f"\n✅ Login passed for {unique_email}")
        time.sleep(0.5)
    
    def test_login_with_wrong_password_fails(self):
        unique_email = f"wrong-{int(time.time())}@example.com"
        requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        time.sleep(0.5)
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": unique_email, "password": "WrongPassword!"}
        )
        assert response.status_code == 401
        print("\n✅ Wrong password correctly rejected")
        time.sleep(0.5)
    
    def test_duplicate_registration_fails(self):
        unique_email = f"dup-{int(time.time())}@example.com"
        response1 = requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert response1.status_code == 201
        time.sleep(0.5)
        response2 = requests.post(f"{API_URL}/auth/register", json={"email": unique_email, "password": "SecurePass123!"})
        assert response2.status_code == 400
        print("\n✅ Duplicate registration correctly blocked")
        time.sleep(0.5)
    
    def test_weak_password_rejected(self):
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": "weak@example.com", "password": "weak"}
        )
        # Pydantic validation returns 422 for invalid data
        assert response.status_code == 422
        print("\n✅ Weak password correctly rejected (422)")
        time.sleep(0.5)
    
    def test_refresh_token_works(self):
        unique_email = f"refresh-{int(time.time())}@example.com"
        register_response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert register_response.status_code == 201
        refresh_token = register_response.json()["refresh_token"]
        time.sleep(2)  # Wait for rate limit window
        refresh_response = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        print("\n✅ Token refresh passed")
    
    def test_complete_user_journey(self):
        unique_email = f"journey-{int(time.time())}@example.com"
        
        # Register
        register_resp = requests.post(
            f"{API_URL}/auth/register",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert register_resp.status_code == 201
        refresh_token = register_resp.json()["refresh_token"]
        print("\n✅ Step 1: Registration")
        time.sleep(2)  # Wait for rate limit
        
        # Login
        login_resp = requests.post(
            f"{API_URL}/auth/login",
            json={"email": unique_email, "password": "SecurePass123!"}
        )
        assert login_resp.status_code == 200
        print("✅ Step 2: Login")
        time.sleep(1)
        
        # Refresh
        refresh_resp = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_resp.status_code == 200
        print("✅ Step 3: Token Refresh")
        
        print("\n🎉 Complete user journey passed!")
