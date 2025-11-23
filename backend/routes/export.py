"""Export endpoints for multiple formats."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse, Response
from starlette.background import BackgroundTask
from typing import Optional, List
import os
import csv
import json
import tempfile
from datetime import datetime
from pathlib import Path
import io

router = APIRouter(prefix="/api/export", tags=["export"])


def _read_and_filter_csv(
    source_csv: Path,
    task_id: Optional[str] = None,
    platform: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> tuple[List[dict], List[str]]:
    """Read CSV and apply filters."""
    filtered_rows = []
    fieldnames = None
    
    try:
        with open(source_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            for row in reader:
                # Filter by task_id
                if task_id:
                    row_task_id = row.get("task_id") or row.get("Task ID")
                    if row_task_id != task_id:
                        continue
                
                # Filter by date range
                if date_from or date_to:
                    extracted_at = row.get("extracted_at") or row.get("Extracted At", "")
                    if extracted_at and extracted_at != "N/A":
                        try:
                            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                try:
                                    row_date = datetime.strptime(extracted_at.split(".")[0], fmt).date()
                                    break
                                except ValueError:
                                    continue
                            else:
                                filtered_rows.append(row)
                                continue
                            
                            if date_from:
                                from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                                if row_date < from_date:
                                    continue
                            
                            if date_to:
                                to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
                                if row_date > to_date:
                                    continue
                        except Exception:
                            pass
                
                filtered_rows.append(row)
    except HTTPException:
        raise
    except Exception as e:
        # Return 404 instead of 500 for file reading errors (file might be corrupted)
        raise HTTPException(status_code=404, detail=f"CSV file not found or unreadable: {str(e)}")
    
    return filtered_rows, fieldnames or []


@router.get("/{format}")
async def export_data(
    format: str,
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Export scraped data in multiple formats (CSV, JSON, Excel) with optional filters.
    
    Supports:
    - Task-specific export (filter by task_id)
    - Platform-specific export
    - Date range export
    - Formats: csv, json, excel
    """
    try:
        # Determine format from path or query
        if format is None:
            # Try to get from path
            format = "csv"  # default
        
        format = format.lower()
        if format not in ["csv", "json", "excel"]:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Use csv, json, or excel")
        
        output_dir = Path(os.path.expanduser("~/Documents/social_leads"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine source CSV
        if platform:
            source_csv = output_dir / f"{platform}.csv"
        else:
            source_csv = output_dir / "all_platforms.csv"
        
        if not source_csv.exists():
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        # Apply filters
        try:
            filtered_rows, fieldnames = _read_and_filter_csv(
                source_csv, task_id, platform, date_from, date_to
            )
        except HTTPException:
            raise
        except Exception as e:
            # If CSV reading fails, return 404 (file might be corrupted or empty)
            raise HTTPException(status_code=404, detail=f"CSV file not found or unreadable: {str(e)}")
        
        # Check if we have valid data
        if not filtered_rows:
            raise HTTPException(status_code=404, detail="No data found matching the specified filters")
        
        # Ensure fieldnames are valid (remove None values)
        if not fieldnames or all(f is None for f in fieldnames):
            # Try to get fieldnames from first row
            if filtered_rows:
                fieldnames = list(filtered_rows[0].keys())
            else:
                raise HTTPException(status_code=404, detail="CSV file has no valid columns")
        
        # Filter out None from fieldnames
        fieldnames = [f for f in fieldnames if f is not None]
        if not fieldnames:
            raise HTTPException(status_code=404, detail="CSV file has no valid columns")
        
        # Generate filename
        filename_parts = [source_csv.stem]
        if task_id:
            filename_parts.append(f"task_{task_id[:8]}")
        if date_from:
            filename_parts.append(f"from_{date_from}")
        if date_to:
            filename_parts.append(f"to_{date_to}")
        
        # Handle each format
        if format == "csv":
            # Create temporary CSV file
            temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8")
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                with open(temp_path, "w", newline="", encoding="utf-8") as f:
                    # Filter rows to only include valid fieldnames
                    cleaned_rows = []
                    for row in filtered_rows:
                        cleaned_row = {k: v for k, v in row.items() if k in fieldnames}
                        cleaned_rows.append(cleaned_row)
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(cleaned_rows)
                
                filename = "_".join(filename_parts) + ".csv"
                
                return FileResponse(
                    temp_path,
                    media_type="text/csv",
                    filename=filename,
                    background=BackgroundTask(os.unlink, temp_path)
                )
            except Exception as e:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise HTTPException(status_code=500, detail=f"Error creating CSV: {str(e)}")
        
        elif format == "json":
            filename = "_".join(filename_parts) + ".json"
            json_content = json.dumps(filtered_rows, indent=2, ensure_ascii=False)
            
            return Response(
                content=json_content,
                media_type="application/json",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
        
        elif format == "excel":
            try:
                import openpyxl
                from openpyxl import Workbook
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="openpyxl not installed. Install with: pip install openpyxl"
                )
            
            # Create Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Leads"
            
            # Write headers
            if fieldnames:
                ws.append(fieldnames)
            
            # Write data
            for row in filtered_rows:
                ws.append([row.get(field, "") for field in fieldnames])
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                wb.save(temp_path)
                filename = "_".join(filename_parts) + ".xlsx"
                
                return FileResponse(
                    temp_path,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    filename=filename,
                    background=BackgroundTask(os.unlink, temp_path)
                )
            except Exception as e:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise HTTPException(status_code=500, detail=f"Error creating Excel file: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        # Catch any other unexpected errors and return 500
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

