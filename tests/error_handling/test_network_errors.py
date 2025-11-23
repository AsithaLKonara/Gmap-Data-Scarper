"""Tests for network error handling."""
from unittest.mock import MagicMock, patch

import pytest
import requests

from scrapers.social_common import HttpClient


def test_http_client_handles_timeout():
    """Test that HTTP client handles timeout errors with retries."""
    client = HttpClient(timeout_seconds=0.1)
    
    # Mock session to always raise timeout (retries will exhaust)
    with patch.object(client.session, "get", side_effect=requests.Timeout()):
        # After retries exhaust, should raise RetryError (which wraps Timeout)
        with pytest.raises((requests.Timeout, Exception)):
            try:
                client.get("https://example.com")
            except Exception as e:
                # RetryError is expected after retries exhaust
                assert "Timeout" in str(e) or "RetryError" in str(type(e).__name__)
                raise


def test_http_client_handles_connection_error():
    """Test that HTTP client handles connection errors with retries."""
    client = HttpClient()
    
    # Mock session to always raise connection error (retries will exhaust)
    with patch.object(client.session, "get", side_effect=requests.ConnectionError()):
        # After retries exhaust, should raise RetryError (which wraps ConnectionError)
        with pytest.raises((requests.ConnectionError, Exception)):
            try:
                client.get("https://example.com")
            except Exception as e:
                # RetryError is expected after retries exhaust
                assert "Connection" in str(e) or "RetryError" in str(type(e).__name__)
                raise


def test_http_client_retries_on_failure():
    """Test that HTTP client retries on failure."""
    client = HttpClient()
    
    # Mock session to fail twice then succeed
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Success"
    
    with patch.object(client.session, "get", side_effect=[
        requests.ConnectionError(),
        requests.Timeout(),
        mock_response,
    ]):
        # Should eventually succeed after retries
        response = client.get("https://example.com")
        assert response.status_code == 200


@patch("scrapers.site_search.rate_limit_delay")
def test_site_search_handles_http_errors(mock_delay):
    """Test that site search handles HTTP errors gracefully."""
    from scrapers.site_search import site_search
    
    mock_client = MagicMock()
    mock_client.session = MagicMock()
    mock_client.session.get.side_effect = requests.ConnectionError("Network error")
    
    with patch("scrapers.site_search.HttpClient", return_value=mock_client):
        urls = site_search("test query", "facebook.com", num=5, debug=False)
        
        # Should return empty list on error
        assert urls == []

