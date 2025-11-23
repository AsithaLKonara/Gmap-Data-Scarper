"""Tests for base scraper interface."""
import pytest

from scrapers.base import BaseScraper, COMMON_FIELDS


class ConcreteScraper(BaseScraper):
    """Concrete implementation for testing."""
    name = "test_scraper"
    
    def search(self, query: str, max_results: int):
        """Mock search implementation."""
        yield {
            "Search Query": query,
            "Platform": self.name,
            "Profile URL": "https://example.com/test",
            "Handle": "test",
            "Display Name": "Test Business",
        }


def test_base_scraper_interface():
    """Test that base scraper interface works correctly."""
    scraper = ConcreteScraper()
    
    assert scraper.name == "test_scraper"
    assert scraper.platform_name() == "test_scraper"
    
    results = list(scraper.search("test query", 1))
    assert len(results) == 1
    assert results[0]["Search Query"] == "test query"
    assert results[0]["Platform"] == "test_scraper"


def test_common_fields_defined():
    """Test that COMMON_FIELDS contains expected fields."""
    expected_fields = [
        "Search Query",
        "Platform",
        "Profile URL",
        "Handle",
        "Display Name",
        "Bio/About",
        "Website",
        "Email",
        "Phone",
        "Followers",
        "Location",
    ]
    
    for field in expected_fields:
        assert field in COMMON_FIELDS, f"{field} not in COMMON_FIELDS"


def test_scraper_normalize_method():
    """Test that normalize method can be overridden."""
    scraper = ConcreteScraper()
    
    raw_result = {"test": "data"}
    normalized = scraper.normalize(raw_result)
    
    # Default implementation should return as-is
    assert normalized == raw_result

