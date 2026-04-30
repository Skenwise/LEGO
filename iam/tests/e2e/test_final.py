"""Final E2E Tests - With proper rate limit handling."""
import pytest
import requests
import time

API_URL = "http://localhost:8005"


@pytest.mark.e2e
class TestFinalE2E:
    
    def test_health_check(self):
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        print("✅ Health check passed")
    
    def test_full_registration_flow(self):
        email = f"final-{int(time.time())}@example.com"
        
        # Register
        resp = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": "SecurePass123!"})
        assert resp.status_code == 201
        print(f"✅ Registration: {email}")
        time.sleep(3)  # Wait for rate limit window
        
        # Login
        resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": "SecurePass123!"})
        assert resp.status_code == 200
        print("✅ Login successful")
        time.sleep(2)
        
        # Refresh
        refresh_token = resp.json()["refresh_token"]
        resp = requests.post(f"{API_URL}/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        print("✅ Refresh successful")
        
        print("🎉 Complete flow passed!")
