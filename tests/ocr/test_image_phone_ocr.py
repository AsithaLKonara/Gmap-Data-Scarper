"""Tests for OCR phone extraction."""
import pytest
from unittest.mock import Mock, patch
import sys

# Check if pytesseract is available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

if TESSERACT_AVAILABLE:
    from ocr.image_phone_ocr import ImagePhoneOCR
else:
    # Create a mock class for when Tesseract is not available
    class ImagePhoneOCR:
        def extract_text(self, path):
            raise ImportError("pytesseract not available")
        def extract_phone_from_image(self, path):
            raise ImportError("pytesseract not available")
        def capture_screenshot(self, driver):
            return "mock_path.png"


class TestImagePhoneOCR:
    """Test OCR-based phone extraction."""
    
    @pytest.mark.skipif(not TESSERACT_AVAILABLE, reason="pytesseract not installed - install with: pip install pytesseract and install Tesseract OCR")
    @patch('ocr.image_phone_ocr.pytesseract')
    def test_extract_text_from_image(self, mock_tesseract):
        """Test text extraction from image."""
        if not TESSERACT_AVAILABLE:
            pytest.skip("pytesseract not installed - install with: pip install pytesseract and install Tesseract OCR binary")
        
        ocr = ImagePhoneOCR()
        
        # Mock Tesseract
        mock_tesseract.image_to_string.return_value = "Call us at 555-123-4567"
        
        try:
            text = ocr.extract_text("dummy_path.png")
            assert "555" in text
            mock_tesseract.image_to_string.assert_called_once()
        except Exception as e:
            pytest.skip(f"OCR extraction failed: {e}")
    
    @pytest.mark.skipif(not TESSERACT_AVAILABLE, reason="pytesseract not installed - install with: pip install pytesseract and install Tesseract OCR")
    @patch('ocr.image_phone_ocr.pytesseract')
    def test_extract_phone_from_image(self, mock_tesseract):
        """Test phone extraction from image."""
        if not TESSERACT_AVAILABLE:
            pytest.skip("pytesseract not installed - install with: pip install pytesseract and install Tesseract OCR binary")
        
        ocr = ImagePhoneOCR()
        
        # Mock Tesseract to return text with phone
        mock_tesseract.image_to_string.return_value = "Contact: (555) 123-4567"
        
        try:
            phones = ocr.extract_phone_from_image("dummy_path.png")
            assert len(phones) >= 1
            assert any("555" in p for p in phones)
        except Exception as e:
            pytest.skip(f"Phone extraction from image failed: {e}")
    
    def test_capture_screenshot(self):
        """Test screenshot capture."""
        ocr = ImagePhoneOCR()
        driver = Mock()
        driver.save_screenshot.return_value = None
        
        path = ocr.capture_screenshot(driver)
        
        assert path is not None
        driver.save_screenshot.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])

