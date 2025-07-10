from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from models import User, Job, Lead
from database import get_db
from auth import get_current_user
from datetime import datetime
import csv
import io
import json
import xlsxwriter
# PDF export can be added with reportlab or similar if needed

router = APIRouter(prefix="/api/export", tags=["export"])

class ExportFormat(str):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
    PDF = "pdf"

@router.get("/analytics", summary="Export analytics data", response_description="Export analytics in various formats")
def export_analytics(
    format: ExportFormat = Query("csv", description="Export format: csv, json, xlsx, pdf"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Export analytics data in CSV, JSON, XLSX, or PDF format."""
    # Generate analytics data
    total_jobs = db.query(Job).filter(Job.user_id == user.id).count()
    completed_jobs = db.query(Job).filter(Job.user_id == user.id, Job.status == 'completed').count()
    failed_jobs = db.query(Job).filter(Job.user_id == user.id, Job.status == 'failed').count()
    total_leads = db.query(Lead).filter(Lead.user_id == user.id).count()
    new_leads = db.query(Lead).filter(Lead.user_id == user.id, Lead.status == 'new').count()
    converted_leads = db.query(Lead).filter(Lead.user_id == user.id, Lead.status == 'converted').count()
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
        response = Response(content=json.dumps(analytics_data, indent=2), media_type="application/json")
        response.headers["Content-Disposition"] = "attachment; filename=analytics.json"
        return response
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