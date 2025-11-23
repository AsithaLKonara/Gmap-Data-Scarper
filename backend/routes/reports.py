"""Report builder and scheduled reports endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from backend.middleware.auth import get_current_user
from backend.services.report_builder import report_builder_service
from backend.services.scheduled_report_service import scheduled_report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportConfigRequest(BaseModel):
    """Request model for building a report."""
    report_config: Dict[str, Any]


class ScheduleRequest(BaseModel):
    """Request model for scheduling a report."""
    frequency: str  # daily, weekly, monthly
    day: Optional[int] = None  # Day of week (0-6) or day of month (1-31)
    time: str = "09:00"  # HH:MM format


class ScheduledReportCreate(BaseModel):
    """Request model for creating a scheduled report."""
    name: str
    report_config: Dict[str, Any]
    schedule: ScheduleRequest
    delivery_method: str = "email"
    delivery_config: Optional[Dict[str, Any]] = None
    format: str = "json"
    team_id: Optional[str] = None


@router.post("/build", response_model=Dict[str, Any])
async def build_report(
    request: ReportConfigRequest,
    current_user: dict = Depends(get_current_user)
):
    """Build a custom report."""
    try:
        user_id = current_user["user_id"]
        report_data = report_builder_service.build_report(
            user_id=user_id,
            report_config=request.report_config
        )
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build report: {str(e)}")


@router.post("/export", response_model=Dict[str, Any])
async def export_report(
    report_data: Dict[str, Any],
    format: str = Query("json", pattern="^(json|csv|pdf)$"),
    current_user: dict = Depends(get_current_user)
):
    """Export report in specified format."""
    try:
        report_bytes = report_builder_service.export_report(
            report_data=report_data,
            format=format
        )
        
        from fastapi.responses import Response
        return Response(
            content=report_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=report.{format}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")


@router.post("/scheduled", response_model=Dict[str, Any])
async def create_scheduled_report(
    request: ScheduledReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a scheduled report."""
    try:
        user_id = current_user["user_id"]
        schedule_dict = {
            "frequency": request.schedule.frequency,
            "day": request.schedule.day,
            "time": request.schedule.time
        }
        
        report = scheduled_report_service.create_scheduled_report(
            user_id=user_id,
            name=request.name,
            report_config=request.report_config,
            schedule=schedule_dict,
            delivery_method=request.delivery_method,
            delivery_config=request.delivery_config,
            format=request.format,
            team_id=request.team_id
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create scheduled report: {str(e)}")


@router.get("/scheduled", response_model=List[Dict[str, Any]])
async def list_scheduled_reports(
    current_user: dict = Depends(get_current_user)
):
    """List all scheduled reports for user."""
    try:
        from backend.models.database import get_session
        from backend.models.scheduled_report import ScheduledReport
        
        user_id = current_user["user_id"]
        db = get_session()
        try:
            reports = db.query(ScheduledReport).filter(
                ScheduledReport.user_id == user_id
            ).all()
            return [r.to_dict() for r in reports]
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.delete("/scheduled/{report_id}", response_model=Dict[str, str])
async def delete_scheduled_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a scheduled report."""
    try:
        from backend.models.database import get_session
        from backend.models.scheduled_report import ScheduledReport
        
        user_id = current_user["user_id"]
        db = get_session()
        try:
            report = db.query(ScheduledReport).filter(
                ScheduledReport.report_id == report_id,
                ScheduledReport.user_id == user_id
            ).first()
            
            if not report:
                raise HTTPException(status_code=404, detail="Report not found")
            
            report.is_active = False
            db.commit()
            
            return {"status": "deleted", "report_id": report_id}
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

