"""Tests for TikTok scraper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.tiktok import TikTokScraper


@patch("scrapers.tiktok.site_search")
@patch("scrapers.tiktok.HttpClient")
def test_tiktok_scraper_extracts_basic_info(mock_client_class, mock_site_search):
    """Test that TikTok scraper extracts basic info from profile."""
    # Mock site search
    mock_site_search.return_value = ["https://www.tiktok.com/@testuser"]
    
    # Mock HTTP client
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="Test User (@testuser)">
            <meta property="og:description" content="A test user profile">
        </head>
        <body>
            <div>1,234 Followers</div>
        </body>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = TikTokScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    result = results[0]
    assert result["Platform"] == "tiktok"
    assert result["Profile URL"] == "https://www.tiktok.com/@testuser"
    assert result["Display Name"] == "Test User (@testuser)"
    assert result["Handle"] == "testuser"
    assert result["Followers"] == "1,234"


@patch("scrapers.tiktok.site_search")
def test_tiktok_scraper_handles_no_candidates(mock_site_search):
    """Test that TikTok scraper handles no search results."""
    mock_site_search.return_value = []
    
    scraper = TikTokScraper()
    results = list(scraper.search("test query", max_results=5))
    
    assert len(results) == 0


@patch("scrapers.tiktok.site_search")
@patch("scrapers.tiktok.HttpClient")
def test_tiktok_scraper_extracts_handle_and_followers(mock_client_class, mock_site_search):
    """Test that TikTok scraper extracts handle and followers."""
    mock_site_search.return_value = ["https://www.tiktok.com/@johndoe"]
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="John Doe (@johndoe)">
        </head>
        <body>
            <div>9,876 Followers</div>
        </body>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = TikTokScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    assert results[0]["Handle"] == "johndoe"
    assert results[0]["Followers"] == "9,876"

