"""PostgreSQL storage service for leads with dual-write support."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from backend.models.database import Lead, Task, get_session, init_db, close_db
from backend.services.query_optimizer import get_query_optimizer
from backend.models.schemas import ScrapeResult
import csv
import os
import json
from pathlib import Path


class PostgreSQLStorage:
    """PostgreSQL storage service with dual-write (CSV + DB) support."""
    
    def __init__(self, enable_csv_dual_write: bool = True):
        """
        Initialize PostgreSQL storage.
        
        Args:
            enable_csv_dual_write: If True, also write to CSV files (for migration period)
        """
        self.enable_csv_dual_write = enable_csv_dual_write
        self.csv_dir = Path("data")
        self.csv_dir.mkdir(exist_ok=True)
        init_db()
    
    def save_leads_batch(
        self,
        task_id: str,
        results: List[Dict[str, Any]],
        db_session: Optional[Session] = None,
        batch_size: int = 100,
        user_id: Optional[str] = None
    ) -> int:
        """
        Save multiple leads in a batch operation for better performance.
        
        Args:
            task_id: Task identifier
            results: List of lead data dictionaries
            db_session: Optional database session (for testing)
            batch_size: Number of leads to insert per batch
            
        Returns:
            Number of leads successfully saved
        """
        if not results:
            return 0
        
        saved_count = 0
        db = db_session if db_session else get_session()
        should_close = db_session is None
        
        try:
            # Process in batches
            for i in range(0, len(results), batch_size):
                batch = results[i:i + batch_size]
                leads_to_add = []
                
                for result in batch:
                    # Check for duplicate
                    profile_url = result.get("profile_url", "")
                    existing = db.query(Lead).filter(
                        Lead.task_id == task_id,
                        Lead.profile_url == profile_url,
                        Lead.deleted_at.is_(None)  # Exclude soft-deleted leads
                    ).first()
                    
                    if existing:
                        continue  # Skip duplicate
                    
                    # Extract phone data
                    phones_data = result.get("phones", [])
                    phone = result.get("phone") or (phones_data[0].get("raw_phone") if phones_data else None)
                    phone_normalized = None
                    if phones_data:
                        phone_normalized = phones_data[0].get("normalized_e164")
                    
                    # Create lead record
                    lead = Lead(
                        task_id=task_id,
                        search_query=result.get("search_query", ""),
                        platform=result.get("platform", ""),
                        profile_url=profile_url,
                        handle=result.get("handle"),
                        display_name=result.get("display_name"),
                        bio_about=result.get("bio_about"),
                        website=result.get("website"),
                        email=result.get("email"),
                        phone=phone,
                        phone_normalized=phone_normalized,
                        followers=result.get("followers"),
                        location=result.get("location"),
                        phones_data=phones_data if phones_data else None,
                        business_type=result.get("business_type"),
                        industry=result.get("industry"),
                        city=result.get("city"),
                        region=result.get("region"),
                        country=result.get("country"),
                        job_title=result.get("job_title"),
                        seniority_level=result.get("seniority_level"),
                        education_level=result.get("education_level"),
                        institution_name=result.get("institution_name"),
                        lead_type=result.get("lead_type"),
                        field_of_study=result.get("field_of_study"),
                        degree_program=result.get("degree_program"),
                        graduation_year=result.get("graduation_year"),
                        extracted_at=datetime.now(timezone.utc),
                    )
                    
                    # Set audit fields
                    from backend.utils.audit_trail import set_audit_fields
                    audit_user_id = user_id or result.get("user_id")
                    set_audit_fields(lead, user_id=audit_user_id, is_creation=True)
                    
                    leads_to_add.append(lead)
                
                # Bulk insert batch
                if leads_to_add:
                    db.bulk_save_objects(leads_to_add)
                    db.commit()
                    saved_count += len(leads_to_add)
                    
                    # Dual-write to CSV if enabled
                    if self.enable_csv_dual_write:
                        for result in batch:
                            self._write_to_csv(task_id, result)
                
        except Exception as e:
            db.rollback()
            import logging
            logging.error(f"[POSTGRES] Error saving leads batch: {e}")
        finally:
            if should_close:
                db.close()
        
        return saved_count
    
    def save_lead(
        self,
        task_id: str,
        result: Dict[str, Any],
        db_session: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Save a lead to PostgreSQL (and optionally CSV).
        
        Args:
            task_id: Task identifier
            result: Lead data dictionary
            db_session: Optional database session (for testing)
            
        Returns:
            True if saved successfully
        """
        try:
            db = db_session if db_session else get_session()
            should_close = db_session is None
            try:
                # Check for duplicate (same profile_url and task_id)
                profile_url = result.get("profile_url", "")
                existing = db.query(Lead).filter(
                    Lead.task_id == task_id,
                    Lead.profile_url == profile_url,
                    Lead.deleted_at.is_(None)  # Exclude soft-deleted leads
                ).first()
                
                if existing:
                    # Duplicate found, skip saving
                    return True
                
                # Extract phone data
                phones_data = result.get("phones", [])
                phone = result.get("phone") or (phones_data[0].get("raw_phone") if phones_data else None)
                phone_normalized = None
                if phones_data:
                    phone_normalized = phones_data[0].get("normalized_e164")
                
                # Create lead record
                lead = Lead(
                    task_id=task_id,
                    search_query=result.get("search_query", ""),
                    platform=result.get("platform", ""),
                    profile_url=result.get("profile_url", ""),
                    handle=result.get("handle"),
                    display_name=result.get("display_name"),
                    bio_about=result.get("bio_about"),
                    website=result.get("website"),
                    email=result.get("email"),
                    phone=phone,
                    phone_normalized=phone_normalized,
                    followers=result.get("followers"),
                    location=result.get("location"),
                    phones_data=phones_data if phones_data else None,
                    business_type=result.get("business_type"),
                    industry=result.get("industry"),
                    city=result.get("city"),
                    region=result.get("region"),
                    country=result.get("country"),
                    job_title=result.get("job_title"),
                    seniority_level=result.get("seniority_level"),
                    education_level=result.get("education_level"),
                    institution_name=result.get("institution_name"),
                    lead_type=result.get("lead_type"),
                    field_of_study=result.get("field_of_study"),
                    degree_program=result.get("degree_program"),
                        graduation_year=result.get("graduation_year"),
                    extracted_at=datetime.now(timezone.utc),
                )
                
                db.add(lead)
                db.commit()
                db.refresh(lead)
                
                # Track audit log for new lead
                if user_id:
                    track_change(
                        table_name="leads",
                        record_id=str(lead.id),
                        action="create",
                        user_id=user_id,
                        metadata={"task_id": task_id, "platform": lead.platform, "profile_url": lead.profile_url}
                    )
                
                # Dual-write to CSV if enabled
                if self.enable_csv_dual_write:
                    self._write_to_csv(task_id, result)
                
                return True
            finally:
                if should_close:
                    db.close()
        except Exception as e:
            import logging
            logging.error(f"[POSTGRES] Error saving lead: {e}", exc_info=True)
            return False
    
    def _write_to_csv(self, task_id: str, result: Dict[str, Any]):
        """Write lead to CSV file (dual-write during migration)."""
        try:
            csv_file = self.csv_dir / f"leads_{task_id}.csv"
            file_exists = csv_file.exists()
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'Display Name', 'Phone', 'Email', 'Website', 'Location',
                    'Platform', 'Profile URL', 'Handle', 'Bio/About',
                    'Field of Study', 'Institution', 'Business Type', 'Industry',
                    'City', 'Region', 'Country', 'Job Title', 'Seniority Level',
                    'Education Level', 'Lead Type', 'Degree Program', 'Graduation Year',
                    'Extracted At'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                # Extract phone
                phone = result.get("phone") or ""
                if not phone and result.get("phones"):
                    phone = result["phones"][0].get("raw_phone", "")
                
                writer.writerow({
                    'Display Name': result.get("display_name", ""),
                    'Phone': phone,
                    'Email': result.get("email", ""),
                    'Website': result.get("website", ""),
                    'Location': result.get("location", ""),
                    'Platform': result.get("platform", ""),
                    'Profile URL': result.get("profile_url", ""),
                    'Handle': result.get("handle", ""),
                    'Bio/About': result.get("bio_about", ""),
                    'Field of Study': result.get("field_of_study", ""),
                    'Institution': result.get("institution_name", ""),
                    'Business Type': result.get("business_type", ""),
                    'Industry': result.get("industry", ""),
                    'City': result.get("city", ""),
                    'Region': result.get("region", ""),
                    'Country': result.get("country", ""),
                    'Job Title': result.get("job_title", ""),
                    'Seniority Level': result.get("seniority_level", ""),
                    'Education Level': result.get("education_level", ""),
                    'Lead Type': result.get("lead_type", ""),
                    'Degree Program': result.get("degree_program", ""),
                    'Graduation Year': result.get("graduation_year", ""),
                    'Extracted At': datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            import logging
            logging.error(f"[CSV] Error writing to CSV: {e}", exc_info=True)
    
    def get_leads(
        self,
        task_id: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query leads from PostgreSQL.
        
        Args:
            task_id: Filter by task ID
            platform: Filter by platform
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            List of lead dictionaries
        """
        try:
            # Use query optimizer for better performance
            optimizer = get_query_optimizer()
            query = optimizer.optimize_lead_query(
                task_id=task_id,
                platform=platform,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset
            )
            
            leads = query.all()
            
            # Batch convert to dict for better performance
            return [self._lead_to_dict(lead) for lead in leads]
        except Exception as e:
            import logging
            logging.error(f"[POSTGRES] Error querying leads: {e}", exc_info=True)
            return []
    
    def _lead_to_dict(self, lead: Lead) -> Dict[str, Any]:
        """Convert Lead model to dictionary."""
        return {
            "search_query": lead.search_query,
            "platform": lead.platform,
            "profile_url": lead.profile_url,
            "handle": lead.handle,
            "display_name": lead.display_name,
            "bio_about": lead.bio_about,
            "website": lead.website,
            "email": lead.email,
            "phone": lead.phone,
            "followers": lead.followers,
            "location": lead.location,
            "phones": lead.phones_data or [],
            "business_type": lead.business_type,
            "industry": lead.industry,
            "city": lead.city,
            "region": lead.region,
            "country": lead.country,
            "job_title": lead.job_title,
            "seniority_level": lead.seniority_level,
            "education_level": lead.education_level,
            "institution_name": lead.institution_name,
            "lead_type": lead.lead_type,
            "field_of_study": lead.field_of_study,
            "degree_program": lead.degree_program,
            "graduation_year": lead.graduation_year,
            "extracted_at": lead.extracted_at.isoformat() if lead.extracted_at else None,
        }
    
    def get_stats(
        self,
        task_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about leads.
        
        Returns:
            Dictionary with stats (total, by_platform, by_field_of_study, etc.)
        """
        try:
            db = get_session()
            try:
                query = db.query(Lead)
                
                if task_id:
                    query = query.filter(Lead.task_id == task_id)
                if start_date:
                    query = query.filter(Lead.extracted_at >= start_date)
                if end_date:
                    query = query.filter(Lead.extracted_at <= end_date)
                
                # Optimized: Use single query with conditional aggregation
                total = query.count()
                with_phone = query.filter(Lead.phone.isnot(None)).count()
                
                # By platform (optimized with index)
                platform_stats = db.query(
                    Lead.platform,
                    func.count(Lead.id).label('count')
                ).filter(Lead.deleted_at.is_(None)).group_by(Lead.platform).order_by(func.count(Lead.id).desc()).all()
                
                # By field of study (optimized with index)
                field_stats = db.query(
                    Lead.field_of_study,
                    func.count(Lead.id).label('count')
                ).filter(Lead.field_of_study.isnot(None), Lead.deleted_at.is_(None)).group_by(Lead.field_of_study).order_by(func.count(Lead.id).desc()).limit(20).all()
                
                return {
                    "total": total,
                    "with_phone": with_phone,
                    "phone_coverage": (with_phone / total * 100) if total > 0 else 0,
                    "by_platform": {p: c for p, c in platform_stats},
                    "by_field_of_study": {f: c for f, c in field_stats if f},
                }
            finally:
                db.close()
        except Exception as e:
            import logging
            logging.error(f"[POSTGRES] Error getting stats: {e}", exc_info=True)
            return {
                "total": 0,
                "with_phone": 0,
                "phone_coverage": 0,
                "by_platform": {},
                "by_field_of_study": {},
            }


# Global instance
_postgresql_storage: Optional[PostgreSQLStorage] = None


def get_postgresql_storage() -> PostgreSQLStorage:
    """Get or create global PostgreSQL storage instance."""
    global _postgresql_storage
    if _postgresql_storage is None:
        _postgresql_storage = PostgreSQLStorage(enable_csv_dual_write=True)
    return _postgresql_storage

