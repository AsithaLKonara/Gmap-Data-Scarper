"""Test configuration and environment setup."""
import os
from pathlib import Path

# Test environment variables
TEST_ENV_VARS = {
    "TESTING": "true",
    "DISABLE_RATE_LIMIT": "true",
    "JWT_SECRET_KEY": "test_secret_key_for_jwt_tokens",
    "DATABASE_URL": os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:"),
    "API_URL": os.getenv("API_URL", "http://localhost:8000"),
}

def setup_test_environment():
    """Set up test environment variables."""
    for key, value in TEST_ENV_VARS.items():
        os.environ[key] = value

def teardown_test_environment():
    """Clean up test environment variables."""
    for key in TEST_ENV_VARS.keys():
        if key in os.environ:
            del os.environ[key]

# Test database configuration
TEST_DB_CONFIG = {
    "url": os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:"),
    "echo": False,
    "pool_pre_ping": True,
    "connect_args": {"check_same_thread": False} if "sqlite" in os.getenv("TEST_DATABASE_URL", "") else {}
}

