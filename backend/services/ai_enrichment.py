"""Enhanced AI enrichment service with keyword extraction and industry detection."""
from typing import Dict, Any, List, Optional
import re
import os


class AIEnrichmentService:
    """Service for enriching leads with AI-powered features."""
    
    def __init__(self):
        """Initialize AI enrichment service."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_ai = bool(self.openai_api_key)
    
    def enrich_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a lead with AI-powered features.
        
        Features:
        - Keyword extraction (tech stack, degree, services)
        - Industry detection
        - Category extraction
        - Revenue/price range estimation
        - Email extraction
        - Location coordinates conversion
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Enriched lead data
        """
        enriched = lead_data.copy()
        
        # 1. Extract keywords
        keywords = self.extract_keywords(lead_data)
        enriched["keywords"] = keywords
        
        # 2. Detect industry
        industry = self.detect_industry(lead_data)
        if industry and not enriched.get("industry"):
            enriched["industry"] = industry
        
        # 3. Extract categories
        categories = self.extract_categories(lead_data)
        if categories:
            enriched["categories"] = categories
        
        # 4. Estimate revenue
        revenue_estimate = self.estimate_revenue(lead_data)
        if revenue_estimate:
            enriched["estimated_revenue"] = revenue_estimate
        
        # 5. Extract email from website (if available)
        if not enriched.get("email") and enriched.get("website"):
            email = self.extract_email_from_website(enriched["website"])
            if email:
                enriched["email"] = email
        
        # 6. Convert location to coordinates
        if enriched.get("location"):
            coords = self.location_to_coordinates(enriched["location"])
            if coords:
                enriched["coordinates"] = coords
        
        return enriched
    
    def extract_keywords(self, lead_data: Dict[str, Any]) -> List[str]:
        """
        Extract keywords from lead data.
        
        Keywords include:
        - Tech stack (if mentioned)
        - Degree/education terms
        - Services offered
        - Skills
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            List of extracted keywords
        """
        keywords = []
        
        # Combine text fields
        text_fields = [
            lead_data.get("display_name", ""),
            lead_data.get("bio_about", ""),
            lead_data.get("website", ""),
            lead_data.get("job_title", ""),
            lead_data.get("field_of_study", ""),
        ]
        combined_text = " ".join([str(f) for f in text_fields if f]).lower()
        
        # Tech stack keywords
        tech_keywords = [
            "python", "javascript", "java", "react", "node", "vue", "angular",
            "aws", "azure", "gcp", "docker", "kubernetes", "mongodb", "postgresql",
            "shopify", "wordpress", "woocommerce", "magento"
        ]
        for tech in tech_keywords:
            if tech in combined_text:
                keywords.append(tech)
        
        # Education keywords
        education_keywords = [
            "bachelor", "master", "phd", "doctorate", "degree", "diploma",
            "university", "college", "undergraduate", "postgraduate"
        ]
        for edu in education_keywords:
            if edu in combined_text:
                keywords.append(edu)
        
        # Service keywords
        service_keywords = [
            "consulting", "development", "design", "marketing", "sales",
            "support", "training", "coaching", "therapy", "treatment"
        ]
        for service in service_keywords:
            if service in combined_text:
                keywords.append(service)
        
        # Use AI for advanced extraction if available
        if self.use_ai and len(keywords) < 5:
            ai_keywords = self._extract_keywords_ai(combined_text)
            keywords.extend(ai_keywords)
        
        return list(set(keywords))[:20]  # Limit to 20 unique keywords
    
    def _extract_keywords_ai(self, text: str) -> List[str]:
        """Extract keywords using AI."""
        if not self.use_ai or len(text) < 10:
            return []
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract 5-10 key terms/keywords from the text. Return as comma-separated list."},
                    {"role": "user", "content": f"Text: {text[:500]}\n\nExtract keywords:"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            keywords_str = response.choices[0].message.content.strip()
            keywords = [k.strip() for k in keywords_str.split(",")]
            return keywords[:10]
        except:
            return []
    
    def detect_industry(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect industry from lead data.
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Detected industry or None
        """
        # Check existing industry field
        if lead_data.get("industry"):
            return lead_data["industry"]
        
        # Check business type
        business_type = lead_data.get("business_type", "").lower()
        industry_map = {
            "restaurant": "Food & Beverage",
            "cafe": "Food & Beverage",
            "clinic": "Healthcare",
            "medical": "Healthcare",
            "software": "Technology",
            "saas": "Technology",
            "tech": "Technology",
            "real_estate": "Real Estate",
            "property": "Real Estate",
            "education": "Education",
            "school": "Education",
            "university": "Education",
        }
        
        for key, industry in industry_map.items():
            if key in business_type:
                return industry
        
        # Use AI if available
        if self.use_ai:
            return self._detect_industry_ai(lead_data)
        
        return None
    
    def _detect_industry_ai(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """Detect industry using AI."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            text = f"{lead_data.get('display_name', '')} {lead_data.get('bio_about', '')}"
            if not text.strip():
                return None
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Identify the industry. Respond with just the industry name."},
                    {"role": "user", "content": f"Business: {text[:300]}\n\nIndustry:"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except:
            return None
    
    def extract_categories(self, lead_data: Dict[str, Any]) -> List[str]:
        """Extract categories from lead data."""
        categories = []
        
        if lead_data.get("business_type"):
            categories.append(lead_data["business_type"])
        
        if lead_data.get("industry"):
            categories.append(lead_data["industry"])
        
        # Extract from bio
        bio = (lead_data.get("bio_about") or "").lower()
        category_keywords = {
            "restaurant": ["restaurant", "cafe", "dining", "food"],
            "retail": ["shop", "store", "retail", "boutique"],
            "service": ["service", "consulting", "professional"],
            "tech": ["software", "tech", "it", "development"],
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in bio for kw in keywords):
                if category not in categories:
                    categories.append(category)
        
        return categories[:5]  # Limit to 5 categories
    
    def estimate_revenue(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """
        Estimate revenue based on business signals.
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Revenue estimate range or None
        """
        # Simple estimation based on signals
        followers = lead_data.get("followers")
        website = lead_data.get("website")
        
        # If has website and good follower count, likely established business
        if website and website != "N/A":
            try:
                followers_count = self._parse_follower_count(str(followers)) if followers else 0
                if followers_count > 10000:
                    return "$1M+"
                elif followers_count > 1000:
                    return "$100K-$1M"
                elif followers_count > 100:
                    return "$10K-$100K"
            except Exception as e:
                import logging
                logging.debug(f"Error parsing followers count for revenue estimate: {e}")
        
        # Default estimate for businesses with website
        if website and website != "N/A":
            return "$10K-$100K"
        
        return None
    
    def _parse_follower_count(self, followers_str: str) -> int:
        """Parse follower count string to integer."""
        import re
        
        clean = re.sub(r'[,\s]', '', followers_str.lower())
        
        if 'k' in clean:
            num = float(re.sub(r'[^0-9.]', '', clean))
            return int(num * 1000)
        elif 'm' in clean:
            num = float(re.sub(r'[^0-9.]', '', clean))
            return int(num * 1000000)
        else:
            num = re.sub(r'[^0-9]', '', clean)
            return int(num) if num else 0
    
    def extract_email_from_website(self, website: str) -> Optional[str]:
        """
        Attempt to extract email from website.
        
        Args:
            website: Website URL
            
        Returns:
            Email address or None
        """
        try:
            from backend.services.email_extractor import email_extractor
            emails = email_extractor.extract_from_website(website, max_emails=1)
            return emails[0] if emails else None
        except Exception as e:
            logging.info(f"[ENRICHMENT] Error extracting email from website: {e}")
            return None
    
    def location_to_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """
        Convert location string to coordinates.
        
        Args:
            location: Location string (e.g., "Toronto, ON, Canada")
            
        Returns:
            Dict with lat/lng or None
        """
        # This would typically use a geocoding API (Google Maps, OpenStreetMap)
        # For now, return None - coordinates can be added later via geocoding service
        return None


# Global instance
ai_enrichment_service = AIEnrichmentService()

