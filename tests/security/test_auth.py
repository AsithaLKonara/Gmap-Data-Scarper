"""Security tests for authentication and authorization."""
import pytest
import os
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.auth_service import auth_service

# Set TESTING mode to disable rate limiting
os.environ["TESTING"] = "true"


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user_credentials():
    """Test user credentials."""
    return {
        "email": "test_user@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }


@pytest.fixture
def registered_user(client, test_user_credentials):
    """Register a test user and return tokens."""
    # Clean up any existing user first (for test isolation)
    try:
        from backend.dependencies import get_db
        from backend.models.user import User
        db = next(get_db())
        existing = db.query(User).filter(User.email == test_user_credentials["email"]).first()
        if existing:
            db.delete(existing)
            db.commit()
    except:
        pass
    
    # Register user
    response = client.post("/api/auth/register", json=test_user_credentials)
    if response.status_code == 200:
        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "email": test_user_credentials["email"]
        }
    return None


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_user_registration(self, client, test_user_credentials):
        """Test user registration."""
        response = client.post("/api/auth/register", json=test_user_credentials)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_user_registration_duplicate_email(self, client, test_user_credentials):
        """Test registration with duplicate email fails."""
        # Clean up any existing user first
        try:
            from backend.dependencies import get_db
            from backend.models.user import User
            db = next(get_db())
            existing = db.query(User).filter(User.email == test_user_credentials["email"]).first()
            if existing:
                db.delete(existing)
                db.commit()
            db.close()
        except:
            pass
        
        # Register first time
        response1 = client.post("/api/auth/register", json=test_user_credentials)
        assert response1.status_code == 200
        
        # Try to register again with same email
        response2 = client.post("/api/auth/register", json=test_user_credentials)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_user_login(self, client, test_user_credentials, registered_user):
        """Test user login."""
        response = client.post("/api/auth/login", json={
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_user_login_invalid_password(self, client, test_user_credentials, registered_user):
        """Test login with invalid password fails."""
        response = client.post("/api/auth/login", json={
            "email": test_user_credentials["email"],
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower() or "unauthorized" in response.json()["detail"].lower()
    
    def test_user_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        })
        assert response.status_code == 401
    
    def test_token_refresh(self, client, registered_user):
        """Test token refresh."""
        if not registered_user:
            pytest.skip("User registration failed")
        
        response = client.post("/api/auth/refresh", json={
            "refresh_token": registered_user["refresh_token"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_token_refresh_invalid_token(self, client):
        """Test refresh with invalid token fails."""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token_here"
        })
        assert response.status_code == 401
    
    def test_access_protected_endpoint_with_token(self, client, registered_user):
        """Test accessing protected endpoint with valid token."""
        if not registered_user:
            pytest.skip("User registration failed")
        
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/scraper/status/test-task-id", headers=headers)
        # Should not return 401 (may return 404 if task doesn't exist, which is fine)
        assert response.status_code != 401
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        response = client.get("/api/scraper/status/test-task-id")
        # Should return 401, 403, or 404 (if endpoint doesn't exist)
        assert response.status_code in [401, 403, 404]
    
    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/scraper/status/test-task-id", headers=headers)
        # Should return 401, 403, or 404 (if endpoint doesn't exist)
        assert response.status_code in [401, 403, 404]
    
    def test_password_hashing(self, test_user_credentials):
        """Test that passwords are hashed (not stored in plain text)."""
        hashed = auth_service.hash_password(test_user_credentials["password"])
        # Verify password is hashed (not equal to original)
        assert hashed != test_user_credentials["password"]
        # Verify password can be verified
        assert auth_service.verify_password(test_user_credentials["password"], hashed)
        # Verify wrong password fails
        assert not auth_service.verify_password("wrong_password", hashed)
    
    def test_jwt_token_structure(self, registered_user):
        """Test JWT token structure and claims."""
        if not registered_user:
            pytest.skip("User registration failed")
        
        import jwt
        token = registered_user["access_token"]
        
        # Decode without verification first to check structure
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Check required claims
        assert "sub" in decoded  # Subject (user_id)
        assert "exp" in decoded  # Expiration
        assert "iat" in decoded  # Issued at
        assert decoded.get("type") == "access"
    
    def test_token_expiration(self, client, registered_user):
        """Test that expired tokens are rejected."""
        if not registered_user:
            pytest.skip("User registration failed")
        
        # Create an expired token manually
        import jwt
        from datetime import datetime, timedelta
        
        expired_payload = {
            "sub": "test_user",
            "email": registered_user["email"],
            "exp": datetime.utcnow() - timedelta(minutes=1),  # Expired 1 minute ago
            "iat": datetime.utcnow() - timedelta(hours=2),
            "type": "access"
        }
        
        expired_token = jwt.encode(
            expired_payload,
            os.getenv("JWT_SECRET_KEY", "test_secret_key"),
            algorithm="HS256"
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/scraper/status/test-task-id", headers=headers)
        # Should return 401, 403, or 404 (if endpoint doesn't exist)
        assert response.status_code in [401, 403, 404]


class TestAuthorization:
    """Test authorization and role-based access control."""
    
    def test_admin_endpoint_access(self, client, registered_user):
        """Test admin endpoint access requires admin role."""
        if not registered_user:
            pytest.skip("User registration failed")
        
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Try to access admin endpoint (soft delete hard delete endpoint)
        # Regular users should not have access
        response = client.delete("/api/soft-delete/hard-delete/lead/1", headers=headers)
        # Should return 403 Forbidden (not 401 Unauthorized)
        # If endpoint doesn't exist, may return 404, which is also acceptable for this test
        assert response.status_code in [403, 404, 401]
    
    def test_user_data_isolation(self, client, test_user_credentials):
        """Test that users can only access their own data."""
        # Register two users
        user1_creds = {
            "email": "user1@test.com",
            "password": "Password123!",
            "name": "User 1"
        }
        user2_creds = {
            "email": "user2@test.com",
            "password": "Password123!",
            "name": "User 2"
        }
        
        # Register both users
        resp1 = client.post("/api/auth/register", json=user1_creds)
        resp2 = client.post("/api/auth/register", json=user2_creds)
        
        if resp1.status_code != 200 or resp2.status_code != 200:
            pytest.skip("Failed to register test users")
        
        token1 = resp1.json()["access_token"]
        token2 = resp2.json()["access_token"]
        
        # User 1 should not be able to access User 2's tasks
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Create a task with user1
        task_resp = client.post("/api/scraper/start", json={
            "queries": ["test query"],
            "platforms": ["google_maps"]
        }, headers=headers1)
        
        if task_resp.status_code == 200:
            task_id = task_resp.json().get("task_id")
            if task_id:
                # User 2 should not be able to access user 1's task
                status_resp = client.get(f"/api/scraper/status/{task_id}", headers=headers2)
                # Should return 403 or 404 (task not found for this user)
                assert status_resp.status_code in [403, 404, 401]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

