"""Pytest configuration and shared fixtures."""
import os
import tempfile
import subprocess
import sys
import time
import requests
from pathlib import Path
from typing import Generator

import pytest
import yaml

# Sample test data
SAMPLE_QUERY = "hotels in kandy"
SAMPLE_QUERIES = [
    "hotels in kandy",
    "restaurants in colombo",
    "shops in galle",
]

SAMPLE_CONFIG = {
    "enabled_platforms": ["facebook", "instagram", "linkedin"],
    "max_results_per_query": 5,
    "headless": True,
    "per_platform_delay_seconds": 2,
    "resume": True,
    "output_dir": "~/Documents/test_leads",
}

SAMPLE_HTML_FACEBOOK = """
<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="Test Hotel Page">
    <meta property="og:description" content="A great hotel in Kandy">
    <title>Test Hotel Page</title>
</head>
<body>
    <div>1,234 people follow this</div>
</body>
</html>
"""

SAMPLE_HTML_INSTAGRAM = """
<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="Test Hotel (@test_hotel) • Instagram photos and videos">
    <meta property="og:description" content="1,234 Followers, 567 Following">
</head>
</html>
"""


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test files using pytest's tmp_path."""
    # tmp_path is pytest's built-in fixture that provides a temporary directory
    # with proper permissions and automatic cleanup
    return tmp_path


@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """Create a temporary config.yaml file."""
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(SAMPLE_CONFIG, f)
    return config_path


@pytest.fixture
def temp_queries_file(temp_dir: Path) -> Path:
    """Create a temporary queries file."""
    queries_path = temp_dir / "queries.txt"
    with open(queries_path, "w", encoding="utf-8") as f:
        f.write("\n".join(SAMPLE_QUERIES))
    return queries_path


@pytest.fixture
def temp_csv_file(temp_dir: Path) -> Path:
    """Create a temporary CSV file path."""
    return temp_dir / "test_output.csv"


@pytest.fixture
def sample_facebook_html() -> str:
    """Sample Facebook page HTML."""
    return SAMPLE_HTML_FACEBOOK


@pytest.fixture
def sample_instagram_html() -> str:
    """Sample Instagram page HTML."""
    return SAMPLE_HTML_INSTAGRAM


@pytest.fixture
def mock_requests_session(monkeypatch):
    """Mock requests session."""
    from unittest.mock import MagicMock
    mock_session = MagicMock()
    monkeypatch.setattr("requests.Session", lambda: mock_session)
    return mock_session


@pytest.fixture(scope="session")
def backend_server():
    """Start backend server as subprocess for E2E tests."""
    # Server configuration
    host = "0.0.0.0"
    port = 8000
    base_url = f"http://localhost:{port}"
    health_url = f"{base_url}/api/health"
    
    # Start server as subprocess
    server_process = None
    
    try:
        # Start uvicorn server as subprocess
        server_process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "backend.main:app",
                "--host", host,
                "--port", str(port),
                "--log-level", "warning"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "TESTING": "true"}
        )
        
        # Wait for server to be ready (max 30 seconds)
        max_wait = 30
        wait_interval = 0.5
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                response = requests.get(health_url, timeout=2)
                if response.status_code == 200:
                    print(f"Backend server started successfully at {base_url}")
                    yield base_url
                    return
            except (requests.exceptions.RequestException, ConnectionError):
                pass
            
            # Check if process is still alive
            if server_process.poll() is not None:
                # Process died
                stdout, stderr = server_process.communicate()
                raise RuntimeError(
                    f"Backend server process died. "
                    f"STDOUT: {stdout.decode() if stdout else 'None'}, "
                    f"STDERR: {stderr.decode() if stderr else 'None'}"
                )
            
            time.sleep(wait_interval)
            elapsed += wait_interval
        
        # If we get here, server didn't start
        raise RuntimeError(f"Backend server failed to start within {max_wait} seconds")
        
    finally:
        # Cleanup: Stop the server process
        if server_process:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            except Exception as e:
                print(f"Error stopping server: {e}")
        print("Backend server fixture cleanup")

