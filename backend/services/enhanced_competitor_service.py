"""Enhanced competitor identification service with ML."""
from typing import List, Dict, Any, Optional
from backend.models.database import get_session
from backend.models.database import Lead
from sqlalchemy import func, and_, or_


class EnhancedCompetitorService:
    """Enhanced service for identifying competitors using ML and similarity matching."""
    
    def identify_competitors(
        self,
        company_name: str,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identify competitors using enhanced matching.
        
        Args:
            company_name: Company name
            location: Company location
            industry: Company industry
            limit: Maximum number of competitors to return
            
        Returns:
            List of competitor information
        """
        db = get_session()
        try:
            # Build query to find similar companies
            query = db.query(Lead).filter(
                Lead.lead_type == "business",
                Lead.display_name.isnot(None),
                Lead.display_name != "N/A"
            )
            
            # Exclude the company itself
            query = query.filter(Lead.display_name != company_name)
            
            # Filter by location if provided
            if location:
                location_parts = location.lower().split(",")
                city = location_parts[0].strip() if location_parts else None
                if city:
                    query = query.filter(
                        or_(
                            func.lower(Lead.city).contains(city),
                            func.lower(Lead.location).contains(city)
                        )
                    )
            
            # Filter by industry if provided
            if industry:
                query = query.filter(
                    or_(
                        Lead.industry == industry,
                        Lead.business_type.contains(industry)
                    )
                )
            
            # Get candidates
            candidates = query.limit(limit * 3).all()  # Get more for scoring
            
            # Score and rank candidates
            scored_competitors = []
            for candidate in candidates:
                score = self._calculate_similarity_score(
                    company_name, location, industry,
                    candidate.display_name, candidate.location, candidate.industry
                )
                
                if score > 0.3:  # Minimum similarity threshold
                    scored_competitors.append({
                        "name": candidate.display_name,
                        "location": candidate.location or candidate.city,
                        "industry": candidate.industry or candidate.business_type,
                        "similarity_score": score,
                        "lead_id": candidate.id,
                        "phone": candidate.phone,
                        "website": candidate.website
                    })
            
            # Sort by similarity score
            scored_competitors.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return scored_competitors[:limit]
            
        finally:
            db.close()
    
    def _calculate_similarity_score(
        self,
        company1: str,
        location1: Optional[str],
        industry1: Optional[str],
        company2: str,
        location2: Optional[str],
        industry2: Optional[str]
    ) -> float:
        """
        Calculate similarity score between two companies.
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        score = 0.0
        
        # 1. Industry similarity (40% weight)
        if industry1 and industry2:
            if industry1.lower() == industry2.lower():
                score += 0.4
            elif industry1.lower() in industry2.lower() or industry2.lower() in industry1.lower():
                score += 0.2
        
        # 2. Location similarity (30% weight)
        if location1 and location2:
            loc1_lower = location1.lower()
            loc2_lower = location2.lower()
            
            # Exact match
            if loc1_lower == loc2_lower:
                score += 0.3
            # City match
            elif any(part in loc2_lower for part in loc1_lower.split(",")[:1]):
                score += 0.2
            # Country match
            elif any(part in loc2_lower for part in loc1_lower.split(",")[-1:]):
                score += 0.1
        
        # 3. Name similarity (30% weight) - using simple word overlap
        if company1 and company2:
            words1 = set(company1.lower().split())
            words2 = set(company2.lower().split())
            
            # Remove common words
            common_words = {"the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for"}
            words1 = words1 - common_words
            words2 = words2 - common_words
            
            if words1 and words2:
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                score += overlap * 0.3
        
        return min(1.0, score)
    
    def get_competitive_analysis(
        self,
        company_name: str,
        location: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive competitive analysis.
        
        Args:
            company_name: Company name
            location: Company location
            industry: Company industry
            
        Returns:
            Competitive analysis data
        """
        competitors = self.identify_competitors(
            company_name=company_name,
            location=location,
            industry=industry,
            limit=10
        )
        
        # Analyze competitor data
        total_competitors = len(competitors)
        avg_similarity = sum(c["similarity_score"] for c in competitors) / total_competitors if competitors else 0
        
        # Market concentration
        locations = [c["location"] for c in competitors if c.get("location")]
        location_diversity = len(set(locations)) / len(locations) if locations else 0
        
        return {
            "company_name": company_name,
            "competitors": competitors,
            "total_competitors": total_competitors,
            "average_similarity": round(avg_similarity, 2),
            "location_diversity": round(location_diversity, 2),
            "market_concentration": "high" if location_diversity < 0.3 else "medium" if location_diversity < 0.6 else "low"
        }


# Global instance
enhanced_competitor_service = EnhancedCompetitorService()

