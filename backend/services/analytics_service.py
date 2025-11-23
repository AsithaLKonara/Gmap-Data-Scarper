"""Advanced analytics service for dashboards and reporting."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.models.database import get_session
from backend.models.database import Lead, Task
from sqlalchemy import func, and_, or_


class AnalyticsService:
    """Service for generating analytics and insights."""
    
    def get_dashboard_metrics(
        self,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None,
        date_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics.
        
        Args:
            user_id: Filter by user ID
            team_id: Filter by team ID
            date_range_days: Number of days to analyze
            
        Returns:
            Dict with dashboard metrics
        """
        db = get_session()
        try:
            start_date = datetime.utcnow() - timedelta(days=date_range_days)
            
            # Base query filters
            filters = [Lead.extracted_at >= start_date]
            if user_id:
                # Get tasks for user
                user_tasks = db.query(Task.task_id).filter(Task.user_id == user_id).all()
                task_ids = [t[0] for t in user_tasks]
                if task_ids:
                    filters.append(Lead.task_id.in_(task_ids))
                else:
                    # No tasks, return empty metrics
                    return self._empty_metrics()
            
            # Total leads
            total_leads = db.query(func.count(Lead.id)).filter(*filters).scalar() or 0
            
            # Leads by platform
            platform_stats = db.query(
                Lead.platform,
                func.count(Lead.id).label('count')
            ).filter(*filters).group_by(Lead.platform).all()
            
            platform_breakdown = {platform: count for platform, count in platform_stats}
            
            # Leads by score category
            score_stats = db.query(
                Lead.lead_score_category,
                func.count(Lead.id).label('count')
            ).filter(
                *filters,
                Lead.lead_score_category.isnot(None)
            ).group_by(Lead.lead_score_category).all()
            
            score_breakdown = {category: count for category, count in score_stats}
            
            # Leads with phone numbers
            leads_with_phone = db.query(func.count(Lead.id)).filter(
                *filters,
                Lead.phone.isnot(None),
                Lead.phone != "N/A"
            ).scalar() or 0
            
            # Leads with email
            leads_with_email = db.query(func.count(Lead.id)).filter(
                *filters,
                Lead.email.isnot(None),
                Lead.email != "N/A"
            ).scalar() or 0
            
            # Average lead score
            avg_score = db.query(func.avg(Lead.lead_score)).filter(
                *filters,
                Lead.lead_score.isnot(None)
            ).scalar() or 0
            
            # Top business types
            business_type_stats = db.query(
                Lead.business_type,
                func.count(Lead.id).label('count')
            ).filter(
                *filters,
                Lead.business_type.isnot(None),
                Lead.business_type != "N/A"
            ).group_by(Lead.business_type).order_by(
                func.count(Lead.id).desc()
            ).limit(10).all()
            
            business_type_breakdown = {bt: count for bt, count in business_type_stats}
            
            # Leads by day (for trend chart)
            daily_stats = db.query(
                func.date(Lead.extracted_at).label('date'),
                func.count(Lead.id).label('count')
            ).filter(*filters).group_by(
                func.date(Lead.extracted_at)
            ).order_by(func.date(Lead.extracted_at)).all()
            
            daily_trend = [
                {"date": date.isoformat() if isinstance(date, datetime) else str(date), "count": count}
                for date, count in daily_stats
            ]
            
            # Top locations
            location_stats = db.query(
                Lead.city,
                func.count(Lead.id).label('count')
            ).filter(
                *filters,
                Lead.city.isnot(None),
                Lead.city != "N/A"
            ).group_by(Lead.city).order_by(
                func.count(Lead.id).desc()
            ).limit(10).all()
            
            location_breakdown = {city: count for city, count in location_stats}
            
            return {
                "total_leads": total_leads,
                "leads_with_phone": leads_with_phone,
                "leads_with_email": leads_with_email,
                "phone_coverage": (leads_with_phone / total_leads * 100) if total_leads > 0 else 0,
                "email_coverage": (leads_with_email / total_leads * 100) if total_leads > 0 else 0,
                "average_lead_score": round(float(avg_score), 2) if avg_score else 0,
                "platform_breakdown": platform_breakdown,
                "score_breakdown": score_breakdown,
                "business_type_breakdown": business_type_breakdown,
                "location_breakdown": location_breakdown,
                "daily_trend": daily_trend,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": datetime.utcnow().isoformat(),
                    "days": date_range_days
                }
            }
        finally:
            db.close()
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure."""
        return {
            "total_leads": 0,
            "leads_with_phone": 0,
            "leads_with_email": 0,
            "phone_coverage": 0,
            "email_coverage": 0,
            "average_lead_score": 0,
            "platform_breakdown": {},
            "score_breakdown": {},
            "business_type_breakdown": {},
            "location_breakdown": {},
            "daily_trend": [],
            "date_range": {
                "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end": datetime.utcnow().isoformat(),
                "days": 30
            }
        }
    
    def get_pipeline_metrics(
        self,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get lead pipeline metrics (funnel analysis).
        
        Returns:
            Dict with pipeline stages and conversion rates
        """
        db = get_session()
        try:
            # Get all leads
            filters = []
            if user_id:
                user_tasks = db.query(Task.task_id).filter(Task.user_id == user_id).all()
                task_ids = [t[0] for t in user_tasks]
                if task_ids:
                    filters.append(Lead.task_id.in_(task_ids))
                else:
                    return self._empty_pipeline()
            
            total_leads = db.query(func.count(Lead.id)).filter(*filters).scalar() or 0
            
            # Stage 1: Leads with contact info
            with_contact = db.query(func.count(Lead.id)).filter(
                *filters,
                or_(
                    and_(Lead.phone.isnot(None), Lead.phone != "N/A"),
                    and_(Lead.email.isnot(None), Lead.email != "N/A")
                )
            ).scalar() or 0
            
            # Stage 2: Verified leads (with phone verification)
            verified = db.query(func.count(Lead.id)).filter(
                *filters,
                Lead.phone.isnot(None),
                Lead.phone != "N/A"
                # Note: Add phone verification status check if available
            ).scalar() or 0
            
            # Stage 3: High-quality leads (score >= 70)
            high_quality = db.query(func.count(Lead.id)).filter(
                *filters,
                Lead.lead_score >= 70
            ).scalar() or 0
            
            # Stage 4: Hot leads (score >= 80)
            hot_leads = db.query(func.count(Lead.id)).filter(
                *filters,
                Lead.lead_score >= 80
            ).scalar() or 0
            
            return {
                "stages": [
                    {
                        "name": "Total Leads",
                        "count": total_leads,
                        "percentage": 100.0
                    },
                    {
                        "name": "With Contact Info",
                        "count": with_contact,
                        "percentage": (with_contact / total_leads * 100) if total_leads > 0 else 0
                    },
                    {
                        "name": "Verified",
                        "count": verified,
                        "percentage": (verified / total_leads * 100) if total_leads > 0 else 0
                    },
                    {
                        "name": "High Quality (70+)",
                        "count": high_quality,
                        "percentage": (high_quality / total_leads * 100) if total_leads > 0 else 0
                    },
                    {
                        "name": "Hot Leads (80+)",
                        "count": hot_leads,
                        "percentage": (hot_leads / total_leads * 100) if total_leads > 0 else 0
                    }
                ],
                "conversion_rates": {
                    "contact_rate": (with_contact / total_leads * 100) if total_leads > 0 else 0,
                    "verification_rate": (verified / with_contact * 100) if with_contact > 0 else 0,
                    "quality_rate": (high_quality / total_leads * 100) if total_leads > 0 else 0,
                    "hot_rate": (hot_leads / total_leads * 100) if total_leads > 0 else 0
                }
            }
        finally:
            db.close()
    
    def _empty_pipeline(self) -> Dict[str, Any]:
        """Return empty pipeline structure."""
        return {
            "stages": [
                {"name": "Total Leads", "count": 0, "percentage": 0},
                {"name": "With Contact Info", "count": 0, "percentage": 0},
                {"name": "Verified", "count": 0, "percentage": 0},
                {"name": "High Quality (70+)", "count": 0, "percentage": 0},
                {"name": "Hot Leads (80+)", "count": 0, "percentage": 0}
            ],
            "conversion_rates": {
                "contact_rate": 0,
                "verification_rate": 0,
                "quality_rate": 0,
                "hot_rate": 0
            }
        }
    
    def get_revenue_forecast(
        self,
        user_id: Optional[str] = None,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Generate revenue forecast based on lead trends.
        
        Args:
            user_id: Filter by user ID
            days_ahead: Number of days to forecast
            
        Returns:
            Dict with forecast data
        """
        db = get_session()
        try:
            # Get historical data (last 30 days)
            start_date = datetime.utcnow() - timedelta(days=30)
            
            filters = [Lead.extracted_at >= start_date]
            if user_id:
                user_tasks = db.query(Task.task_id).filter(Task.user_id == user_id).all()
                task_ids = [t[0] for t in user_tasks]
                if task_ids:
                    filters.append(Lead.task_id.in_(task_ids))
                else:
                    return {"forecast": [], "trend": "stable", "estimated_leads": 0}
            
            # Daily lead counts
            daily_counts = db.query(
                func.date(Lead.extracted_at).label('date'),
                func.count(Lead.id).label('count')
            ).filter(*filters).group_by(
                func.date(Lead.extracted_at)
            ).order_by(func.date(Lead.extracted_at)).all()
            
            if not daily_counts:
                return {"forecast": [], "trend": "stable", "estimated_leads": 0}
            
            # Calculate average daily leads
            counts = [count for _, count in daily_counts]
            avg_daily = sum(counts) / len(counts) if counts else 0
            
            # Simple trend calculation (linear regression)
            if len(counts) > 1:
                trend_slope = (counts[-1] - counts[0]) / len(counts)
                if trend_slope > 0.1:
                    trend = "growing"
                elif trend_slope < -0.1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Generate forecast
            forecast = []
            base_date = datetime.utcnow().date()
            for i in range(days_ahead):
                forecast_date = base_date + timedelta(days=i)
                # Simple forecast: use average with trend adjustment
                estimated = avg_daily + (trend_slope * i if len(counts) > 1 else 0)
                forecast.append({
                    "date": forecast_date.isoformat(),
                    "estimated_leads": max(0, int(estimated))
                })
            
            total_estimated = sum(f["estimated_leads"] for f in forecast)
            
            return {
                "forecast": forecast,
                "trend": trend,
                "estimated_leads": total_estimated,
                "average_daily": round(avg_daily, 2),
                "trend_slope": round(trend_slope, 2) if len(counts) > 1 else 0
            }
        finally:
            db.close()


# Global instance
analytics_service = AnalyticsService()

