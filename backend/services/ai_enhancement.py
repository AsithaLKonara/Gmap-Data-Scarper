"""AI enhancement service for lead quality assessment and summarization."""
import os
from typing import Optional, Dict, Any, List
from backend.utils.retry import retry


class AIEnhancementService:
    """Enhances lead data with AI-generated summaries and quality assessments."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize AI enhancement service.
        
        Args:
            openai_api_key: OpenAI API key (or from env OPENAI_API_KEY)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.api_enabled = bool(self.openai_api_key)
    
    def generate_business_description(
        self,
        business_name: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        website: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a business description using AI.
        
        Args:
            business_name: Name of the business
            industry: Industry category
            location: Business location
            website: Business website
            additional_info: Additional business information
        
        Returns:
            Generated business description
        """
        if not self.api_enabled:
            # Fallback to template-based description
            return self._generate_fallback_description(
                business_name, industry, location, website
            )
        
        try:
            return self._generate_openai_description(
                business_name, industry, location, website, additional_info
            )
        except Exception:
            return self._generate_fallback_description(
                business_name, industry, location, website
            )
    
    @retry(attempts=2, delay=1)
    def _generate_openai_description(
        self,
        business_name: str,
        industry: Optional[str],
        location: Optional[str],
        website: Optional[str],
        additional_info: Optional[Dict[str, Any]]
    ) -> str:
        """Generate description using OpenAI API."""
        try:
            # Try new OpenAI client library first
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                prompt_parts = [f"Business: {business_name}"]
                if industry:
                    prompt_parts.append(f"Industry: {industry}")
                if location:
                    prompt_parts.append(f"Location: {location}")
                if website:
                    prompt_parts.append(f"Website: {website}")
                if additional_info:
                    for key, value in additional_info.items():
                        if value:
                            prompt_parts.append(f"{key}: {value}")
                
                prompt = "\n".join(prompt_parts) + "\n\nGenerate a brief professional business description (2-3 sentences):"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a business analyst. Generate concise, professional business descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
            except ImportError:
                # Fallback to old OpenAI library
                import openai
                openai.api_key = self.openai_api_key
                
                prompt_parts = [f"Business: {business_name}"]
                if industry:
                    prompt_parts.append(f"Industry: {industry}")
                if location:
                    prompt_parts.append(f"Location: {location}")
                if website:
                    prompt_parts.append(f"Website: {website}")
                if additional_info:
                    for key, value in additional_info.items():
                        if value:
                            prompt_parts.append(f"{key}: {value}")
                
                prompt = "\n".join(prompt_parts) + "\n\nGenerate a brief professional business description (2-3 sentences):"
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a business analyst. Generate concise, professional business descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
        except ImportError:
            # OpenAI library not installed
            return self._generate_fallback_description(business_name, industry, location, website)
        except Exception:
            return self._generate_fallback_description(business_name, industry, location, website)
    
    def _generate_fallback_description(
        self,
        business_name: str,
        industry: Optional[str],
        location: Optional[str],
        website: Optional[str]
    ) -> str:
        """Generate fallback description without AI."""
        parts = [business_name]
        if industry and industry != "unknown":
            parts.append(f"operating in the {industry} industry")
        if location:
            parts.append(f"located in {location}")
        if website:
            parts.append(f"with website {website}")
        
        return f"{', '.join(parts)}."
    
    def assess_lead_quality(
        self,
        business_name: str,
        phone_number: Optional[str] = None,
        website: Optional[str] = None,
        enrichment_data: Optional[Dict[str, Any]] = None,
        phone_verification: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess lead quality and generate a quality score.
        
        Args:
            business_name: Name of the business
            phone_number: Phone number (optional)
            website: Website URL (optional)
            enrichment_data: Business enrichment data (optional)
            phone_verification: Phone verification data (optional)
        
        Returns:
            Dict with quality assessment:
            - quality_score: int (0-100)
            - quality_tier: str ("high", "medium", "low")
            - strengths: List[str]
            - weaknesses: List[str]
            - recommendations: List[str]
        """
        score = 0
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Business name (required)
        if business_name and len(business_name.strip()) > 0:
            score += 10
            strengths.append("Business name provided")
        else:
            weaknesses.append("Missing business name")
            recommendations.append("Ensure business name is captured")
        
        # Phone number
        if phone_number:
            score += 20
            strengths.append("Phone number available")
            
            # Phone verification
            if phone_verification:
                if phone_verification.get("is_valid"):
                    score += 15
                    strengths.append("Phone number verified")
                    line_type = phone_verification.get("line_type", "")
                    if line_type == "mobile":
                        score += 5
                        strengths.append("Mobile number (higher engagement)")
                    elif line_type == "landline":
                        score += 3
                        strengths.append("Landline number")
                else:
                    score -= 10
                    weaknesses.append("Phone number invalid")
                    recommendations.append("Verify phone number accuracy")
        else:
            weaknesses.append("No phone number")
            recommendations.append("Try to extract phone number from website or social media")
        
        # Website
        if website:
            score += 15
            strengths.append("Website available")
            
            # Website validation
            if website.startswith(("http://", "https://")):
                score += 5
            else:
                recommendations.append("Validate website URL format")
        else:
            weaknesses.append("No website")
            recommendations.append("Search for business website")
        
        # Enrichment data
        if enrichment_data:
            score += 10
            strengths.append("Business data enriched")
            
            # Company size
            company_size = enrichment_data.get("company_size", "unknown")
            if company_size != "unknown":
                score += 5
                strengths.append(f"Company size identified: {company_size}")
            
            # Industry
            industry = enrichment_data.get("industry", "unknown")
            if industry != "unknown":
                score += 5
                strengths.append(f"Industry identified: {industry}")
            
            # Technology stack
            tech_stack = enrichment_data.get("technology_stack", [])
            if tech_stack:
                score += 5
                strengths.append(f"Technology stack identified: {', '.join(tech_stack[:3])}")
        
        # Determine quality tier
        if score >= 80:
            quality_tier = "high"
        elif score >= 50:
            quality_tier = "medium"
        else:
            quality_tier = "low"
        
        return {
            "quality_score": min(100, max(0, score)),
            "quality_tier": quality_tier,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }
    
    def extract_key_insights(
        self,
        business_name: str,
        enrichment_data: Optional[Dict[str, Any]] = None,
        phone_verification: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Extract key insights from lead data.
        
        Args:
            business_name: Name of the business
            enrichment_data: Business enrichment data (optional)
            phone_verification: Phone verification data (optional)
        
        Returns:
            List of key insights
        """
        insights = []
        
        if enrichment_data:
            company_size = enrichment_data.get("company_size", "unknown")
            if company_size != "unknown":
                insights.append(f"Company size: {company_size} employees")
            
            industry = enrichment_data.get("industry", "unknown")
            if industry != "unknown":
                insights.append(f"Industry: {industry}")
            
            employee_count = enrichment_data.get("employee_count")
            if employee_count:
                insights.append(f"Employee count: {employee_count}")
            
            revenue_range = enrichment_data.get("revenue_range", "unknown")
            if revenue_range != "unknown":
                insights.append(f"Revenue range: {revenue_range}")
        
        if phone_verification:
            carrier = phone_verification.get("carrier", "unknown")
            if carrier != "unknown":
                insights.append(f"Phone carrier: {carrier}")
            
            line_type = phone_verification.get("line_type", "unknown")
            if line_type != "unknown":
                insights.append(f"Line type: {line_type}")
        
        return insights


# Global instance
_ai_enhancement_service = None

def get_ai_enhancement_service() -> AIEnhancementService:
    """Get or create global AI enhancement service instance."""
    global _ai_enhancement_service
    if _ai_enhancement_service is None:
        _ai_enhancement_service = AIEnhancementService()
    return _ai_enhancement_service

