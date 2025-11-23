"""Tests for YouTube scraper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.youtube import YouTubeScraper


@patch("scrapers.youtube.site_search")
@patch("scrapers.youtube.HttpClient")
def test_youtube_scraper_extracts_basic_info(mock_client_class, mock_site_search):
    """Test that YouTube scraper extracts basic info from channel."""
    # Mock site search
    mock_site_search.return_value = ["https://www.youtube.com/channel/testchannel"]
    
    # Mock HTTP client
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="Test Channel">
            <meta property="og:description" content="A great channel">
        </head>
        <body>
            <div>1,234 subscribers</div>
        </body>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = YouTubeScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    result = results[0]
    assert result["Platform"] == "youtube"
    assert result["Profile URL"] == "https://www.youtube.com/channel/testchannel"
    assert result["Display Name"] == "Test Channel"
    assert result["Followers"] == "1,234"


@patch("scrapers.youtube.site_search")
def test_youtube_scraper_handles_no_candidates(mock_site_search):
    """Test that YouTube scraper handles no search results."""
    mock_site_search.return_value = []
    
    scraper = YouTubeScraper()
    results = list(scraper.search("test query", max_results=5))
    
    assert len(results) == 0


@patch("scrapers.youtube.site_search")
@patch("scrapers.youtube.HttpClient")
def test_youtube_scraper_extracts_subscribers(mock_client_class, mock_site_search):
    """Test that YouTube scraper extracts subscriber count."""
    mock_site_search.return_value = ["https://www.youtube.com/channel/testchannel"]
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="Test Channel">
        </head>
        <body>
            <div>5,678 subscribers</div>
        </body>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = YouTubeScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    assert results[0]["Followers"] == "5,678"

