"""Data retention service for automatic cleanup of old records."""
import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path


class RetentionService:
    """Manages data retention and automatic cleanup."""
    
    def __init__(self, retention_days: int = 180, output_dir: str = None):
        """
        Initialize retention service.
        
        Args:
            retention_days: Number of days to retain data (default: 180 = 6 months)
            output_dir: Directory containing CSV files (default: ~/Documents/social_leads)
        """
        self.retention_days = retention_days
        if output_dir is None:
            output_dir = os.path.expanduser("~/Documents/social_leads")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def cleanup_old_records(self) -> Dict[str, int]:
        """
        Remove records older than retention period.
        
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            "files_processed": 0,
            "records_before": 0,
            "records_after": 0,
            "records_deleted": 0,
        }
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        # Find all CSV files in output directory
        csv_files = list(self.output_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            stats["files_processed"] += 1
            try:
                # Read all rows
                rows = []
                fieldnames = None
                
                if not csv_file.exists():
                    continue
                
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    if not fieldnames:
                        continue
                    
                    for row in reader:
                        stats["records_before"] += 1
                        
                        # Check if record has timestamp
                        extracted_at = row.get("extracted_at") or row.get("Extracted At")
                        if extracted_at and extracted_at != "N/A":
                            try:
                                # Parse timestamp
                                if isinstance(extracted_at, str):
                                    # Try different formats
                                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                        try:
                                            record_date = datetime.strptime(extracted_at.split(".")[0], fmt)
                                            break
                                        except ValueError:
                                            continue
                                    else:
                                        # If no format matches, keep the record
                                        rows.append(row)
                                        stats["records_after"] += 1
                                        continue
                                else:
                                    record_date = extracted_at
                                
                                # Keep if within retention period
                                if record_date >= cutoff_date:
                                    rows.append(row)
                                    stats["records_after"] += 1
                                else:
                                    stats["records_deleted"] += 1
                            except Exception:
                                # If parsing fails, keep the record to be safe
                                rows.append(row)
                                stats["records_after"] += 1
                        else:
                            # No timestamp, keep the record
                            rows.append(row)
                            stats["records_after"] += 1
                
                # Write filtered rows back
                if fieldnames and rows:
                    with open(csv_file, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)
                elif not rows:
                    # File is empty, delete it
                    csv_file.unlink()
                    
            except Exception as e:
                # Log error but continue with other files
                logging.info(f"[RETENTION] Error processing {csv_file}: {e}")
        
        return stats
    
    def get_retention_stats(self) -> Dict[str, any]:
        """Get statistics about data retention."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        total_records = 0
        records_to_delete = 0
        oldest_record = None
        
        csv_files = list(self.output_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_records += 1
                        
                        extracted_at = row.get("extracted_at") or row.get("Extracted At")
                        if extracted_at and extracted_at != "N/A":
                            try:
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        record_date = datetime.strptime(extracted_at.split(".")[0], fmt)
                                        break
                                    except ValueError:
                                        continue
                                else:
                                    continue
                                
                                if oldest_record is None or record_date < oldest_record:
                                    oldest_record = record_date
                                
                                if record_date < cutoff_date:
                                    records_to_delete += 1
                            except Exception as e:
                                import logging
                                logging.debug(f"Error parsing record date in retention service: {e}")
            except Exception as e:
                import logging
                logging.debug(f"Error processing CSV file in retention service: {e}")
        
        return {
            "retention_days": self.retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "total_records": total_records,
            "records_to_delete": records_to_delete,
            "oldest_record": oldest_record.isoformat() if oldest_record else None,
        }


def run_retention_cleanup(retention_days: int = 180) -> Dict[str, int]:
    """
    Convenience function to run retention cleanup.
    
    Args:
        retention_days: Number of days to retain data
        
    Returns:
        Cleanup statistics
    """
    service = RetentionService(retention_days=retention_days)
    return service.cleanup_old_records()

