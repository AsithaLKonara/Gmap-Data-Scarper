"""Tests for LinkedIn scraper."""
from unittest.mock import MagicMock, patch

import pytest

from scrapers.linkedin import LinkedInScraper


@patch("scrapers.linkedin.site_search")
@patch("scrapers.linkedin.HttpClient")
def test_linkedin_scraper_extracts_basic_info(mock_client_class, mock_site_search):
    """Test that LinkedIn scraper extracts basic info from company page."""
    # Mock site search
    mock_site_search.return_value = ["https://www.linkedin.com/company/test-company"]
    
    # Mock HTTP client
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <meta property="og:title" content="Test Company">
            <meta property="og:description" content="A great company with 1,234 followers">
        </head>
    </html>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    scraper = LinkedInScraper()
    results = list(scraper.search("test query", max_results=1))
    
    assert len(results) >= 1
    result = results[0]
    assert result["Platform"] == "linkedin"
    assert result["Profile URL"] == "https://www.linkedin.com/company/test-company"
    assert result["Display Name"] == "Test Company"
    assert result["Followers"] == "1,234"


@patch("scrapers.linkedin.site_search")
def test_linkedin_scraper_handles_no_candidates(mock_site_search):
    """Test that LinkedIn scraper handles no search results."""
    mock_site_search.return_value = []
    
    scraper = LinkedInScraper()
    results = list(scraper.search("test query", max_results=5))
    
    assert len(results) == 0


@patch("scrapers.linkedin.site_search")
@patch("scrapers.linkedin.HttpClient")
def test_linkedin_scraper_handles_extraction_errors(mock_client_class, mock_site_search):
    """Test that LinkedIn scraper handles extraction errors gracefully."""
    mock_site_search.return_value = ["https://www.linkedin.com/company/test-company"]
    
    # Mock HTTP client to raise exception
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("Network error")
    mock_client_class.return_value = mock_client
    
    scraper = LinkedInScraper()
    results = list(scraper.search("test query", max_results=1))
    
    # Should handle error gracefully and return empty or partial results
    assert isinstance(results, list)

