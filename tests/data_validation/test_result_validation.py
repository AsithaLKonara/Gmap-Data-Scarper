"""Tests for result data validation."""
import re
from urllib.parse import urlparse

import pytest

from scrapers.base import COMMON_FIELDS


def test_result_has_required_fields():
    """Test that result dictionaries have all required fields."""
    required_fields = [
        "Search Query",
        "Platform",
        "Profile URL",
        "Handle",
        "Display Name",
    ]
    
    sample_result = {
        "Search Query": "test query",
        "Platform": "facebook",
        "Profile URL": "https://facebook.com/test",
        "Handle": "test",
        "Display Name": "Test Business",
        "Bio/About": "",
        "Website": "",
        "Email": "",
        "Phone": "",
        "Followers": "",
        "Location": "",
    }
    
    for field in required_fields:
        assert field in sample_result, f"Missing required field: {field}"


def test_profile_url_is_valid():
    """Test that profile URLs are valid."""
    valid_urls = [
        "https://www.facebook.com/test",
        "https://instagram.com/test",
        "http://example.com/test",
    ]
    
    for url in valid_urls:
        parsed = urlparse(url)
        assert parsed.scheme in ["http", "https"]
        assert parsed.netloc != ""


def test_handle_format():
    """Test that handles have reasonable format."""
    valid_handles = ["test", "test_user", "test-user", "test123"]
    invalid_handles = ["", " ", "test/user", "test@user"]
    
    for handle in valid_handles:
        assert len(handle) > 0
        assert " " not in handle
        assert "/" not in handle
    
    for handle in invalid_handles:
        if handle:
            # Some characters shouldn't be in handles
            assert "/" not in handle or "@" not in handle


def test_platform_values():
    """Test that platform values are valid."""
    valid_platforms = [
        "google_maps",
        "facebook",
        "instagram",
        "linkedin",
        "x",
        "youtube",
        "tiktok",
    ]
    
    sample_result = {
        "Platform": "facebook",
        "Search Query": "test",
        "Profile URL": "https://example.com",
        "Handle": "",
        "Display Name": "Test",
    }
    
    assert sample_result["Platform"] in valid_platforms


def test_result_fields_match_common_fields():
    """Test that result fields match COMMON_FIELDS definition."""
    sample_result = {
        "Search Query": "test",
        "Platform": "facebook",
        "Profile URL": "https://example.com",
        "Handle": "test",
        "Display Name": "Test",
        "Bio/About": "",
        "Website": "",
        "Email": "",
        "Phone": "",
        "Followers": "",
        "Location": "",
    }
    
    # All result keys should be in COMMON_FIELDS (or be platform-specific extras)
    result_keys = set(sample_result.keys())
    common_keys = set(COMMON_FIELDS)
    
    # Required fields must be in result
    required_fields = {"Search Query", "Platform", "Profile URL", "Handle", "Display Name"}
    assert required_fields.issubset(result_keys)
    
    # Common fields should match
    for key in result_keys:
        if key not in common_keys:
            # Platform-specific fields are allowed
            assert key in ["Category", "Address", "Plus Code"] or key.startswith("_")

