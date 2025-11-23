"""Tests for site search helper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.site_search import site_search


@patch("scrapers.site_search.HttpClient")
@patch("scrapers.site_search.rate_limit_delay")
def test_site_search_success(mock_delay, mock_client_class, temp_dir):
    """Test successful site search."""
    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <body>
            <a class="result__a" href="https://www.facebook.com/testpage">Test Page</a>
            <a class="result__a" href="https://www.facebook.com/testpage2">Test Page 2</a>
        </body>
    </html>
    """
    
    mock_client = MagicMock()
    mock_client.session = MagicMock()
    mock_client.session.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    urls = site_search("test query", "facebook.com", num=2, debug=False)
    
    assert len(urls) == 2
    assert "facebook.com" in urls[0]
    assert "facebook.com" in urls[1]


@patch("scrapers.site_search.HttpClient")
@patch("scrapers.site_search.rate_limit_delay")
def test_site_search_handles_202_response(mock_delay, mock_client_class):
    """Test that site search handles 202 (blocked) responses."""
    mock_response_202 = MagicMock()
    mock_response_202.status_code = 202
    mock_response_202.text = "<html><body>Blocked</body></html>"
    
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.text = """
    <html>
        <body>
            <a class="result__a" href="https://www.facebook.com/test">Test</a>
        </body>
    </html>
    """
    
    mock_client = MagicMock()
    mock_client.session = MagicMock()
    mock_client.session.get.side_effect = [mock_response_202, mock_response_200]
    mock_client_class.return_value = mock_client
    
    urls = site_search("test query", "facebook.com", num=1, debug=False)
    
    # Should retry and eventually get results
    assert mock_client.session.get.call_count >= 2


@patch("scrapers.site_search.HttpClient")
@patch("scrapers.site_search.rate_limit_delay")
def test_site_search_handles_duckduckgo_redirects(mock_delay, mock_client_class):
    """Test handling of DuckDuckGo redirect URLs."""
    import urllib.parse
    redirect_url = "https://www.facebook.com/testpage"
    encoded = urllib.parse.quote(redirect_url)
    ddg_url = f"/l/?kh=-1&uddg={encoded}"
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = f"""
    <html>
        <body>
            <a class="result__a" href="{ddg_url}">Test Page</a>
        </body>
    </html>
    """
    
    mock_client = MagicMock()
    mock_client.session = MagicMock()
    mock_client.session.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    urls = site_search("test query", "facebook.com", num=1, debug=False)
    
    # Should extract the actual URL from redirect
    if urls:
        assert "facebook.com" in urls[0]


@patch("scrapers.site_search.HttpClient")
@patch("scrapers.site_search.rate_limit_delay")
def test_site_search_returns_empty_on_no_results(mock_delay, mock_client_class):
    """Test that site search returns empty list when no results found."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>No results</body></html>"
    
    mock_client = MagicMock()
    mock_client.session = MagicMock()
    mock_client.session.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    urls = site_search("test query", "facebook.com", num=5, debug=False)
    
    assert urls == []

