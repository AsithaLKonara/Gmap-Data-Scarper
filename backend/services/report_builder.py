"""Custom report builder service."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.models.database import get_session
from backend.models.database import Lead, Task
from sqlalchemy import func, and_, or_


class ReportBuilderService:
    """Service for building custom reports."""
    
    def build_report(
        self,
        user_id: str,
        report_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build a custom report based on configuration.
        
        Args:
            user_id: User ID
            report_config: Report configuration
            
        Returns:
            Report data
        """
        db = get_session()
        try:
            # Get date range
            date_range = report_config.get("date_range", {})
            start_date = datetime.fromisoformat(date_range.get("start")) if date_range.get("start") else datetime.utcnow() - timedelta(days=30)
            end_date = datetime.fromisoformat(date_range.get("end")) if date_range.get("end") else datetime.utcnow()
            
            # Get user's tasks
            user_tasks = db.query(Task.task_id).filter(
                Task.user_id == user_id,
                Task.started_at >= start_date,
                Task.started_at <= end_date
            ).all()
            task_ids = [t[0] for t in user_tasks]
            
            if not task_ids:
                return self._empty_report()
            
            # Build query
            query = db.query(Lead).filter(
                Lead.task_id.in_(task_ids),
                Lead.extracted_at >= start_date,
                Lead.extracted_at <= end_date
            )
            
            # Apply filters
            filters = report_config.get("filters", {})
            if filters.get("platforms"):
                query = query.filter(Lead.platform.in_(filters["platforms"]))
            
            if filters.get("min_score"):
                query = query.filter(Lead.lead_score >= filters["min_score"])
            
            if filters.get("business_types"):
                query = query.filter(Lead.business_type.in_(filters["business_types"]))
            
            if filters.get("locations"):
                query = query.filter(Lead.city.in_(filters["locations"]))
            
            # Get metrics
            metrics = report_config.get("metrics", ["total", "by_platform", "by_score"])
            
            report_data = {
                "report_config": report_config,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_leads": query.count(),
            }
            
            # Add requested metrics
            if "by_platform" in metrics:
                platform_stats = db.query(
                    Lead.platform,
                    func.count(Lead.id).label('count')
                ).filter(
                    Lead.task_id.in_(task_ids),
                    Lead.extracted_at >= start_date,
                    Lead.extracted_at <= end_date
                ).group_by(Lead.platform).all()
                report_data["by_platform"] = {platform: count for platform, count in platform_stats}
            
            if "by_score" in metrics:
                score_stats = db.query(
                    Lead.lead_score_category,
                    func.count(Lead.id).label('count')
                ).filter(
                    Lead.task_id.in_(task_ids),
                    Lead.extracted_at >= start_date,
                    Lead.extracted_at <= end_date,
                    Lead.lead_score_category.isnot(None)
                ).group_by(Lead.lead_score_category).all()
                report_data["by_score"] = {category: count for category, count in score_stats}
            
            if "by_location" in metrics:
                location_stats = db.query(
                    Lead.city,
                    func.count(Lead.id).label('count')
                ).filter(
                    Lead.task_id.in_(task_ids),
                    Lead.extracted_at >= start_date,
                    Lead.extracted_at <= end_date,
                    Lead.city.isnot(None),
                    Lead.city != "N/A"
                ).group_by(Lead.city).order_by(func.count(Lead.id).desc()).limit(10).all()
                report_data["by_location"] = {city: count for city, count in location_stats}
            
            if "daily_trend" in metrics:
                daily_stats = db.query(
                    func.date(Lead.extracted_at).label('date'),
                    func.count(Lead.id).label('count')
                ).filter(
                    Lead.task_id.in_(task_ids),
                    Lead.extracted_at >= start_date,
                    Lead.extracted_at <= end_date
                ).group_by(func.date(Lead.extracted_at)).order_by(func.date(Lead.extracted_at)).all()
                report_data["daily_trend"] = [
                    {"date": date.isoformat() if isinstance(date, datetime) else str(date), "count": count}
                    for date, count in daily_stats
                ]
            
            return report_data
        finally:
            db.close()
    
    def _empty_report(self) -> Dict[str, Any]:
        """Return empty report structure."""
        return {
            "total_leads": 0,
            "by_platform": {},
            "by_score": {},
            "by_location": {},
            "daily_trend": []
        }
    
    def export_report(
        self,
        report_data: Dict[str, Any],
        format: str = "json"
    ) -> bytes:
        """
        Export report in specified format.
        
        Args:
            report_data: Report data
            format: Export format (json, csv, pdf)
            
        Returns:
            Exported file bytes
        """
        if format == "json":
            import json
            return json.dumps(report_data, indent=2).encode('utf-8')
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Metric", "Value"])
            
            # Write data
            writer.writerow(["Total Leads", report_data.get("total_leads", 0)])
            
            if "by_platform" in report_data:
                writer.writerow([])
                writer.writerow(["Platform", "Count"])
                for platform, count in report_data["by_platform"].items():
                    writer.writerow([platform, count])
            
            return output.getvalue().encode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global instance
report_builder_service = ReportBuilderService()

