"""Database query optimization utilities."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Query
from sqlalchemy import func, and_, or_
from backend.models.database import Lead, get_session


class QueryOptimizer:
    """Utilities for optimizing database queries."""
    
    @staticmethod
    def optimize_lead_query(
        task_id: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        limit: int = 1000,
        offset: int = 0,
        use_index_hint: bool = True
    ) -> Query:
        """
        Build optimized query with proper index usage.
        
        Args:
            task_id: Filter by task ID
            platform: Filter by platform
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum results
            offset: Offset for pagination
            use_index_hint: Use index hints for optimization
        
        Returns:
            Optimized SQLAlchemy query
        """
        db = get_session()
        query = db.query(Lead).filter(Lead.deleted_at.is_(None))  # Exclude soft-deleted leads
        
        # Apply filters in order of index availability
        # 1. Task + Platform (composite index)
        if task_id and platform:
            query = query.filter(
                and_(Lead.task_id == task_id, Lead.platform == platform)
            )
        elif task_id:
            query = query.filter(Lead.task_id == task_id)
        elif platform:
            query = query.filter(Lead.platform == platform)
        
        # 2. Date range (indexed field)
        if start_date:
            query = query.filter(Lead.extracted_at >= start_date)
        if end_date:
            query = query.filter(Lead.extracted_at <= end_date)
        
        # Order by indexed field for better performance
        query = query.order_by(Lead.extracted_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query
    
    @staticmethod
    def get_leads_with_phones(
        task_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Optimized query for leads with phone numbers.
        Uses index on phone_normalized.
        """
        db = get_session()
        try:
            query = db.query(Lead).filter(
                Lead.phone_normalized.isnot(None),
                Lead.deleted_at.is_(None)  # Exclude soft-deleted leads
            )
            
            if task_id:
                query = query.filter(Lead.task_id == task_id)
            
            leads = query.order_by(Lead.extracted_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": lead.id,
                    "display_name": lead.display_name,
                    "phone": lead.phone,
                    "phone_normalized": lead.phone_normalized,
                    "platform": lead.platform,
                    "extracted_at": lead.extracted_at.isoformat() if lead.extracted_at else None
                }
                for lead in leads
            ]
        finally:
            db.close()
    
    @staticmethod
    def get_leads_by_field_of_study(
        field_of_study: str,
        city: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Optimized query using composite index on field_of_study + city.
        """
        db = get_session()
        try:
            query = db.query(Lead).filter(
                Lead.field_of_study.ilike(f"%{field_of_study}%"),
                Lead.deleted_at.is_(None)  # Exclude soft-deleted leads
            )
            
            if city:
                query = query.filter(Lead.city.ilike(f"%{city}%"))
            
            leads = query.order_by(Lead.extracted_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": lead.id,
                    "display_name": lead.display_name,
                    "field_of_study": lead.field_of_study,
                    "city": lead.city,
                    "phone": lead.phone,
                    "platform": lead.platform
                }
                for lead in leads
            ]
        finally:
            db.close()
    
    @staticmethod
    def get_platform_statistics(
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Optimized query for platform statistics using aggregation.
        """
        db = get_session()
        try:
            query = db.query(Lead).filter(Lead.deleted_at.is_(None))  # Exclude soft-deleted leads
            
            if start_date:
                query = query.filter(Lead.extracted_at >= start_date)
            if end_date:
                query = query.filter(Lead.extracted_at <= end_date)
            
            # Use database aggregation for better performance
            platform_stats = db.query(
                Lead.platform,
                func.count(Lead.id).label('total'),
                func.count(Lead.phone_normalized).label('with_phone'),
                func.avg(
                    func.cast(Lead.followers, func.Integer)
                ).label('avg_followers')
            ).filter(Lead.deleted_at.is_(None)).group_by(Lead.platform).all()
            
            return {
                platform: {
                    "total": total,
                    "with_phone": with_phone,
                    "phone_coverage": (with_phone / total * 100) if total > 0 else 0,
                    "avg_followers": float(avg_followers) if avg_followers else 0
                }
                for platform, total, with_phone, avg_followers in platform_stats
            }
        finally:
            db.close()


# Global instance
_query_optimizer = None

def get_query_optimizer() -> QueryOptimizer:
    """Get or create global query optimizer instance."""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer

