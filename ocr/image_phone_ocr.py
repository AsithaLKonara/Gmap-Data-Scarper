"""OCR-based phone number extraction from images."""
import os
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from PIL import Image
import pytesseract


class ImagePhoneOCR:
    """Extracts text from page screenshots using OCR."""
    
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)
    
    def capture_screenshot(self, driver: WebDriver) -> Optional[str]:
        """Capture screenshot of current page."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
            
            driver.save_screenshot(screenshot_path)
            return screenshot_path
        except Exception as e:
            return None
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR."""
        try:
            # Pre-process image for better OCR
            image = Image.open(image_path)
            
            # Convert to grayscale
            if image.mode != "L":
                image = image.convert("L")
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Run OCR
            text = pytesseract.image_to_string(image, config="--psm 6")
            return text
        except Exception as e:
            # OCR not available or failed
            return ""
    
    def extract_phone_from_image(self, image_path: str) -> list:
        """Extract phone numbers from image."""
        import re
        
        text = self.extract_text(image_path)
        
        # Phone regex pattern (fixed - removed problematic nested groups)
        phone_regex = re.compile(r"""
            (?:\+?\d{1,3}[\s\-\.\(\)])?
            (?:\(?\d{1,4}\)?[\s\-\.\)]{0,2})?
            (?:\d{1,4}[\s\-\.\)]{0,2}){2,4}
            (?:\s*(?:ext|x|#|extension)\s*\d{1,5})?
        """, re.VERBOSE | re.IGNORECASE)
        
        matches = phone_regex.findall(text)
        return [match.strip() for match in matches if len(match.strip()) >= 10]

