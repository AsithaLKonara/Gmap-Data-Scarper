"""Business enrichment service for lead data enhancement."""
import os
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests
from backend.utils.retry import retry


class BusinessEnrichmentService:
    """Enriches business data with company information."""
    
    def __init__(
        self,
        clearbit_api_key: Optional[str] = None,
        google_places_api_key: Optional[str] = None
    ):
        """
        Initialize enrichment service.
        
        Args:
            clearbit_api_key: Clearbit API key (or from env CLEARBIT_API_KEY)
            google_places_api_key: Google Places API key (or from env GOOGLE_PLACES_API_KEY)
        """
        self.clearbit_api_key = clearbit_api_key or os.getenv("CLEARBIT_API_KEY")
        self.google_places_api_key = google_places_api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        
        # Cache directory
        cache_dir = Path(os.path.expanduser("~/Documents/enrichment_cache"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = cache_dir
        self.cache_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
    
    def enrich_business(
        self,
        business_name: str,
        website: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich business data with company information.
        
        Args:
            business_name: Name of the business
            website: Business website URL (optional)
            location: Business location (optional)
        
        Returns:
            Dict with enrichment data:
            - company_size: str (e.g., "1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001+")
            - industry: str
            - description: str
            - website: str
            - social_media: Dict with platform URLs
            - technology_stack: List of technologies
            - founded_year: int
            - revenue_range: str
            - employee_count: int
            - enrichment_source: str ("clearbit", "google_places", "internal")
        """
        # Check cache first
        cache_key = f"{business_name}_{website or ''}_{location or ''}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result["cached"] = True
            return cached_result
        
        enrichment_result = {
            "company_size": "unknown",
            "industry": "unknown",
            "description": "",
            "website": website or "",
            "social_media": {},
            "technology_stack": [],
            "founded_year": None,
            "revenue_range": "unknown",
            "employee_count": None,
            "enrichment_source": "internal",
            "cached": False,
            "enrichment_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Try Clearbit first (if API key available)
        if self.clearbit_api_key and website:
            try:
                clearbit_data = self._enrich_clearbit(website)
                if clearbit_data:
                    enrichment_result.update(clearbit_data)
                    enrichment_result["enrichment_source"] = "clearbit"
            except Exception as e:
                import logging
                logging.debug(f"Error enriching with Clearbit for {website}: {e}")
        
        # Try Google Places (if API key available and location provided)
        if self.google_places_api_key and (business_name or location):
            try:
                places_data = self._enrich_google_places(business_name, location)
                if places_data:
                    # Merge with existing data (don't overwrite Clearbit data)
                    for key, value in places_data.items():
                        if key not in enrichment_result or enrichment_result[key] in ("unknown", "", None):
                            enrichment_result[key] = value
                    if enrichment_result["enrichment_source"] == "internal":
                        enrichment_result["enrichment_source"] = "google_places"
            except Exception as e:
                import logging
                logging.debug(f"Error enriching with Google Places for {business_name}: {e}")
        
        # Fallback to internal classification
        if enrichment_result["enrichment_source"] == "internal":
            enrichment_result.update(self._internal_classification(business_name, website))
        
        # Cache the result
        self._save_to_cache(cache_key, enrichment_result)
        
        return enrichment_result
    
    @retry(attempts=2, delay=1, exceptions=(requests.RequestException,))
    def _enrich_clearbit(self, website: str) -> Optional[Dict[str, Any]]:
        """Enrich using Clearbit API."""
        if not self.clearbit_api_key:
            return None
        
        # Clean website URL
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"
        
        url = f"https://company.clearbit.com/v2/companies/find?domain={website.split('//')[1].split('/')[0]}"
        
        response = requests.get(
            url,
            auth=(self.clearbit_api_key, ""),
            timeout=5
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Map Clearbit data to our format
        employee_count = data.get("metrics", {}).get("employees", 0)
        company_size = self._estimate_company_size(employee_count)
        
        return {
            "company_size": company_size,
            "industry": data.get("category", {}).get("industry", "unknown"),
            "description": data.get("description", ""),
            "website": data.get("domain", website),
            "social_media": {
                "linkedin": data.get("linkedin", {}).get("handle", ""),
                "twitter": data.get("twitter", {}).get("handle", ""),
                "facebook": data.get("facebook", {}).get("handle", "")
            },
            "founded_year": data.get("foundedYear"),
            "employee_count": employee_count,
            "revenue_range": self._estimate_revenue_range(data.get("metrics", {}).get("annualRevenue", 0))
        }
    
    @retry(attempts=2, delay=1, exceptions=(requests.RequestException,))
    def _enrich_google_places(self, business_name: str, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Enrich using Google Places API."""
        if not self.google_places_api_key:
            return None
        
        # Search for place
        query = business_name
        if location:
            query = f"{business_name} {location}"
        
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": self.google_places_api_key
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not data.get("results"):
            return None
        
        place = data["results"][0]
        place_id = place.get("place_id")
        
        # Get place details
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,formatted_address,website,types,business_status",
            "key": self.google_places_api_key
        }
        
        details_response = requests.get(details_url, params=details_params, timeout=5)
        if details_response.status_code != 200:
            return None
        
        details_data = details_response.json().get("result", {})
        
        # Extract industry from types
        types = details_data.get("types", [])
        industry = "unknown"
        for t in types:
            if t not in ["establishment", "point_of_interest"]:
                industry = t.replace("_", " ").title()
                break
        
        return {
            "industry": industry,
            "website": details_data.get("website", ""),
            "description": f"{details_data.get('name', '')} - {details_data.get('formatted_address', '')}"
        }
    
    def _internal_classification(
        self,
        business_name: str,
        website: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal classification using heuristics."""
        # Simple keyword-based industry detection
        industry_keywords = {
            "technology": ["tech", "software", "it", "digital", "app", "web", "cloud"],
            "healthcare": ["health", "medical", "clinic", "hospital", "doctor", "dental"],
            "education": ["school", "university", "college", "education", "academy", "learning"],
            "retail": ["shop", "store", "retail", "market", "boutique"],
            "restaurant": ["restaurant", "cafe", "food", "dining", "bar", "bistro"],
            "real_estate": ["real estate", "property", "realtor", "housing", "estate"],
            "finance": ["bank", "financial", "finance", "investment", "accounting", "tax"],
            "legal": ["law", "legal", "attorney", "lawyer", "law firm"],
        }
        
        name_lower = business_name.lower()
        industry = "unknown"
        for ind, keywords in industry_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                industry = ind
                break
        
        # Detect technology stack from website (if available)
        technology_stack = []
        if website:
            try:
                tech_stack = self._detect_technology_stack(website)
                technology_stack = tech_stack
            except Exception as e:
                import logging
                logging.debug(f"Error detecting technology stack for {website}: {e}")
        
        return {
            "industry": industry,
            "technology_stack": technology_stack,
            "company_size": "unknown"  # Can't estimate without more data
        }
    
    def _detect_technology_stack(self, website: str) -> List[str]:
        """Detect technology stack from website (basic detection)."""
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"
        
        try:
            response = requests.get(website, timeout=5, allow_redirects=True)
            content = response.text.lower()
            
            technologies = []
            
            # Detect CMS
            if "wp-content" in content or "wordpress" in content:
                technologies.append("WordPress")
            if "drupal" in content:
                technologies.append("Drupal")
            if "joomla" in content:
                technologies.append("Joomla")
            
            # Detect frameworks
            if "react" in content or "reactjs" in content:
                technologies.append("React")
            if "angular" in content:
                technologies.append("Angular")
            if "vue" in content:
                technologies.append("Vue.js")
            
            # Detect e-commerce
            if "shopify" in content:
                technologies.append("Shopify")
            if "woocommerce" in content:
                technologies.append("WooCommerce")
            if "magento" in content:
                technologies.append("Magento")
            
            return technologies
        except Exception:
            return []
    
    def _estimate_company_size(self, employee_count: int) -> str:
        """Estimate company size category from employee count."""
        if employee_count == 0:
            return "unknown"
        elif employee_count <= 10:
            return "1-10"
        elif employee_count <= 50:
            return "11-50"
        elif employee_count <= 200:
            return "51-200"
        elif employee_count <= 500:
            return "201-500"
        elif employee_count <= 1000:
            return "501-1000"
        elif employee_count <= 5000:
            return "1001-5000"
        else:
            return "5001+"
    
    def _estimate_revenue_range(self, annual_revenue: float) -> str:
        """Estimate revenue range from annual revenue."""
        if annual_revenue == 0:
            return "unknown"
        elif annual_revenue < 1_000_000:
            return "< $1M"
        elif annual_revenue < 10_000_000:
            return "$1M - $10M"
        elif annual_revenue < 50_000_000:
            return "$10M - $50M"
        elif annual_revenue < 100_000_000:
            return "$50M - $100M"
        else:
            return "> $100M"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get enrichment result from cache."""
        import hashlib
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_hash}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = cached_data.get("enrichment_timestamp", 0)
            if isinstance(cache_time, str):
                cache_time = time.mktime(time.strptime(cache_time, "%Y-%m-%d %H:%M:%S"))
            
            if time.time() - cache_time > self.cache_ttl:
                cache_file.unlink()
                return None
            
            return cached_data
        except Exception:
            return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Save enrichment result to cache."""
        import hashlib
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_hash}.json"
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            import logging
            logging.debug(f"Error saving enrichment cache to {cache_file}: {e}")


# Global instance
_enrichment_service = None

def get_enrichment_service() -> BusinessEnrichmentService:
    """Get or create global enrichment service instance."""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = BusinessEnrichmentService()
    return _enrichment_service

