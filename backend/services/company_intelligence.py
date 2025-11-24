"""Company intelligence service for deep company insights."""
from typing import Dict, Any, Optional, List
import os
import requests


class CompanyIntelligenceService:
    """Service for gathering company intelligence data."""
    
    def __init__(self):
        """Initialize company intelligence service."""
        self.crunchbase_api_key = os.getenv("CRUNCHBASE_API_KEY")
        self.clearbit_api_key = os.getenv("CLEARBIT_API_KEY")
    
    def get_company_intelligence(
        self,
        company_name: str,
        website: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive company intelligence.
        
        Features:
        - Employee count estimation
        - Revenue estimates
        - Funding rounds (via Crunchbase)
        - Competitor identification
        - Tags (SaaS, Restaurant, IT training, etc.)
        
        Args:
            company_name: Company name
            website: Company website (optional)
            location: Company location (optional)
            
        Returns:
            Dict with company intelligence data
        """
        intelligence = {
            "employee_count": None,
            "revenue_estimate": None,
            "funding_rounds": [],
            "total_funding": None,
            "competitors": [],
            "tags": [],
            "founded_year": None,
            "headquarters": location,
        }
        
        # 1. Get employee count
        employee_count = self.estimate_employee_count(company_name, website, location)
        if employee_count:
            intelligence["employee_count"] = employee_count
        
        # 2. Estimate revenue
        revenue = self.estimate_revenue(company_name, website, location, employee_count)
        if revenue:
            intelligence["revenue_estimate"] = revenue
        
        # 3. Get funding data (Crunchbase)
        if self.crunchbase_api_key:
            funding_data = self.get_funding_data(company_name, website)
            if funding_data:
                intelligence["funding_rounds"] = funding_data.get("rounds", [])
                intelligence["total_funding"] = funding_data.get("total_funding")
                intelligence["founded_year"] = funding_data.get("founded_year")
        
        # 4. Identify competitors
        competitors = self.identify_competitors(company_name, location)
        if competitors:
            intelligence["competitors"] = competitors
        
        # 5. Generate tags
        tags = self.generate_tags(company_name, website, location)
        if tags:
            intelligence["tags"] = tags
        
        return intelligence
    
    def estimate_employee_count(
        self,
        company_name: str,
        website: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[int]:
        """
        Estimate employee count.
        
        Args:
            company_name: Company name
            website: Company website
            location: Company location
            
        Returns:
            Estimated employee count or None
        """
        # Try Clearbit API if available
        if self.clearbit_api_key and website:
            try:
                clearbit_data = self._get_clearbit_data(website)
                if clearbit_data and clearbit_data.get("metrics"):
                    employees = clearbit_data["metrics"].get("employees")
                    if employees:
                        return employees
            except Exception as e:
                import logging
                logging.debug(f"Error estimating employees for {company_name}: {e}")
        
        # Fallback: Estimate based on signals
        # This is a simplified estimation
        # In production, you'd use more sophisticated methods
        return None
    
    def estimate_revenue(
        self,
        company_name: str,
        website: Optional[str] = None,
        location: Optional[str] = None,
        employee_count: Optional[int] = None
    ) -> Optional[str]:
        """
        Estimate revenue range.
        
        Args:
            company_name: Company name
            website: Company website
            location: Company location
            employee_count: Estimated employee count
            
        Returns:
            Revenue estimate range (e.g., "$1M-$10M") or None
        """
        # Use employee count to estimate revenue
        if employee_count:
            # Rough estimate: $100K per employee for tech companies
            estimated_revenue = employee_count * 100000
            if estimated_revenue >= 1000000000:
                return "$1B+"
            elif estimated_revenue >= 100000000:
                return "$100M-$1B"
            elif estimated_revenue >= 10000000:
                return "$10M-$100M"
            elif estimated_revenue >= 1000000:
                return "$1M-$10M"
            elif estimated_revenue >= 100000:
                return "$100K-$1M"
            else:
                return "<$100K"
        
        return None
    
    def get_funding_data(
        self,
        company_name: str,
        website: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get funding data from Crunchbase.
        
        Args:
            company_name: Company name
            website: Company website
            
        Returns:
            Dict with funding data or None
        """
        if not self.crunchbase_api_key:
            return None
        
        try:
            # Crunchbase API call using Basic API v4
            # Note: Crunchbase Basic API requires POST for searches
            url = "https://api.crunchbase.com/v4/searches/organizations"
            headers = {
                "X-cb-user-key": self.crunchbase_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "field_ids": ["name", "funding_total", "founded_on"],
                "query": [
                    {
                        "type": "predicate",
                        "field_id": "name",
                        "operator_id": "contains",
                        "values": [company_name]
                    }
                ],
                "limit": 1
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Parse Crunchbase response
                entities = data.get("entities", [])
                if entities:
                    entity = entities[0]
                    properties = entity.get("properties", {})
                    
                    # Extract funding information
                    funding_total = properties.get("funding_total", {}).get("value")
                    founded_on = properties.get("founded_on", {}).get("value")
                    founded_year = None
                    if founded_on:
                        try:
                            founded_year = int(founded_on.split("-")[0])
                        except (ValueError, AttributeError):
                            pass
                    
                    return {
                        "rounds": [],  # Would need additional API call for detailed rounds
                        "total_funding": funding_total,
                        "founded_year": founded_year
                    }
                
                return {
                    "rounds": [],
                    "total_funding": None,
                    "founded_year": None
                }
        except Exception as e:
            import logging
            logging.debug(f"Error fetching Crunchbase funding data: {e}")
        
        return None
    
    def identify_competitors(
        self,
        company_name: str,
        location: Optional[str] = None
    ) -> List[str]:
        """
        Identify competitors using enhanced service.
        
        Args:
            company_name: Company name
            location: Company location
            
        Returns:
            List of competitor names
        """
        try:
            from backend.services.enhanced_competitor_service import enhanced_competitor_service
            
            # Get industry from company data if available
            industry = None  # Could be passed as parameter
            
            competitors_data = enhanced_competitor_service.identify_competitors(
                company_name=company_name,
                location=location,
                industry=industry,
                limit=10
            )
            
            # Return just names for backward compatibility
            return [c["name"] for c in competitors_data]
        except Exception as e:
            logging.info(f"[COMPANY_INTELLIGENCE] Error identifying competitors: {e}")
            return []
    
    def generate_tags(
        self,
        company_name: str,
        website: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[str]:
        """
        Generate tags for company.
        
        Args:
            company_name: Company name
            website: Company website
            location: Company location
            
        Returns:
            List of tags
        """
        tags = []
        
        # Analyze company name and website for tags
        name_lower = company_name.lower()
        website_lower = (website or "").lower()
        combined = f"{name_lower} {website_lower}"
        
        # Technology tags
        if any(term in combined for term in ["saas", "software", "tech", "it", "development"]):
            tags.append("SaaS")
            tags.append("Technology")
        
        # Business type tags
        if any(term in combined for term in ["restaurant", "cafe", "food", "dining"]):
            tags.append("Restaurant")
            tags.append("Food & Beverage")
        
        if any(term in combined for term in ["clinic", "medical", "health", "hospital"]):
            tags.append("Healthcare")
            tags.append("Medical")
        
        if any(term in combined for term in ["real estate", "property", "realty"]):
            tags.append("Real Estate")
        
        if any(term in combined for term in ["education", "school", "university", "training"]):
            tags.append("Education")
        
        # Size tags (if we have employee count)
        # These would be added based on employee_count if available
        
        return tags[:10]  # Limit to 10 tags
    
    def _get_clearbit_data(self, website: str) -> Optional[Dict[str, Any]]:
        """Get data from Clearbit API."""
        if not self.clearbit_api_key:
            return None
        
        try:
            # Clean website URL
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"
            
            url = f"https://company.clearbit.com/v2/companies/find?domain={website}"
            headers = {
                "Authorization": f"Bearer {self.clearbit_api_key}"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            import logging
            logging.debug(f"Error fetching Clearbit data for {website}: {e}")
        
        return None


# Global instance
company_intelligence_service = CompanyIntelligenceService()

