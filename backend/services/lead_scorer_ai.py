"""AI-powered lead scoring system."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class AILeadScorer:
    """Service for scoring leads based on multiple factors."""
    
    def __init__(self):
        """Initialize lead scorer."""
        pass
    
    def calculate_score(self, lead_data: Dict[str, Any], query: str) -> int:
        """
        Calculate lead score (0-100) based on multiple factors.
        
        Scoring factors:
        - Relevance to query (30 points)
        - Freshness/recent activity (20 points)
        - Contact info availability (20 points)
        - Social presence strength (15 points)
        - Business category match (15 points)
        
        Args:
            lead_data: Lead data dictionary
            query: Original search query
            
        Returns:
            Score from 0-100
        """
        score = 0
        
        # 1. Relevance to query (30 points)
        relevance_score = self._calculate_relevance(lead_data, query)
        score += relevance_score
        
        # 2. Freshness/recent activity (20 points)
        freshness_score = self._calculate_freshness(lead_data)
        score += freshness_score
        
        # 3. Contact info availability (20 points)
        contact_score = self._calculate_contact_availability(lead_data)
        score += contact_score
        
        # 4. Social presence strength (15 points)
        social_score = self._calculate_social_presence(lead_data)
        score += social_score
        
        # 5. Business category match (15 points)
        category_score = self._calculate_category_match(lead_data, query)
        score += category_score
        
        return min(100, max(0, score))
    
    def _calculate_relevance(self, lead_data: Dict[str, Any], query: str) -> int:
        """Calculate relevance score (0-30)."""
        score = 0
        query_lower = query.lower()
        
        # Check if query terms appear in lead data
        display_name = (lead_data.get("display_name") or "").lower()
        bio = (lead_data.get("bio_about") or "").lower()
        location = (lead_data.get("location") or "").lower()
        
        query_terms = query_lower.split()
        matches = 0
        
        for term in query_terms:
            if len(term) < 3:  # Skip short words
                continue
            if term in display_name or term in bio or term in location:
                matches += 1
        
        # Score based on match percentage
        if len(query_terms) > 0:
            match_ratio = matches / len(query_terms)
            score = int(30 * match_ratio)
        
        return score
    
    def _calculate_freshness(self, lead_data: Dict[str, Any]) -> int:
        """Calculate freshness score (0-20)."""
        score = 0
        
        # Check extracted_at timestamp
        extracted_at = lead_data.get("extracted_at")
        if extracted_at:
            if isinstance(extracted_at, str):
                try:
                    extracted_at = datetime.fromisoformat(extracted_at.replace('Z', '+00:00'))
                except Exception as e:
                    import logging
                    logging.debug(f"Error parsing extracted_at timestamp: {e}")
                    return 10  # Default score if parsing fails
            elif isinstance(extracted_at, datetime):
                pass
            else:
                return 10
            
            # Score based on how recent
            now = datetime.utcnow()
            if isinstance(extracted_at, datetime):
                age_days = (now - extracted_at.replace(tzinfo=None)).days
                
                if age_days <= 1:
                    score = 20
                elif age_days <= 7:
                    score = 15
                elif age_days <= 30:
                    score = 10
                else:
                    score = 5
        else:
            # No timestamp, give default score
            score = 10
        
        return score
    
    def _calculate_contact_availability(self, lead_data: Dict[str, Any]) -> int:
        """Calculate contact info availability score (0-20)."""
        score = 0
        
        # Phone number (10 points)
        phone = lead_data.get("phone") or lead_data.get("phone_normalized")
        if phone and phone != "N/A":
            score += 10
        
        # Email (5 points)
        email = lead_data.get("email")
        if email and email != "N/A":
            score += 5
        
        # Website (5 points)
        website = lead_data.get("website")
        if website and website != "N/A":
            score += 5
        
        return score
    
    def _calculate_social_presence(self, lead_data: Dict[str, Any]) -> int:
        """Calculate social presence strength (0-15)."""
        score = 0
        
        # Followers count
        followers_str = lead_data.get("followers")
        if followers_str and followers_str != "N/A":
            try:
                # Parse follower count
                followers = self._parse_follower_count(followers_str)
                if followers >= 10000:
                    score += 15
                elif followers >= 1000:
                    score += 10
                elif followers >= 100:
                    score += 5
            except:
                pass
        
        # Multiple platforms presence
        platform = lead_data.get("platform", "")
        # If we have data from multiple sources, that's a good sign
        # This is a simplified check
        if platform:
            score += 2
        
        return min(15, score)
    
    def _calculate_category_match(self, lead_data: Dict[str, Any], query: str) -> int:
        """Calculate business category match score (0-15)."""
        score = 0
        query_lower = query.lower()
        
        business_type = (lead_data.get("business_type") or "").lower()
        industry = (lead_data.get("industry") or "").lower()
        category = (lead_data.get("Category") or "").lower()
        
        # Check if query contains business-related terms
        business_terms = ["restaurant", "cafe", "shop", "store", "company", "business", "clinic", "salon"]
        query_has_business_term = any(term in query_lower for term in business_terms)
        
        if query_has_business_term:
            # If lead has business type, that's a match
            if business_type and business_type != "n/a":
                score += 10
            if industry and industry != "n/a":
                score += 5
        
        return min(15, score)
    
    def _parse_follower_count(self, followers_str: str) -> int:
        """Parse follower count string to integer."""
        import re
        
        # Remove commas and spaces
        clean = re.sub(r'[,\s]', '', followers_str.lower())
        
        # Handle K, M suffixes
        if 'k' in clean:
            num = float(re.sub(r'[^0-9.]', '', clean))
            return int(num * 1000)
        elif 'm' in clean:
            num = float(re.sub(r'[^0-9.]', '', clean))
            return int(num * 1000000)
        else:
            # Just numbers
            num = re.sub(r'[^0-9]', '', clean)
            return int(num) if num else 0
    
    def get_score_category(self, score: int) -> str:
        """
        Get score category label.
        
        Args:
            score: Lead score (0-100)
            
        Returns:
            Category: "hot", "warm", or "low"
        """
        if score >= 80:
            return "hot"
        elif score >= 50:
            return "warm"
        else:
            return "low"
    
    def get_score_emoji(self, score: int) -> str:
        """Get emoji for score category."""
        category = self.get_score_category(score)
        emoji_map = {
            "hot": "🔥",
            "warm": "🟡",
            "low": "⚪"
        }
        return emoji_map.get(category, "⚪")


# Global instance
ai_lead_scorer = AILeadScorer()

