"""Tests for phone normalizer."""
import pytest
from normalize.phone_normalizer import PhoneNormalizer


class TestPhoneNormalizer:
    """Test phone normalization functionality."""
    
    def test_normalize_us_phone(self):
        """Test normalization of US phone number."""
        normalizer = PhoneNormalizer()
        
        raw = "(555) 123-4567"
        normalized, status = normalizer.normalize(raw, "US")
        
        assert status in ["valid", "possible"]
        assert normalized is not None
        assert normalized.startswith("+1")
    
    def test_normalize_international(self):
        """Test normalization of international phone."""
        normalizer = PhoneNormalizer()
        
        raw = "+44 20 7946 0958"
        normalized, status = normalizer.normalize(raw, "GB")
        
        assert status in ["valid", "possible"]
        assert normalized is not None
        assert normalized.startswith("+44")
    
    def test_normalize_invalid(self):
        """Test normalization of invalid phone."""
        normalizer = PhoneNormalizer()
        
        raw = "123"
        normalized, status = normalizer.normalize(raw, "US")
        
        assert status == "invalid"
        assert normalized is None
    
    def test_calculate_confidence(self):
        """Test confidence score calculation."""
        normalizer = PhoneNormalizer()
        
        # High confidence for valid tel: link
        score1 = normalizer.calculate_confidence("+1234567890", "tel_link", "valid")
        assert score1 >= 90
        
        # Lower confidence for OCR
        score2 = normalizer.calculate_confidence("555-1234", "ocr", "possible")
        assert score2 < score1


if __name__ == "__main__":
    pytest.main([__file__])

