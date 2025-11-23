"""Data archival endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, Dict, Any
from backend.services.archival import get_archival_service
from backend.middleware.auth import get_optional_user

router = APIRouter(prefix="/api/archival", tags=["archival"])


@router.get("/stats")
async def get_archival_stats(
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get statistics about data eligible for archival."""
    try:
        archival_service = get_archival_service()
        stats = archival_service.get_archival_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get archival stats: {str(e)}")


@router.post("/archive")
async def archive_old_data(
    dry_run: bool = Query(False, description="If true, only report what would be archived"),
    batch_size: int = Query(1000, ge=100, le=10000, description="Batch size for archival"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Archive leads older than retention period."""
    try:
        archival_service = get_archival_service()
        result = archival_service.archive_old_leads(
            dry_run=dry_run,
            batch_size=batch_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Archival failed: {str(e)}")


@router.post("/restore")
async def restore_from_archive(
    archive_file: str = Body(..., description="Path to archive JSON file"),
    dry_run: bool = Body(False, description="If true, only report what would be restored"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Restore leads from archive file."""
    try:
        archival_service = get_archival_service()
        result = archival_service.restore_from_archive(
            archive_file=archive_file,
            dry_run=dry_run
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restoration failed: {str(e)}")
