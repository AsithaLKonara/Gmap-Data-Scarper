"""Data archival service for managing old data."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from backend.models.database import Lead, get_session
import os
import json
from pathlib import Path


class DataArchivalService:
    """Manages archival of old lead data."""
    
    def __init__(
        self,
        retention_days: int = 180,  # 6 months default
        archive_dir: Optional[str] = None
    ):
        """
        Initialize archival service.
        
        Args:
            retention_days: Number of days to retain data before archiving
            archive_dir: Directory to store archived data
        """
        self.retention_days = retention_days
        self.archive_dir = Path(archive_dir) if archive_dir else Path(
            os.path.expanduser("~/Documents/lead_intelligence_archive")
        )
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def archive_old_leads(
        self,
        dry_run: bool = False,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Archive leads older than retention period.
        
        Args:
            dry_run: If True, only report what would be archived
            batch_size: Number of leads to process per batch
        
        Returns:
            Dictionary with archival statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        db = get_session()
        try:
            # Count leads to archive
            count_query = db.query(func.count(Lead.id)).filter(
                Lead.extracted_at < cutoff_date
            )
            total_to_archive = count_query.scalar() or 0
            
            if total_to_archive == 0:
                return {
                    "archived_count": 0,
                    "total_found": 0,
                    "archived_files": [],
                    "errors": []
                }
            
            if dry_run:
                return {
                    "archived_count": 0,
                    "total_found": total_to_archive,
                    "archived_files": [],
                    "dry_run": True
                }
            
            # Archive in batches
            archived_count = 0
            archived_files = []
            errors = []
            offset = 0
            
            while offset < total_to_archive:
                try:
                    # Get batch of old leads
                    leads = db.query(Lead).filter(
                        Lead.extracted_at < cutoff_date
                    ).limit(batch_size).offset(offset).all()
                    
                    if not leads:
                        break
                    
                    # Group by extraction date for file organization
                    date_groups: Dict[str, List[Dict]] = {}
                    for lead in leads:
                        date_key = lead.extracted_at.strftime("%Y-%m") if lead.extracted_at else "unknown"
                        if date_key not in date_groups:
                            date_groups[date_key] = []
                        date_groups[date_key].append(self._lead_to_dict(lead))
                    
                    # Write to archive files
                    for date_key, lead_data in date_groups.items():
                        archive_file = self.archive_dir / f"leads_{date_key}.json"
                        
                        # Load existing data if file exists
                        existing_data = []
                        if archive_file.exists():
                            try:
                                with open(archive_file, 'r', encoding='utf-8') as f:
                                    existing_data = json.load(f)
                            except Exception as e:
                                import logging
                                logging.debug(f"Error loading existing archive data from {archive_file}: {e}")
                                existing_data = []
                        
                        # Append new data
                        existing_data.extend(lead_data)
                        
                        # Write back
                        with open(archive_file, 'w', encoding='utf-8') as f:
                            json.dump(existing_data, f, indent=2, default=str)
                        
                        if archive_file not in archived_files:
                            archived_files.append(str(archive_file))
                    
                    # Delete from database
                    lead_ids = [lead.id for lead in leads]
                    db.query(Lead).filter(Lead.id.in_(lead_ids)).delete(synchronize_session=False)
                    db.commit()
                    
                    archived_count += len(leads)
                    offset += batch_size
                    
                except Exception as e:
                    errors.append(f"Batch at offset {offset}: {str(e)}")
                    db.rollback()
                    offset += batch_size
            
            return {
                "archived_count": archived_count,
                "total_found": total_to_archive,
                "archived_files": archived_files,
                "errors": errors
            }
        finally:
            db.close()
    
    def get_archival_stats(self) -> Dict[str, Any]:
        """Get statistics about data eligible for archival."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        db = get_session()
        try:
            # Count leads to archive
            count = db.query(func.count(Lead.id)).filter(
                Lead.extracted_at < cutoff_date
            ).scalar() or 0
            
            # Get oldest lead date
            oldest = db.query(func.min(Lead.extracted_at)).scalar()
            
            # Get total leads
            total = db.query(func.count(Lead.id)).scalar() or 0
            
            return {
                "total_leads": total,
                "leads_to_archive": count,
                "oldest_lead_date": oldest.isoformat() if oldest else None,
                "retention_days": self.retention_days,
                "cutoff_date": cutoff_date.isoformat()
            }
        finally:
            db.close()
    
    def restore_from_archive(
        self,
        archive_file: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Restore leads from archive file.
        
        Args:
            archive_file: Path to archive JSON file
            dry_run: If True, only report what would be restored
        
        Returns:
            Dictionary with restoration statistics
        """
        archive_path = Path(archive_file)
        if not archive_path.exists():
            return {
                "restored_count": 0,
                "errors": [f"Archive file not found: {archive_file}"]
            }
        
        try:
            with open(archive_path, 'r', encoding='utf-8') as f:
                archived_leads = json.load(f)
            
            if dry_run:
                return {
                    "restored_count": 0,
                    "total_found": len(archived_leads),
                    "dry_run": True
                }
            
            # Restore to database
            from backend.services.postgresql_storage import get_postgresql_storage
            storage = get_postgresql_storage()
            
            restored_count = 0
            errors = []
            
            for lead_data in archived_leads:
                try:
                    # Use original task_id or generate new one
                    task_id = lead_data.get("task_id", "restored")
                    storage.save_lead(task_id, lead_data)
                    restored_count += 1
                except Exception as e:
                    errors.append(f"Failed to restore lead: {str(e)}")
            
            return {
                "restored_count": restored_count,
                "total_found": len(archived_leads),
                "errors": errors
            }
        except Exception as e:
            return {
                "restored_count": 0,
                "errors": [f"Failed to read archive: {str(e)}"]
            }
    
    def _lead_to_dict(self, lead: Lead) -> Dict[str, Any]:
        """Convert Lead model to dictionary."""
        return {
            "id": lead.id,
            "task_id": lead.task_id,
            "search_query": lead.search_query,
            "platform": lead.platform,
            "profile_url": lead.profile_url,
            "handle": lead.handle,
            "display_name": lead.display_name,
            "bio_about": lead.bio_about,
            "website": lead.website,
            "email": lead.email,
            "phone": lead.phone,
            "phone_normalized": lead.phone_normalized,
            "followers": lead.followers,
            "location": lead.location,
            "phones_data": lead.phones_data,
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
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }


# Global instance
_archival_service = None

def get_archival_service() -> DataArchivalService:
    """Get or create global archival service instance."""
    global _archival_service
    if _archival_service is None:
        retention_days = int(os.getenv("DATA_RETENTION_DAYS", "180"))
        _archival_service = DataArchivalService(retention_days=retention_days)
    return _archival_service

