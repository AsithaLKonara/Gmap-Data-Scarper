"""Tests for X/Twitter scraper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.x_twitter import XScraper


@patch("scrapers.x_twitter.site_search")
@patch("scrapers.x_twitter.HttpClient")
def test_x_scraper_extracts_basic_info(mock_client_class, mock_site_search):
    """Test that X scraper extracts basic info from profile."""
    # Mock site search
    mock_site_search.return_value = ["https://twitter.com/testuser"]
    
    # Mock HTTP client
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="Test User (@testuser)">
            <meta property="og:description" content="A test user profile">
        </head>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = XScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    result = results[0]
    assert result["Platform"] == "x"
    assert result["Profile URL"] == "https://twitter.com/testuser"
    assert result["Display Name"] == "Test User (@testuser)"
    assert result["Handle"] == "testuser"


@patch("scrapers.x_twitter.site_search")
def test_x_scraper_filters_generic_urls(mock_site_search):
    """Test that X scraper filters out generic Twitter URLs."""
    # Mock site search with generic URLs
    mock_site_search.return_value = [
        "https://twitter.com/home",
        "https://twitter.com/explore",
        "https://twitter.com/login",
        "https://twitter.com/validuser",
    ]
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="Test">
        </head>
    </html>
    """
    
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    
    with patch("scrapers.x_twitter.HttpClient", return_value=mock_client):
        scraper = XScraper()
        results = list(scraper.search("test query", max_results=10))
        
        # Should only process validuser, not generic pages
        urls = [r["Profile URL"] for r in results]
        assert "https://twitter.com/validuser" in urls
        assert "https://twitter.com/home" not in urls
        assert "https://twitter.com/explore" not in urls


@patch("scrapers.x_twitter.site_search")
def test_x_scraper_handles_no_candidates(mock_site_search):
    """Test that X scraper handles no search results."""
    mock_site_search.return_value = []
    
    scraper = XScraper()
    results = list(scraper.search("test query", max_results=5))
    
    assert len(results) == 0


@patch("scrapers.x_twitter.site_search")
@patch("scrapers.x_twitter.HttpClient")
def test_x_scraper_extracts_handle_from_title(mock_client_class, mock_site_search):
    """Test that X scraper extracts handle from og:title."""
    mock_site_search.return_value = ["https://twitter.com/testuser"]
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="John Doe (@johndoe)">
        </head>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = XScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    assert results[0]["Handle"] == "johndoe"

