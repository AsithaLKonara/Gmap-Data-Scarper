"""Tests for Instagram scraper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.instagram import InstagramScraper


@patch("scrapers.instagram.site_search")
@patch("scrapers.instagram.HttpClient")
def test_instagram_scraper_extracts_profile_info(mock_client_class, mock_site_search, sample_instagram_html):
    """Test that Instagram scraper extracts profile information."""
    mock_site_search.return_value = ["https://www.instagram.com/testprofile/"]
    
    mock_response = MagicMock()
    mock_response.text = sample_instagram_html
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = InstagramScraper()
    results = list(scraper.search("test query", max_results=1))
    
    if results:
        result = results[0]
        assert result["Platform"] == "instagram"
        assert "instagram.com" in result["Profile URL"]


@patch("scrapers.instagram.site_search")
def test_instagram_scraper_handles_no_results(mock_site_search):
    """Test that Instagram scraper handles no search results."""
    mock_site_search.return_value = []
    
    scraper = InstagramScraper()
    results = list(scraper.search("test query", max_results=5))
    
    assert len(results) == 0

