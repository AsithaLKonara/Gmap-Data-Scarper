"""Test configuration."""
import os

# Test environment flags
SKIP_NETWORK_TESTS = os.getenv("SKIP_NETWORK_TESTS", "false").lower() == "true"
SKIP_PERF_TESTS = os.getenv("SKIP_PERF_TESTS", "false").lower() == "true"
SKIP_EXTERNAL_API_TESTS = os.getenv("SKIP_EXTERNAL_API_TESTS", "false").lower() == "true"

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# Mock external services
MOCK_EXTERNAL_APIS = os.getenv("MOCK_EXTERNAL_APIS", "true").lower() == "true"
