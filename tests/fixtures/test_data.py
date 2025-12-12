"""Test data fixtures for use across test suites."""
from typing import Dict, List, Any

# Sample test users
TEST_USERS = [
    {
        "email": "test_user@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "user_id": "test_user_12345"
    },
    {
        "email": "admin_user@example.com",
        "password": "AdminPassword123!",
        "name": "Admin User",
        "user_id": "admin_user_12345"
    }
]

# Sample lead data
SAMPLE_LEADS = [
    {
        "email": "business1@example.com",
        "name": "Test Business 1",
        "phone": "+1234567890",
        "platform": "google_maps",
        "profile_url": "https://maps.google.com/business1",
        "lead_score": 85,
        "phones": [
            {"number": "+1234567890", "confidence": 0.9, "source": "DOM"}
        ]
    },
    {
        "email": "business2@example.com",
        "name": "Test Business 2",
        "phone": "+0987654321",
        "platform": "facebook",
        "profile_url": "https://facebook.com/business2",
        "lead_score": 65,
        "phones": [
            {"number": "+0987654321", "confidence": 0.7, "source": "text"}
        ]
    },
    {
        "email": "business3@example.com",
        "name": "Test Business 3",
        "platform": "linkedin",
        "profile_url": "https://linkedin.com/company/business3",
        "lead_score": 45,
        "phones": []
    }
]

# Sample task data
SAMPLE_TASKS = [
    {
        "task_id": "task_123456",
        "user_id": "test_user_12345",
        "queries": ["ICT students in Toronto"],
        "platforms": ["google_maps", "linkedin"],
        "status": "running",
        "created_at": "2025-01-01T00:00:00Z"
    },
    {
        "task_id": "task_789012",
        "user_id": "test_user_12345",
        "queries": ["restaurants in Colombo"],
        "platforms": ["facebook"],
        "status": "completed",
        "created_at": "2025-01-01T01:00:00Z"
    }
]

# Sample platform data
PLATFORMS = [
    "google_maps",
    "facebook",
    "instagram",
    "linkedin",
    "x_twitter",
    "youtube",
    "tiktok"
]

# Sample search queries
SEARCH_QUERIES = [
    "ICT students in Toronto",
    "restaurants in Colombo",
    "software companies in Silicon Valley",
    "fashion stores in New York",
    "hotels in Paris"
]

# Test API keys (these should be test/mock keys, not real ones)
TEST_API_KEYS = {
    "TWILIO_ACCOUNT_SID": "test_account_sid",
    "TWILIO_AUTH_TOKEN": "test_auth_token",
    "OPENAI_API_KEY": "sk-test-key-12345",
    "CLEARBIT_API_KEY": "test_clearbit_key",
    "GOOGLE_PLACES_API_KEY": "test_google_places_key",
}

# Test JWT tokens (for testing authentication)
def generate_test_token(user_id: str = "test_user_12345", email: str = "test@example.com") -> str:
    """Generate a test JWT token."""
    import jwt
    import os
    from datetime import datetime, timedelta
    
    secret = os.getenv("JWT_SECRET_KEY", "test_secret_key")
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, secret, algorithm="HS256")

# Test database URLs
import os
TEST_DATABASE_URLS = {
    "sqlite": "sqlite:///:memory:",
    "postgresql": os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost/test_db")
}

# Sample GDPR request data
GDPR_REQUESTS = {
    "data_access": {
        "email": "user@example.com",
        "profile_url": None
    },
    "data_deletion": {
        "email": "user@example.com",
        "profile_url": "https://facebook.com/user"
    },
    "opt_out": {
        "profile_url": "https://facebook.com/user",
        "email": "user@example.com"
    }
}

# Sample audit log entries
AUDIT_LOG_ENTRIES = [
    {
        "table_name": "leads",
        "record_id": "1",
        "action": "create",
        "user_id": "test_user_12345",
        "changes": None,
        "metadata": {"task_id": "task_123456"}
    },
    {
        "table_name": "leads",
        "record_id": "1",
        "action": "delete",
        "user_id": "test_user_12345",
        "changes": {"deleted_at": {"old": None, "new": "2025-01-01T00:00:00Z"}},
        "metadata": {}
    }
]

