"""Predictive analytics service for lead conversion and churn prediction."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.models.database import get_session
from backend.models.database import Lead, Task
from sqlalchemy import func, and_


class PredictiveAnalyticsService:
    """Service for predictive analytics and forecasting."""
    
    def predict_lead_conversion(
        self,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict likelihood of lead conversion.
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Dict with conversion probability and factors
        """
        score = 0.0
        factors = []
        
        # Factor 1: Lead score (0-40 points)
        lead_score = lead_data.get("lead_score", 0)
        if lead_score >= 80:
            score += 40
            factors.append({"factor": "High lead score", "impact": "high"})
        elif lead_score >= 70:
            score += 30
            factors.append({"factor": "Good lead score", "impact": "medium"})
        elif lead_score >= 50:
            score += 20
            factors.append({"factor": "Average lead score", "impact": "low"})
        else:
            factors.append({"factor": "Low lead score", "impact": "negative"})
        
        # Factor 2: Contact info availability (0-30 points)
        has_phone = lead_data.get("phone") and lead_data.get("phone") != "N/A"
        has_email = lead_data.get("email") and lead_data.get("email") != "N/A"
        
        if has_phone and has_email:
            score += 30
            factors.append({"factor": "Both phone and email available", "impact": "high"})
        elif has_phone:
            score += 20
            factors.append({"factor": "Phone available", "impact": "medium"})
        elif has_email:
            score += 15
            factors.append({"factor": "Email available", "impact": "medium"})
        else:
            factors.append({"factor": "No contact info", "impact": "negative"})
        
        # Factor 3: Business type match (0-20 points)
        business_type = lead_data.get("business_type", "").lower()
        high_value_types = ["restaurant", "retail", "service", "tech", "saas"]
        if any(bt in business_type for bt in high_value_types):
            score += 20
            factors.append({"factor": "High-value business type", "impact": "high"})
        
        # Factor 4: Location (0-10 points)
        location = lead_data.get("location", "").lower()
        major_markets = ["toronto", "new york", "london", "san francisco", "los angeles"]
        if any(market in location for market in major_markets):
            score += 10
            factors.append({"factor": "Major market location", "impact": "medium"})
        
        # Normalize to 0-100%
        conversion_probability = min(100, max(0, score))
        
        # Determine category
        if conversion_probability >= 70:
            category = "high"
        elif conversion_probability >= 40:
            category = "medium"
        else:
            category = "low"
        
        return {
            "conversion_probability": round(conversion_probability, 2),
            "category": category,
            "factors": factors,
            "recommendation": self._get_conversion_recommendation(conversion_probability)
        }
    
    def _get_conversion_recommendation(self, probability: float) -> str:
        """Get recommendation based on conversion probability."""
        if probability >= 70:
            return "High priority - Contact immediately"
        elif probability >= 40:
            return "Medium priority - Follow up within 24 hours"
        else:
            return "Low priority - Add to nurture sequence"
    
    def predict_churn(
        self,
        user_id: str,
        days_lookback: int = 30
    ) -> Dict[str, Any]:
        """
        Predict user churn risk.
        
        Args:
            user_id: User ID
            days_lookback: Days to analyze
            
        Returns:
            Dict with churn probability and risk factors
        """
        db = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)
            
            # Get user activity
            recent_tasks = db.query(func.count(Task.id)).filter(
                Task.user_id == user_id,
                Task.started_at >= cutoff_date
            ).scalar() or 0
            
            recent_leads = db.query(func.count(Lead.id)).join(
                Task, Lead.task_id == Task.task_id
            ).filter(
                Task.user_id == user_id,
                Lead.extracted_at >= cutoff_date
            ).scalar() or 0
            
            # Calculate churn risk
            risk_score = 0.0
            factors = []
            
            # Factor 1: Recent activity (0-40 points)
            if recent_tasks == 0:
                risk_score += 40
                factors.append({"factor": "No recent tasks", "impact": "high"})
            elif recent_tasks < 3:
                risk_score += 20
                factors.append({"factor": "Low task activity", "impact": "medium"})
            else:
                factors.append({"factor": "Active user", "impact": "positive"})
            
            # Factor 2: Lead generation (0-30 points)
            if recent_leads == 0:
                risk_score += 30
                factors.append({"factor": "No leads generated", "impact": "high"})
            elif recent_leads < 50:
                risk_score += 15
                factors.append({"factor": "Low lead generation", "impact": "medium"})
            else:
                factors.append({"factor": "Good lead generation", "impact": "positive"})
            
            # Factor 3: Time since last activity (0-30 points)
            last_task = db.query(Task.started_at).filter(
                Task.user_id == user_id
            ).order_by(Task.started_at.desc()).first()
            
            if last_task:
                days_since_activity = (datetime.utcnow() - last_task[0]).days
                if days_since_activity > 30:
                    risk_score += 30
                    factors.append({"factor": f"No activity for {days_since_activity} days", "impact": "high"})
                elif days_since_activity > 14:
                    risk_score += 15
                    factors.append({"factor": f"Low activity for {days_since_activity} days", "impact": "medium"})
            
            # Normalize to 0-100%
            churn_probability = min(100, max(0, risk_score))
            
            # Determine risk level
            if churn_probability >= 60:
                risk_level = "high"
            elif churn_probability >= 30:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "churn_probability": round(churn_probability, 2),
                "risk_level": risk_level,
                "factors": factors,
                "recent_tasks": recent_tasks,
                "recent_leads": recent_leads,
                "recommendation": self._get_churn_recommendation(churn_probability)
            }
        finally:
            db.close()
    
    def _get_churn_recommendation(self, probability: float) -> str:
        """Get recommendation based on churn probability."""
        if probability >= 60:
            return "High risk - Immediate engagement needed"
        elif probability >= 30:
            return "Medium risk - Proactive outreach recommended"
        else:
            return "Low risk - Continue normal engagement"
    
    def analyze_market_trends(
        self,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze market trends from lead data.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with trend analysis
        """
        db = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get trends by business type
            business_trends = db.query(
                Lead.business_type,
                func.count(Lead.id).label('count')
            ).filter(
                Lead.extracted_at >= cutoff_date,
                Lead.business_type.isnot(None),
                Lead.business_type != "N/A"
            ).group_by(Lead.business_type).order_by(
                func.count(Lead.id).desc()
            ).limit(10).all()
            
            # Get trends by location
            location_trends = db.query(
                Lead.city,
                func.count(Lead.id).label('count')
            ).filter(
                Lead.extracted_at >= cutoff_date,
                Lead.city.isnot(None),
                Lead.city != "N/A"
            ).group_by(Lead.city).order_by(
                func.count(Lead.id).desc()
            ).limit(10).all()
            
            # Calculate growth rates (simplified)
            # In production, would compare periods
            business_growth = {
                bt: {"count": count, "growth": "stable"}  # Simplified
                for bt, count in business_trends
            }
            
            location_growth = {
                city: {"count": count, "growth": "stable"}  # Simplified
                for city, count in location_trends
            }
            
            return {
                "period_days": days,
                "top_business_types": business_growth,
                "top_locations": location_growth,
                "insights": self._generate_trend_insights(business_trends, location_trends)
            }
        finally:
            db.close()
    
    def _generate_trend_insights(
        self,
        business_trends: List,
        location_trends: List
    ) -> List[str]:
        """Generate insights from trends."""
        insights = []
        
        if business_trends:
            top_business = business_trends[0][0]
            insights.append(f"Most active business type: {top_business}")
        
        if location_trends:
            top_location = location_trends[0][0]
            insights.append(f"Most active location: {top_location}")
        
        return insights


# Global instance
predictive_analytics_service = PredictiveAnalyticsService()

