"""Advanced duplicate detection service across platforms and tasks."""
from typing import Dict, Any, List, Set, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_
from backend.models.database import Lead, get_session
import hashlib
import re


class DuplicateDetectionService:
    """Detects duplicate leads across platforms and tasks."""
    
    def __init__(self):
        """Initialize duplicate detection service."""
        self.similarity_threshold = 0.85  # 85% similarity for duplicates
    
    def is_duplicate(
        self,
        lead_data: Dict[str, Any],
        task_id: Optional[str] = None,
        check_across_tasks: bool = True
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Check if a lead is a duplicate.
        
        Args:
            lead_data: Lead data dictionary
            task_id: Current task ID (to exclude from search)
            check_across_tasks: If True, check across all tasks
        
        Returns:
            Tuple of (is_duplicate, reason, existing_lead_data)
        """
        db = get_session()
        try:
            # 1. Check by normalized phone number (strongest match)
            phone_normalized = lead_data.get("phone_normalized") or self._normalize_phone(
                lead_data.get("phone", "")
            )
            if phone_normalized and phone_normalized != "N/A":
                query = db.query(Lead).filter(Lead.phone_normalized == phone_normalized)
                if not check_across_tasks and task_id:
                    query = query.filter(Lead.task_id == task_id)
                existing = query.first()
                if existing:
                    return (True, "duplicate_phone", self._lead_to_dict(existing))
            
            # 2. Check by profile URL (strong match)
            profile_url = lead_data.get("profile_url", "")
            if profile_url and profile_url != "N/A":
                query = db.query(Lead).filter(Lead.profile_url == profile_url)
                if not check_across_tasks and task_id:
                    query = query.filter(Lead.task_id == task_id)
                existing = query.first()
                if existing:
                    return (True, "duplicate_url", self._lead_to_dict(existing))
            
            # 3. Check by email (if available)
            email = lead_data.get("email", "")
            if email and email != "N/A" and "@" in email:
                query = db.query(Lead).filter(Lead.email == email.lower().strip())
                if not check_across_tasks and task_id:
                    query = query.filter(Lead.task_id == task_id)
                existing = query.first()
                if existing:
                    return (True, "duplicate_email", self._lead_to_dict(existing))
            
            # 4. Check by name + location similarity (fuzzy match)
            display_name = lead_data.get("display_name", "")
            location = lead_data.get("location", "")
            if display_name and display_name != "N/A":
                # Get similar names
                similar_leads = db.query(Lead).filter(
                    Lead.display_name.ilike(f"%{display_name[:20]}%")
                ).all()
                
                for existing_lead in similar_leads:
                    if task_id and existing_lead.task_id == task_id and not check_across_tasks:
                        continue
                    
                    # Check name similarity
                    name_similarity = self._calculate_similarity(
                        display_name.lower(),
                        existing_lead.display_name.lower() if existing_lead.display_name else ""
                    )
                    
                    # Check location similarity if both have locations
                    location_match = False
                    if location and existing_lead.location:
                        location_similarity = self._calculate_similarity(
                            location.lower(),
                            existing_lead.location.lower()
                        )
                        location_match = location_similarity > 0.7
                    
                    # If name is very similar and location matches, it's likely a duplicate
                    if name_similarity > self.similarity_threshold:
                        if not location or location_match:
                            return (True, "duplicate_name_location", self._lead_to_dict(existing_lead))
            
            # 5. Check by website (if available)
            website = lead_data.get("website", "")
            if website and website != "N/A":
                normalized_website = self._normalize_website(website)
                if normalized_website:
                    # Check for similar websites
                    all_leads = db.query(Lead).filter(Lead.website.isnot(None)).all()
                    for existing_lead in all_leads:
                        if task_id and existing_lead.task_id == task_id and not check_across_tasks:
                            continue
                        
                        if existing_lead.website:
                            existing_normalized = self._normalize_website(existing_lead.website)
                            if normalized_website == existing_normalized:
                                return (True, "duplicate_website", self._lead_to_dict(existing_lead))
            
            return (False, None, None)
        finally:
            db.close()
    
    def find_duplicates(
        self,
        lead_data: Dict[str, Any],
        task_id: Optional[str] = None,
        check_across_tasks: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find all potential duplicates for a lead.
        
        Returns:
            List of duplicate lead dictionaries
        """
        db = get_session()
        duplicates = []
        try:
            # Get all potential matches
            phone_normalized = lead_data.get("phone_normalized") or self._normalize_phone(
                lead_data.get("phone", "")
            )
            profile_url = lead_data.get("profile_url", "")
            email = lead_data.get("email", "")
            display_name = lead_data.get("display_name", "")
            
            # By phone
            if phone_normalized and phone_normalized != "N/A":
                matches = db.query(Lead).filter(Lead.phone_normalized == phone_normalized).all()
                duplicates.extend([self._lead_to_dict(m) for m in matches])
            
            # By URL
            if profile_url and profile_url != "N/A":
                matches = db.query(Lead).filter(Lead.profile_url == profile_url).all()
                duplicates.extend([self._lead_to_dict(m) for m in matches])
            
            # By email
            if email and email != "N/A" and "@" in email:
                matches = db.query(Lead).filter(Lead.email == email.lower().strip()).all()
                duplicates.extend([self._lead_to_dict(m) for m in matches])
            
            # Remove duplicates from list
            seen_ids = set()
            unique_duplicates = []
            for dup in duplicates:
                dup_id = dup.get("id")
                if dup_id and dup_id not in seen_ids:
                    seen_ids.add(dup_id)
                    unique_duplicates.append(dup)
            
            return unique_duplicates
        finally:
            db.close()
    
    def _normalize_phone(self, phone: str) -> Optional[str]:
        """Normalize phone number to E.164 format."""
        if not phone or phone == "N/A":
            return None
        
        # Remove all non-digit characters except +
        normalized = re.sub(r'[^\d+]', '', phone)
        
        # Add + if missing and starts with digit
        if normalized and not normalized.startswith('+'):
            # Assume US number if 10 digits
            if len(normalized) == 10:
                normalized = f"+1{normalized}"
            else:
                normalized = f"+{normalized}"
        
        return normalized if normalized else None
    
    def _normalize_website(self, website: str) -> Optional[str]:
        """Normalize website URL for comparison."""
        if not website or website == "N/A":
            return None
        
        # Remove protocol
        website = website.replace("http://", "").replace("https://", "")
        
        # Remove www.
        if website.startswith("www."):
            website = website[4:]
        
        # Remove trailing slash
        website = website.rstrip("/")
        
        # Convert to lowercase
        website = website.lower()
        
        return website if website else None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (simple Jaccard similarity)."""
        if not str1 or not str2:
            return 0.0
        
        # Tokenize
        tokens1 = set(str1.split())
        tokens2 = set(str2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def _lead_to_dict(self, lead: Lead) -> Dict[str, Any]:
        """Convert Lead model to dictionary."""
        return {
            "id": lead.id,
            "task_id": lead.task_id,
            "display_name": lead.display_name,
            "phone": lead.phone,
            "phone_normalized": lead.phone_normalized,
            "profile_url": lead.profile_url,
            "email": lead.email,
            "website": lead.website,
            "location": lead.location,
            "platform": lead.platform,
            "extracted_at": lead.extracted_at.isoformat() if lead.extracted_at else None,
        }


# Global instance
_duplicate_detection_service = None

def get_duplicate_detection_service() -> DuplicateDetectionService:
    """Get or create global duplicate detection service instance."""
    global _duplicate_detection_service
    if _duplicate_detection_service is None:
        _duplicate_detection_service = DuplicateDetectionService()
    return _duplicate_detection_service

