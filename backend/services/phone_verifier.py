"""Phone verification service using Twilio Lookup API."""
import os
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path
import requests
from backend.utils.retry import retry


class PhoneVerifier:
    """Verifies phone numbers using Twilio Lookup API with caching."""
    
    def __init__(self, twilio_account_sid: Optional[str] = None, twilio_auth_token: Optional[str] = None):
        """
        Initialize phone verifier.
        
        Args:
            twilio_account_sid: Twilio Account SID (or from env TWILIO_ACCOUNT_SID)
            twilio_auth_token: Twilio Auth Token (or from env TWILIO_AUTH_TOKEN)
        """
        self.account_sid = twilio_account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = twilio_auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.api_enabled = bool(self.account_sid and self.auth_token)
        
        # Cache directory
        cache_dir = Path(os.path.expanduser("~/Documents/phone_verification_cache"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = cache_dir
        self.cache_ttl = 30 * 24 * 60 * 60  # 30 days in seconds
    
    def verify(self, phone_number: str) -> Dict[str, Any]:
        """
        Verify a phone number.
        
        Args:
            phone_number: Phone number in E.164 format (e.g., +15551234567)
        
        Returns:
            Dict with verification results:
            - is_valid: bool
            - carrier: str (e.g., "Verizon", "AT&T")
            - line_type: str ("mobile", "landline", "voip", "unknown")
            - country_code: str
            - national_format: str
            - cached: bool
            - verification_timestamp: str
        """
        # Check cache first
        cached_result = self._get_from_cache(phone_number)
        if cached_result:
            cached_result["cached"] = True
            return cached_result
        
        # If API not enabled, return basic validation
        if not self.api_enabled:
            return {
                "is_valid": True,  # Assume valid if we can't verify
                "carrier": "unknown",
                "line_type": "unknown",
                "country_code": self._extract_country_code(phone_number),
                "national_format": phone_number,
                "cached": False,
                "verification_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_enabled": False
            }
        
        # Call Twilio Lookup API
        try:
            result = self._lookup_twilio(phone_number)
            # Cache the result
            self._save_to_cache(phone_number, result)
            result["cached"] = False
            result["api_enabled"] = True
            return result
        except Exception as e:
            # On error, return basic info
            return {
                "is_valid": True,  # Assume valid on error
                "carrier": "unknown",
                "line_type": "unknown",
                "country_code": self._extract_country_code(phone_number),
                "national_format": phone_number,
                "cached": False,
                "verification_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_enabled": True,
                "error": str(e)
            }
    
    @retry(attempts=3, delay=1, exceptions=(requests.RequestException,))
    def _lookup_twilio(self, phone_number: str) -> Dict[str, Any]:
        """Lookup phone number using Twilio API."""
        url = f"https://lookups.twilio.com/v1/PhoneNumbers/{phone_number}"
        
        response = requests.get(
            url,
            auth=(self.account_sid, self.auth_token),
            params={"Type": "carrier"},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "is_valid": True,
            "carrier": data.get("carrier", {}).get("name", "unknown"),
            "line_type": data.get("carrier", {}).get("type", "unknown").lower(),
            "country_code": data.get("country_code", ""),
            "national_format": data.get("national_format", phone_number),
            "verification_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def _get_from_cache(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get verification result from cache."""
        cache_file = self.cache_dir / f"{phone_number.replace('+', '')}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = cached_data.get("verification_timestamp", 0)
            if isinstance(cache_time, str):
                cache_time = time.mktime(time.strptime(cache_time, "%Y-%m-%d %H:%M:%S"))
            
            if time.time() - cache_time > self.cache_ttl:
                # Cache expired, delete file
                cache_file.unlink()
                return None
            
            return cached_data
        except Exception:
            return None
    
    def _save_to_cache(self, phone_number: str, result: Dict[str, Any]) -> None:
        """Save verification result to cache."""
        cache_file = self.cache_dir / f"{phone_number.replace('+', '')}.json"
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass  # Cache write failure is not critical
    
    def _extract_country_code(self, phone_number: str) -> str:
        """Extract country code from phone number."""
        if phone_number.startswith("+"):
            # Try to extract country code (1-3 digits after +)
            import re
            match = re.match(r'\+(\d{1,3})', phone_number)
            if match:
                return match.group(1)
        return ""
    
    def update_confidence_score(
        self,
        original_confidence: int,
        verification_result: Dict[str, Any]
    ) -> int:
        """
        Update confidence score based on verification result.
        
        Args:
            original_confidence: Original confidence score (0-100)
            verification_result: Result from verify() method
        
        Returns:
            Updated confidence score (0-100)
        """
        if not verification_result.get("is_valid"):
            return max(0, original_confidence - 30)
        
        # Boost confidence for verified mobile numbers
        if verification_result.get("line_type") == "mobile":
            return min(100, original_confidence + 10)
        
        # Boost confidence for verified landlines
        if verification_result.get("line_type") == "landline":
            return min(100, original_confidence + 5)
        
        # Slight boost for any verified number
        if verification_result.get("api_enabled", False):
            return min(100, original_confidence + 5)
        
        return original_confidence


# Global instance
_phone_verifier = None

def get_phone_verifier() -> PhoneVerifier:
    """Get or create global phone verifier instance."""
    global _phone_verifier
    if _phone_verifier is None:
        _phone_verifier = PhoneVerifier()
    return _phone_verifier

