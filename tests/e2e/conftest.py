"""Pytest configuration and fixtures for E2E tests."""
import pytest
import asyncio
import os
import subprocess
import time
import requests
import signal
import sys
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from backend.main import app
from tests.e2e.fixtures.test_data import TestDataFixtures


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_queries():
    """Provide sample search queries."""
    return TestDataFixtures.get_sample_queries()


@pytest.fixture
def sample_scrape_request():
    """Provide sample scrape request."""
    return TestDataFixtures.get_sample_scrape_request()


@pytest.fixture
def sample_result():
    """Provide sample scrape result."""
    return TestDataFixtures.get_sample_result()


@pytest.fixture
def mock_websocket_message():
    """Provide mock WebSocket message."""
    return TestDataFixtures.get_mock_websocket_message()


@pytest.fixture
def test_csv_data():
    """Provide test CSV data for volume testing."""
    return TestDataFixtures.create_test_csv_data(100)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("CHROME_DEBUG_PORT", "9222")
    monkeypatch.setenv("STREAM_FPS", "2")
    monkeypatch.setenv("TASK_TIMEOUT_SECONDS", "3600")
    monkeypatch.setenv("OUTPUT_DIR", os.path.join(os.path.expanduser("~"), "test_social_leads"))
    monkeypatch.setenv("TESTING", "true")


# backend_server fixture is now in tests/conftest.py for shared access

