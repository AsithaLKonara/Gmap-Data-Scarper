"""Tests for Facebook scraper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.facebook import FacebookScraper


@patch("scrapers.facebook.site_search")
@patch("scrapers.facebook.HttpClient")
def test_facebook_scraper_extracts_basic_info(mock_client_class, mock_site_search, sample_facebook_html):
    """Test that Facebook scraper extracts basic info from page."""
    # Mock site search
    mock_site_search.return_value = ["https://www.facebook.com/testpage"]
    
    # Mock HTTP client
    mock_response = MagicMock()
    mock_response.text = sample_facebook_html
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = FacebookScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    result = results[0]
    assert result["Platform"] == "facebook"
    assert result["Profile URL"] == "https://www.facebook.com/testpage"
    assert "Display Name" in result


@patch("scrapers.facebook.site_search")
def test_facebook_scraper_handles_login_pages(mock_site_search):
    """Test that Facebook scraper handles login pages."""
    mock_site_search.return_value = ["https://www.facebook.com/protected"]
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <title>Log in or sign up to view</title>
        </head>
    </html>
    """
    
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    
    with patch("scrapers.facebook.HttpClient", return_value=mock_client):
        scraper = FacebookScraper()
        results = list(scraper.search("test query", max_results=1))
        
        # Should still return minimal data from URL
        if results:
            assert results[0]["Profile URL"] == "https://www.facebook.com/protected"


@patch("scrapers.facebook.site_search")
def test_facebook_scraper_handles_no_candidates(mock_site_search):
    """Test that Facebook scraper handles no search results."""
    mock_site_search.return_value = []
    
    scraper = FacebookScraper()
    results = list(scraper.search("test query", max_results=5))
    
    assert len(results) == 0


def test_facebook_extract_handle_from_url():
    """Test handle extraction from Facebook URLs."""
    scraper = FacebookScraper()
    
    assert scraper._extract_handle_from_url("https://www.facebook.com/testpage") == "testpage"
    assert scraper._extract_handle_from_url("https://www.facebook.com/pages/Test/123456") == "123456"
    assert scraper._extract_handle_from_url("https://www.facebook.com/groups/123") == ""

