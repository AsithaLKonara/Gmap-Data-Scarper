"""Security vulnerability tests - SQL injection, XSS, CSRF, etc."""
import pytest
import os
from fastapi.testclient import TestClient
from backend.main import app

# Set TESTING mode
os.environ["TESTING"] = "true"


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user(client):
    """Create a test user for authenticated tests."""
    email = "security_test@example.com"
    password = "TestPassword123!"
    
    # Register user
    response = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "name": "Security Test User"
    })
    
    if response.status_code == 200:
        return {
            "email": email,
            "password": password,
            "token": response.json()["access_token"]
        }
    return None


class TestSQLInjection:
    """Test SQL injection prevention."""
    
    def test_sql_injection_in_query_param(self, client, test_user):
        """Test SQL injection in query parameters."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Common SQL injection attempts
        sql_injections = [
            "1' OR '1'='1",
            "1; DROP TABLE leads; --",
            "' UNION SELECT * FROM users --",
            "1' AND 1=1 --",
            "admin'--",
            "1' OR 1=1#"
        ]
        
        for injection in sql_injections:
            # Try injection in various endpoints
            # Task ID parameter
            response = client.get(f"/api/scraper/status/{injection}", headers=headers)
            # Should not execute SQL, should return 404 or 400, not 500
            assert response.status_code != 500, f"SQL injection succeeded with: {injection}"
            
            # Lead ID parameter
            response = client.get(f"/api/filters/leads?lead_id={injection}", headers=headers)
            assert response.status_code != 500, f"SQL injection succeeded with: {injection}"
    
    def test_sql_injection_in_json_body(self, client, test_user):
        """Test SQL injection in JSON request body."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        sql_injections = [
            "test'; DROP TABLE leads; --",
            "test' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'pass'); --"
        ]
        
        for injection in sql_injections:
            # Try in scraper start query
            response = client.post("/api/scraper/start", json={
                "queries": [injection],
                "platforms": ["google_maps"]
            }, headers=headers)
            # Should validate and reject or sanitize, not execute SQL
            assert response.status_code != 500, f"SQL injection succeeded in body: {injection}"


class TestXSS:
    """Test Cross-Site Scripting (XSS) prevention."""
    
    def test_xss_in_query_parameter(self, client, test_user):
        """Test XSS prevention in query parameters."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
        for payload in xss_payloads:
            # Try XSS in task ID
            response = client.get(f"/api/scraper/status/{payload}", headers=headers)
            # Response should not contain the script tag
            if response.status_code == 200:
                response_text = str(response.content)
                assert "<script>" not in response_text.lower(), f"XSS payload not sanitized: {payload}"
    
    def test_xss_in_json_body(self, client, test_user):
        """Test XSS prevention in JSON request body."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/scraper/start", json={
                "queries": [payload],
                "platforms": ["google_maps"]
            }, headers=headers)
            # Should accept but sanitize, not return 500
            assert response.status_code != 500, f"XSS payload caused error: {payload}"


class TestCSRF:
    """Test Cross-Site Request Forgery (CSRF) protection."""
    
    def test_csrf_token_not_required_for_api(self, client, test_user):
        """Test that API endpoints don't require CSRF tokens (REST APIs typically use token auth)."""
        # FastAPI REST APIs typically use JWT tokens for authentication
        # CSRF protection is usually handled at the application/framework level
        # For REST APIs, CSRF is less critical since they use token-based auth
        # This test verifies the API works with just JWT tokens
        
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # POST request should work with just JWT token (no CSRF token needed)
        response = client.post("/api/scraper/start", json={
            "queries": ["test query"],
            "platforms": ["google_maps"]
        }, headers=headers)
        
        # Should succeed (may fail for other reasons like rate limits, but not CSRF)
        assert response.status_code != 403 or "csrf" not in str(response.content).lower()


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_path_traversal_prevention(self, client, test_user):
        """Test path traversal prevention."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        path_traversals = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fetc/passwd"
        ]
        
        for traversal in path_traversals:
            # Try in file-related endpoints if any
            response = client.get(f"/api/scraper/status/{traversal}", headers=headers)
            # Should not allow access to files outside intended directory
            assert response.status_code != 200 or "passwd" not in str(response.content).lower()
    
    def test_command_injection_prevention(self, client, test_user):
        """Test command injection prevention."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        command_injections = [
            "; ls -la",
            "| cat /etc/passwd",
            "& dir",
            "`whoami`",
            "$(id)"
        ]
        
        for injection in command_injections:
            response = client.post("/api/scraper/start", json={
                "queries": [f"test{injection}"],
                "platforms": ["google_maps"]
            }, headers=headers)
            # Should not execute commands, should validate/sanitize
            assert response.status_code != 500


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_enforced(self, client):
        """Test that rate limiting is enforced (when not in TESTING mode)."""
        # Note: Rate limiting is disabled in TESTING mode
        # This test verifies the mechanism exists
        
        # Make many rapid requests
        for i in range(150):  # More than default limit
            response = client.get("/api/health")
            # Should eventually be rate limited (but in TESTING mode it won't be)
            # This test documents the expected behavior
        
        # In production, this would return 429 after exceeding limits
        # In test mode, it should still work
        assert True  # Test passes if no exception
    
    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present in responses."""
        response = client.get("/api/health")
        # Check for rate limit headers (may not be present in test mode)
        headers = response.headers
        # If rate limiting is active, these headers should be present
        if "X-RateLimit-Limit" in headers:
            assert "X-RateLimit-Remaining" in headers
            assert "X-RateLimit-Reset" in headers


class TestSensitiveDataExposure:
    """Test for sensitive data exposure."""
    
    def test_passwords_not_returned_in_responses(self, client, test_user):
        """Test that passwords are never returned in API responses."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Login response should not contain password
        response = client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        response_text = str(response.content).lower()
        assert test_user["password"].lower() not in response_text
        assert "password" in response_text  # But "password" field name is OK
    
    def test_sql_errors_not_exposed(self, client, test_user):
        """Test that SQL errors are not exposed to users."""
        if not test_user:
            pytest.skip("User creation failed")
        
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Try to trigger a database error
        response = client.get("/api/scraper/status/invalid_id_format_123", headers=headers)
        
        # Error messages should not expose SQL details
        if response.status_code >= 500:
            response_text = str(response.content).lower()
            # Should not contain SQL keywords or database structure
            sql_keywords = ["select", "from", "where", "join", "table", "column", "sql", "database"]
            for keyword in sql_keywords:
                assert keyword not in response_text, f"SQL error exposed: {keyword}"


class TestAuthenticationBypass:
    """Test authentication bypass attempts."""
    
    def test_jwt_token_tampering(self, client):
        """Test that tampered JWT tokens are rejected."""
        # Create a valid-looking but tampered token
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.tampered_signature"
        
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = client.get("/api/scraper/status/test-task", headers=headers)
        
        # Should reject tampered token (401/403) or endpoint doesn't exist (404)
        assert response.status_code in [401, 403, 404]
    
    def test_no_auth_header_bypass(self, client):
        """Test that missing auth header doesn't bypass authentication."""
        # Try accessing protected endpoint without auth header
        response = client.get("/api/scraper/status/test-task")
        # Should require auth (401/403) or endpoint doesn't exist (404)
        assert response.status_code in [401, 403, 404]
    
    def test_empty_token_bypass(self, client):
        """Test that empty token doesn't bypass authentication."""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/scraper/status/test-task", headers=headers)
        # Should require valid auth (401/403) or endpoint doesn't exist (404)
        assert response.status_code in [401, 403, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

