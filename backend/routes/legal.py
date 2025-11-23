"""Legal and compliance endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import os
import csv
import json
from pathlib import Path
from backend.services.optout_service import optout_service
from backend.models.database import get_session
from backend.models.data_request import DataRequest, RequestType, RequestStatus
from backend.models.database import Lead

router = APIRouter(prefix="/api/legal", tags=["legal"])


class OptOutRequest(BaseModel):
    """Opt-out request model."""
    profile_url: str
    email: Optional[EmailStr] = None


class DataAccessRequest(BaseModel):
    """GDPR data access request model."""
    email: EmailStr
    profile_url: Optional[str] = None


class DataDeletionRequest(BaseModel):
    """GDPR data deletion request model."""
    email: EmailStr
    profile_url: Optional[str] = None
    reason: Optional[str] = None


@router.post("/opt-out")
async def create_optout_request(request: OptOutRequest):
    """
    Create an opt-out request with tracking.
    
    Args:
        request: Opt-out request with profile URL and optional email
    """
    # Create request in database
    request_id = optout_service.create_request(
        profile_url=request.profile_url,
        email=request.email
    )
    
    # Process the removal
    try:
        result = await process_optout(request.profile_url)
        optout_service.update_request_status(
            request_id,
            "completed",
            removed_count=result["removed_count"],
            files_processed=result["files_processed"]
        )
        
        return {
            "status": "success",
            "request_id": request_id,
            "removed_count": result["removed_count"],
            "files_processed": result["files_processed"],
            "message": f"Removed {result['removed_count']} record(s) from {result['files_processed']} file(s)"
        }
    except Exception as e:
        optout_service.update_request_status(request_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/opt-out/{profile_url:path}")
async def opt_out(profile_url: str):
    """
    Remove a specific record from all CSV files (opt-out request).
    Legacy endpoint for backward compatibility.
    """
    return await process_optout(profile_url)


async def process_optout(profile_url: str) -> Dict:
    """Process opt-out removal."""
    output_dir = Path(os.path.expanduser("~/Documents/social_leads"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    removed_count = 0
    files_processed = 0
    
    # Find all CSV files
    csv_files = list(output_dir.glob("*.csv"))
    
    for csv_file in csv_files:
        files_processed += 1
        try:
            # Read all rows
            rows = []
            fieldnames = None
            
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                if not fieldnames:
                    continue
                
                for row in reader:
                    # Check if this row matches the profile URL
                    row_url = row.get("Profile URL") or row.get("profile_url", "")
                    if row_url != profile_url:
                        rows.append(row)
                    else:
                        removed_count += 1
            
            # Write filtered rows back
            if fieldnames:
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                    
        except Exception as e:
            # Log error but continue
            print(f"[OPT-OUT] Error processing {csv_file}: {e}")
    
    if removed_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Profile URL not found: {profile_url}"
        )
    
    return {
        "status": "success",
        "removed_count": removed_count,
        "files_processed": files_processed,
        "message": f"Removed {removed_count} record(s) from {files_processed} file(s)"
    }


@router.get("/opt-out/requests")
async def get_optout_requests(status: Optional[str] = None):
    """Get opt-out requests (admin endpoint)."""
    if status:
        requests = optout_service.get_requests_by_status(status)
    else:
        requests = optout_service.get_requests_by_status("pending") + \
                   optout_service.get_requests_by_status("completed")
    
    return {
        "requests": requests,
        "stats": optout_service.get_stats()
    }


@router.get("/opt-out/request/{request_id}")
async def get_optout_request(request_id: int):
    """Get specific opt-out request."""
    request = optout_service.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.get("/retention/stats")
async def get_retention_stats():
    """Get data retention statistics."""
    from backend.services.retention_service import RetentionService
    
    service = RetentionService()
    stats = service.get_retention_stats()
    return stats


@router.post("/retention/cleanup")
async def run_retention_cleanup():
    """Manually trigger retention cleanup."""
    from backend.services.retention_service import RetentionService
    
    service = RetentionService()
    stats = service.cleanup_old_records()
    return {
        "status": "success",
        **stats
    }


@router.post("/data-access-request")
async def create_data_access_request(request: DataAccessRequest):
    """
    Create a GDPR data access request.
    
    Args:
        request: Data access request with email and optional profile URL
    """
    request_id = f"dar_{int(datetime.now().timestamp())}"
    estimated_completion = datetime.utcnow() + timedelta(days=30)
    
    # Create request record in database
    db = get_session()
    try:
        data_request = DataRequest(
            id=request_id,
            request_type=RequestType.ACCESS,
            status=RequestStatus.PENDING,
            email=request.email,
            profile_url=request.profile_url,
            request_data=json.dumps({
                "email": request.email,
                "profile_url": request.profile_url
            }),
            estimated_completion=estimated_completion
        )
        db.add(data_request)
        db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Failed to create data access request: {e}")
    finally:
        db.close()
    
    # In a production system, this would:
    # 1. Verify email ownership (send verification email)
    # 2. Collect all data associated with the email/profile
    # 3. Generate export file (CSV/JSON)
    # 4. Send email with download link
    
    return {
        "status": "received",
        "request_id": request_id,
        "message": "Data access request received. You will receive an email with your data export within 30 days.",
        "estimated_completion": estimated_completion.isoformat()
    }


async def delete_data_by_email(email: str) -> Dict:
    """
    Delete all data associated with an email address.
    
    Args:
        email: Email address to delete data for
        
    Returns:
        Dictionary with deletion results
    """
    db = get_session()
    removed_count = 0
    files_processed = 0
    
    try:
        # Delete from database
        leads = db.query(Lead).filter(Lead.email == email).all()
        removed_count = len(leads)
        
        for lead in leads:
            db.delete(lead)
        
        db.commit()
        
        # Also delete from CSV files
        output_dir = Path(os.path.expanduser("~/Documents/social_leads"))
        if output_dir.exists():
            csv_files = list(output_dir.glob("*.csv"))
            
            for csv_file in csv_files:
                files_processed += 1
                try:
                    rows = []
                    fieldnames = None
                    
                    with open(csv_file, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        fieldnames = reader.fieldnames
                        if not fieldnames:
                            continue
                        
                        for row in reader:
                            row_email = row.get("Email") or row.get("email", "")
                            if row_email.lower() != email.lower():
                                rows.append(row)
                            else:
                                removed_count += 1
                    
                    # Write filtered rows back
                    if fieldnames:
                        with open(csv_file, "w", newline="", encoding="utf-8") as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(rows)
                except Exception as e:
                    import logging
                    logging.error(f"Error processing CSV file {csv_file}: {e}")
        
        return {
            "removed_count": removed_count,
            "files_processed": files_processed
        }
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error deleting data by email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete data: {str(e)}")
    finally:
        db.close()


@router.post("/data-deletion-request")
async def create_data_deletion_request(request: DataDeletionRequest):
    """
    Create a GDPR data deletion request.
    
    Args:
        request: Data deletion request with email and optional profile URL
    """
    request_id = f"ddr_{int(datetime.now().timestamp())}"
    estimated_completion = datetime.utcnow() + timedelta(days=30)
    
    # Create request record in database
    db = get_session()
    try:
        data_request = DataRequest(
            id=request_id,
            request_type=RequestType.DELETION,
            status=RequestStatus.PENDING,
            email=request.email,
            profile_url=request.profile_url,
            request_data=json.dumps({
                "email": request.email,
                "profile_url": request.profile_url,
                "reason": request.reason
            }),
            estimated_completion=estimated_completion
        )
        db.add(data_request)
        db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Failed to create data deletion request: {e}")
    finally:
        db.close()
    
    # Process deletion if profile URL provided
    if request.profile_url:
        try:
            result = await process_optout(request.profile_url)
            # Update request status
            db = get_session()
            try:
                data_request = db.query(DataRequest).filter(DataRequest.id == request_id).first()
                if data_request:
                    data_request.status = RequestStatus.COMPLETED
                    data_request.completed_at = datetime.utcnow()
                    data_request.response_data = json.dumps(result)
                    db.commit()
            finally:
                db.close()
            
            return {
                "status": "success",
                "request_id": request_id,
                "removed_count": result["removed_count"],
                "message": "Data deletion request processed successfully"
            }
        except HTTPException as e:
            import logging
            logging.warning(f"Failed to process opt-out for profile URL: {e.detail}")
    
    # Process email-based deletion
    try:
        result = await delete_data_by_email(request.email)
        # Update request status
        db = get_session()
        try:
            data_request = db.query(DataRequest).filter(DataRequest.id == request_id).first()
            if data_request:
                data_request.status = RequestStatus.COMPLETED
                data_request.completed_at = datetime.utcnow()
                data_request.response_data = json.dumps(result)
                db.commit()
        finally:
            db.close()
        
        return {
            "status": "success",
            "request_id": request_id,
            "removed_count": result["removed_count"],
            "message": f"Deleted {result['removed_count']} record(s) associated with {request.email}"
        }
    except Exception as e:
        import logging
        logging.error(f"Error processing email-based deletion: {e}")
        # Return pending status if deletion fails
        return {
            "status": "received",
            "request_id": request_id,
            "message": "Data deletion request received. Your data will be deleted within 30 days.",
            "estimated_completion": estimated_completion.isoformat()
        }


@router.get("/data-requests")
async def get_data_requests(status: Optional[str] = None):
    """
    Get all data access/deletion requests (admin endpoint).
    
    Args:
        status: Optional status filter (pending, processing, completed, failed)
    """
    db = get_session()
    try:
        query = db.query(DataRequest)
        
        if status:
            try:
                status_enum = RequestStatus[status.upper()]
                query = query.filter(DataRequest.status == status_enum)
            except KeyError:
                pass  # Invalid status, return all
        
        requests = query.order_by(DataRequest.created_at.desc()).all()
        
        access_requests = [
            {
                "id": r.id,
                "email": r.email,
                "profile_url": r.profile_url,
                "status": r.status.value,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "estimated_completion": r.estimated_completion.isoformat() if r.estimated_completion else None
            }
            for r in requests if r.request_type == RequestType.ACCESS
        ]
        
        deletion_requests = [
            {
                "id": r.id,
                "email": r.email,
                "profile_url": r.profile_url,
                "status": r.status.value,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "estimated_completion": r.estimated_completion.isoformat() if r.estimated_completion else None
            }
            for r in requests if r.request_type == RequestType.DELETION
        ]
        
        return {
            "access_requests": access_requests,
            "deletion_requests": deletion_requests,
            "total": len(requests),
            "pending": len([r for r in requests if r.status == RequestStatus.PENDING]),
            "completed": len([r for r in requests if r.status == RequestStatus.COMPLETED])
        }
    finally:
        db.close()

