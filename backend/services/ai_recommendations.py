"""AI-powered lead recommendation service."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import os


class AIRecommendationService:
    """Service for AI-powered lead recommendations."""
    
    def __init__(self):
        """Initialize recommendation service."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_ai = bool(self.openai_api_key)
    
    def recommend_leads(
        self,
        user_id: str,
        criteria: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend leads based on user criteria and history.
        
        Args:
            user_id: User ID
            criteria: Recommendation criteria (business_type, location, etc.)
            limit: Number of recommendations
            
        Returns:
            List of recommended leads
        """
        from backend.models.database import get_session
        from backend.models.database import Lead, Task
        
        db = get_session()
        try:
            # Get user's historical leads
            user_tasks = db.query(Task.task_id).filter(Task.user_id == user_id).all()
            task_ids = [t[0] for t in user_tasks] if user_tasks else []
            
            # Build query based on criteria
            query = db.query(Lead)
            
            if task_ids:
                query = query.filter(Lead.task_id.in_(task_ids))
            
            # Apply filters
            if criteria.get("business_type"):
                query = query.filter(Lead.business_type == criteria["business_type"])
            
            if criteria.get("location"):
                query = query.filter(Lead.location.contains(criteria["location"]))
            
            if criteria.get("min_score"):
                query = query.filter(Lead.lead_score >= criteria["min_score"])
            
            # Order by score and recency
            leads = query.order_by(
                Lead.lead_score.desc(),
                Lead.extracted_at.desc()
            ).limit(limit).all()
            
            # Convert to dicts
            recommendations = []
            for lead in leads:
                lead_dict = {
                    "lead_id": lead.id,
                    "display_name": lead.display_name,
                    "phone": lead.phone,
                    "email": lead.email,
                    "location": lead.location,
                    "business_type": lead.business_type,
                    "lead_score": lead.lead_score,
                    "lead_score_category": lead.lead_score_category,
                    "reason": self._generate_recommendation_reason(lead, criteria)
                }
                recommendations.append(lead_dict)
            
            return recommendations
        finally:
            db.close()
    
    def _generate_recommendation_reason(
        self,
        lead: Any,
        criteria: Dict[str, Any]
    ) -> str:
        """Generate reason for recommendation."""
        reasons = []
        
        if lead.lead_score and lead.lead_score >= 80:
            reasons.append("High lead score")
        
        if lead.phone and lead.phone != "N/A":
            reasons.append("Phone available")
        
        if criteria.get("business_type") and lead.business_type == criteria["business_type"]:
            reasons.append("Matches business type")
        
        if criteria.get("location") and criteria["location"].lower() in (lead.location or "").lower():
            reasons.append("Matches location")
        
        return ", ".join(reasons) if reasons else "Based on your search history"
    
    def auto_qualify_lead(
        self,
        lead_data: Dict[str, Any],
        qualification_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Automatically qualify a lead based on rules.
        
        Args:
            lead_data: Lead data dictionary
            qualification_rules: Custom qualification rules
            
        Returns:
            Qualification result
        """
        score = 0
        criteria_met = []
        
        # Default qualification criteria
        rules = qualification_rules or {
            "min_score": 70,
            "require_phone": True,
            "require_email": False,
            "min_followers": 0
        }
        
        # Check lead score
        lead_score = lead_data.get("lead_score", 0)
        if lead_score >= rules.get("min_score", 70):
            score += 40
            criteria_met.append("Meets minimum score")
        
        # Check phone
        has_phone = lead_data.get("phone") and lead_data.get("phone") != "N/A"
        if rules.get("require_phone", True):
            if has_phone:
                score += 30
                criteria_met.append("Has phone number")
            else:
                score -= 20
        else:
            if has_phone:
                score += 10
        
        # Check email
        has_email = lead_data.get("email") and lead_data.get("email") != "N/A"
        if rules.get("require_email", False):
            if has_email:
                score += 20
                criteria_met.append("Has email")
            else:
                score -= 10
        
        # Check followers (if available)
        followers = lead_data.get("followers", "0")
        try:
            follower_count = self._parse_follower_count(str(followers))
            min_followers = rules.get("min_followers", 0)
            if follower_count >= min_followers:
                score += 10
                criteria_met.append("Meets follower threshold")
        except:
            pass
        
        # Determine qualification
        qualified = score >= 50
        
        return {
            "qualified": qualified,
            "qualification_score": score,
            "criteria_met": criteria_met,
            "recommendation": "Contact immediately" if qualified else "Review manually"
        }
    
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


# Global instance
ai_recommendation_service = AIRecommendationService()

