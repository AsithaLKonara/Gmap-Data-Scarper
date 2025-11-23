"""Phone number validation and normalization."""
from typing import Optional, Tuple
import phonenumbers
from phonenumbers import PhoneNumberFormat, is_valid_number, is_possible_number


class PhoneNormalizer:
    """Normalizes and validates phone numbers."""
    
    def __init__(self, default_region: str = "US"):
        self.default_region = default_region
    
    def normalize(
        self,
        raw_phone: str,
        region: Optional[str] = None
    ) -> Tuple[Optional[str], str]:
        """
        Normalize phone number to E.164 format.
        
        Returns:
            Tuple of (normalized_e164, validation_status)
            validation_status: "valid", "possible", or "invalid"
        """
        if not raw_phone:
            return None, "invalid"
        
        # Clean phone number (remove common separators but keep +)
        cleaned = self._clean_phone(raw_phone)
        
        if not cleaned:
            return None, "invalid"
        
        # Use provided region or default
        parse_region = region or self.default_region
        
        try:
            # Parse phone number
            parsed = phonenumbers.parse(cleaned, parse_region)
            
            # Check if valid
            if is_valid_number(parsed):
                normalized = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
                return normalized, "valid"
            elif is_possible_number(parsed):
                # Possible but not valid - format as international
                normalized = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
                return normalized, "possible"
            else:
                return None, "invalid"
        
        except phonenumbers.NumberParseException:
            # Could not parse
            return None, "invalid"
        except Exception:
            return None, "invalid"
    
    def _clean_phone(self, phone: str) -> str:
        """Clean phone number string."""
        # Remove common words that might be in phone numbers
        phone = phone.lower()
        phone = phone.replace("phone:", "").replace("tel:", "").replace("call:", "")
        phone = phone.replace("extension", "ext").replace("ext.", "ext")
        
        # Keep only digits, +, spaces, hyphens, parentheses, x (for extension)
        cleaned = ""
        for char in phone:
            if char.isdigit() or char in "+-() xX#":
                cleaned += char
        
        return cleaned.strip()
    
    def calculate_confidence(
        self,
        raw_phone: str,
        phone_source: str,
        validation_status: str
    ) -> int:
        """
        Calculate confidence score (0-100) based on source and validation.
        
        Args:
            raw_phone: Original phone text
            phone_source: Source of phone (tel_link, visible_text, jsonld, ocr, website)
            validation_status: Validation status (valid, possible, invalid)
        """
        base_scores = {
            "tel_link": 95,
            "jsonld": 85,
            "visible_text": 70,
            "website": 75,
            "ocr": 50,
        }
        
        base_score = base_scores.get(phone_source, 60)
        
        # Adjust based on validation
        if validation_status == "valid":
            return min(100, base_score + 10)
        elif validation_status == "possible":
            return max(0, base_score - 10)
        else:  # invalid
            return max(0, base_score - 30)

