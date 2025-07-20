from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from models import Users, Jobs, Leads
from database import get_db
from auth import get_current_user
from datetime import datetime
from audit import audit_log
from security import check_permission

import csv
import io
import json
import xlsxwriter
import enum
# PDF export can be added with reportlab or similar if needed

router = APIRouter(prefix="/api/export", tags=["export"])

class ExportFormat(str, enum.Enum):
    """Supported export formats for analytics data."""
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
    PDF = "pdf"

class JobStatistics(BaseModel):
    total_jobs: int = Field(..., description="Total number of jobs", example=42)
    completed_jobs: int = Field(..., description="Number of completed jobs", example=35)
    failed_jobs: int = Field(..., description="Number of failed jobs", example=2)
    success_rate: float = Field(..., description="Success rate as a percentage", example=83.3)

class LeadStatistics(BaseModel):
    total_leads: int = Field(..., description="Total number of leads", example=100)
    new_leads: int = Field(..., description="Number of new leads", example=20)
    converted_leads: int = Field(..., description="Number of converted leads", example=10)
    conversion_rate: float = Field(..., description="Conversion rate as a percentage", example=10.0)

class AnalyticsExportOut(BaseModel):
    job_statistics: JobStatistics = Field(..., description="Job statistics for the user")
    lead_statistics: LeadStatistics = Field(..., description="Lead statistics for the user")
    export_date: str = Field(..., description="UTC ISO export date", example="2024-05-01T12:00:00Z")
    user_id: int = Field(..., description="User ID", example=1)

@router.get(
    "/analytics",
    summary="Export analytics data",
    description="Export analytics data in CSV, JSON, XLSX, or PDF format. Returns a file download for CSV/XLSX/PDF, or a JSON object for JSON format.",
    response_model=AnalyticsExportOut,
    response_description="Analytics data as JSON (if format=json)"
)
@audit_log(action="export_analytics", target_type="user")
def export_analytics(
    format: ExportFormat = Query("csv", description="Export format: csv, json, xlsx, pdf"),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Export analytics data in CSV, JSON, XLSX, or PDF format."""
    # Generate analytics data
    total_jobs = db.query(Jobs).filter(Jobs.user_id == user.id).count()
    completed_jobs = db.query(Jobs).filter(Jobs.user_id == user.id, Jobs.status == 'completed').count()
    failed_jobs = db.query(Jobs).filter(Jobs.user_id == user.id, Jobs.status == 'failed').count()
    total_leads = db.query(Leads).filter(Leads.user_id == user.id).count()
    new_leads = db.query(Leads).filter(Leads.user_id == user.id, Leads.status == 'new').count()
    converted_leads = db.query(Leads).filter(Leads.user_id == user.id, Leads.status == 'converted').count()
    analytics_data = {
        'job_statistics': {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        },
        'lead_statistics': {
            'total_leads': total_leads,
            'new_leads': new_leads,
            'converted_leads': converted_leads,
            'conversion_rate': (converted_leads / total_leads * 100) if total_leads > 0 else 0
        },
        'export_date': datetime.utcnow().isoformat(),
        'user_id': user.id
    }
    if format == ExportFormat.CSV:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        for section, stats in analytics_data.items():
            if isinstance(stats, dict):
                for k, v in stats.items():
                    writer.writerow([f"{section}.{k}", v])
            else:
                writer.writerow([section, stats])
        response = Response(content=output.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=analytics.csv"
        return response
    elif format == ExportFormat.JSON:
        # Validate with response model
        return AnalyticsExportOut(**analytics_data)
    elif format == ExportFormat.XLSX:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Metric")
        worksheet.write(0, 1, "Value")
        row = 1
        for section, stats in analytics_data.items():
            if isinstance(stats, dict):
                for k, v in stats.items():
                    worksheet.write(row, 0, f"{section}.{k}")
                    worksheet.write(row, 1, v)
                    row += 1
            else:
                worksheet.write(row, 0, section)
                worksheet.write(row, 1, stats)
                row += 1
        workbook.close()
        response = Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = "attachment; filename=analytics.xlsx"
        return response
    elif format == ExportFormat.PDF:
        # PDF export can be implemented with reportlab or similar
        return Response(content="PDF export not implemented yet", media_type="text/plain")
    else:
        raise HTTPException(status_code=400, detail="Invalid export format") 