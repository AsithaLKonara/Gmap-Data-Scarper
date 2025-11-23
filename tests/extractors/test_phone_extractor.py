"""Tests for phone extractor."""
import pytest
from unittest.mock import Mock, MagicMock
from selenium.webdriver.remote.webdriver import WebDriver
from extractors.phone_extractor import PhoneExtractor


class TestPhoneExtractor:
    """Test phone extraction functionality."""
    
    def test_extract_tel_links(self):
        """Test extraction from tel: links."""
        extractor = PhoneExtractor()
        driver = Mock(spec=WebDriver)
        
        # Mock tel: link element
        tel_link = Mock()
        tel_link.get_attribute.return_value = "tel:+1234567890"
        tel_link.tag_name = "a"
        tel_link.get_property.return_value = None
        
        driver.find_elements.return_value = [tel_link]
        
        phones = extractor._extract_tel_links(driver)
        
        assert len(phones) == 1
        assert phones[0]["raw_phone"] == "+1234567890"
        assert phones[0]["phone_source"] == "tel_link"
        assert phones[0]["confidence_score"] == 95
    
    def test_extract_from_text(self):
        """Test extraction from visible text."""
        extractor = PhoneExtractor()
        driver = Mock(spec=WebDriver)
        
        # Mock body element with phone in text
        body = Mock()
        body.text = "Call us at (555) 123-4567 or 555-123-4568"
        driver.find_element.return_value = body
        
        phones = extractor._extract_from_text(driver)
        
        assert len(phones) >= 1
        assert any("555" in p["raw_phone"] for p in phones)
    
    def test_extract_from_jsonld(self):
        """Test extraction from JSON-LD."""
        extractor = PhoneExtractor()
        driver = Mock(spec=WebDriver)
        
        # Mock script element with JSON-LD
        script = Mock()
        script.get_attribute.return_value = '{"@type": "Organization", "telephone": "+1-555-123-4567"}'
        driver.find_elements.return_value = [script]
        
        phones = extractor._extract_from_jsonld(driver)
        
        assert len(phones) >= 1
        assert any("555" in p["raw_phone"] for p in phones)
        assert any(p["phone_source"] == "jsonld" for p in phones)
    
    def test_extract_from_driver_integration(self):
        """Test full extraction pipeline."""
        extractor = PhoneExtractor()
        driver = Mock(spec=WebDriver)
        
        # Mock various elements
        tel_link = Mock()
        tel_link.get_attribute.return_value = "tel:+1234567890"
        tel_link.tag_name = "a"
        tel_link.get_property.return_value = None
        
        body = Mock()
        body.text = "Contact: 555-123-4567"
        
        driver.find_elements.side_effect = [
            [tel_link],  # tel: links
            [body],      # body element
            []           # JSON-LD scripts
        ]
        driver.find_element.return_value = body
        
        phones = extractor.extract_from_driver(driver, "http://example.com")
        
        assert len(phones) >= 1
        # Should have tel: link
        assert any(p["phone_source"] == "tel_link" for p in phones)


if __name__ == "__main__":
    pytest.main([__file__])

