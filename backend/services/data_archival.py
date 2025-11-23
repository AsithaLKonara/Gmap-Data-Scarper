"""Data archival service for managing old records and cold storage."""
import os
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
import csv
import json
from backend.services.postgresql_cache import get_postgresql_cache


class DataArchivalService:
    """Manages data archival to cold storage with table partitioning."""
    
    def __init__(
        self,
        archive_dir: Optional[str] = None,
        retention_days: int = 180,  # 6 months
        partition_by_days: int = 30  # Monthly partitions
    ):
        """
        Initialize data archival service.
        
        Args:
            archive_dir: Directory for archived data (or from env ARCHIVE_DIR)
            retention_days: Days before archiving (default 180)
            partition_by_days: Days per partition (default 30)
        """
        self.archive_dir = Path(archive_dir or os.getenv("ARCHIVE_DIR", "~/Documents/archived_leads"))
        self.archive_dir = Path(os.path.expanduser(self.archive_dir))
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        self.retention_days = retention_days
        self.partition_by_days = partition_by_days
    
    def archive_old_records(
        self,
        cutoff_date: Optional[datetime] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Archive old records to cold storage.
        
        Args:
            cutoff_date: Date before which to archive (default: retention_days ago)
            platform: Specific platform to archive (None = all)
        
        Returns:
            Dict with archival statistics
        """
        if cutoff_date is None:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        stats = {
            "archived_count": 0,
            "archived_files": [],
            "errors": [],
            "cutoff_date": cutoff_date.isoformat()
        }
        
        # Archive CSV files
        output_dir = Path(os.path.expanduser("~/Documents/social_leads"))
        if not output_dir.exists():
            return stats
        
        csv_files = list(output_dir.glob("*.csv"))
        if platform:
            csv_files = [f for f in csv_files if platform in f.name]
        
        for csv_file in csv_files:
            try:
                archived = self._archive_csv_file(csv_file, cutoff_date)
                if archived:
                    stats["archived_count"] += archived["count"]
                    stats["archived_files"].append(archived["archive_path"])
            except Exception as e:
                stats["errors"].append(f"Error archiving {csv_file.name}: {str(e)}")
        
        # Archive PostgreSQL cache if available
        postgres_cache = get_postgresql_cache()
        if postgres_cache:
            try:
                deleted = postgres_cache.cleanup_old_records(days=self.retention_days)
                stats["postgres_cache_cleaned"] = deleted
            except Exception as e:
                stats["errors"].append(f"Error cleaning PostgreSQL cache: {str(e)}")
        
        return stats
    
    def _archive_csv_file(
        self,
        csv_file: Path,
        cutoff_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Archive a CSV file, moving old records to partitioned archive."""
        # Determine partition (monthly)
        partition_date = cutoff_date.replace(day=1)  # Start of month
        partition_name = partition_date.strftime("%Y-%m")
        
        # Create partition directory
        partition_dir = self.archive_dir / partition_name
        partition_dir.mkdir(parents=True, exist_ok=True)
        
        # Read and filter CSV
        old_records = []
        new_records = []
        fieldnames = None
        
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            for row in reader:
                # Check extracted_at date
                extracted_at = row.get("extracted_at") or row.get("Extracted At", "")
                if extracted_at and extracted_at != "N/A":
                    try:
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                            try:
                                record_date = datetime.strptime(extracted_at.split(".")[0], fmt)
                                if record_date < cutoff_date:
                                    old_records.append(row)
                                else:
                                    new_records.append(row)
                                break
                            except ValueError:
                                continue
                        else:
                            # Could not parse date, keep in new records
                            new_records.append(row)
                    except Exception:
                        new_records.append(row)
                else:
                    # No date, keep in new records
                    new_records.append(row)
        
        if not old_records:
            return None  # Nothing to archive
        
        # Write archived records to partition file
        archive_file = partition_dir / f"{csv_file.stem}_{partition_name}.csv"
        archive_exists = archive_file.exists()
        
        with open(archive_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not archive_exists:
                writer.writeheader()
            writer.writerows(old_records)
        
        # Write new records back to original file
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_records)
        
        return {
            "count": len(old_records),
            "archive_path": str(archive_file),
            "partition": partition_name
        }
    
    def restore_from_archive(
        self,
        partition: str,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore records from archive partition.
        
        Args:
            partition: Partition name (e.g., "2024-01")
            platform: Specific platform to restore (None = all)
        
        Returns:
            Dict with restoration statistics
        """
        partition_dir = self.archive_dir / partition
        if not partition_dir.exists():
            return {"error": f"Partition {partition} not found", "restored_count": 0}
        
        stats = {
            "restored_count": 0,
            "restored_files": [],
            "errors": []
        }
        
        archive_files = list(partition_dir.glob("*.csv"))
        if platform:
            archive_files = [f for f in archive_files if platform in f.name]
        
        output_dir = Path(os.path.expanduser("~/Documents/social_leads"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for archive_file in archive_files:
            try:
                # Determine target file
                original_name = archive_file.stem.split("_")[0] + ".csv"
                target_file = output_dir / original_name
                
                # Read archived records
                with open(archive_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    records = list(reader)
                    fieldnames = reader.fieldnames or []
                
                # Append to target file
                file_exists = target_file.exists()
                with open(target_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    if not file_exists:
                        writer.writeheader()
                    writer.writerows(records)
                
                stats["restored_count"] += len(records)
                stats["restored_files"].append(str(target_file))
            except Exception as e:
                stats["errors"].append(f"Error restoring {archive_file.name}: {str(e)}")
        
        return stats
    
    def list_archives(self) -> List[Dict[str, Any]]:
        """List available archive partitions."""
        archives = []
        
        for partition_dir in sorted(self.archive_dir.iterdir()):
            if partition_dir.is_dir():
                archive_files = list(partition_dir.glob("*.csv"))
                total_records = 0
                
                for archive_file in archive_files:
                    try:
                        with open(archive_file, "r", encoding="utf-8") as f:
                            reader = csv.DictReader(f)
                            total_records += sum(1 for _ in reader)
                    except Exception as e:
                        import logging
                        logging.debug(f"Error reading archive file {archive_file}: {e}")
                
                archives.append({
                    "partition": partition_dir.name,
                    "file_count": len(archive_files),
                    "total_records": total_records,
                    "path": str(partition_dir)
                })
        
        return archives
    
    def get_archive_stats(self) -> Dict[str, Any]:
        """Get overall archive statistics."""
        archives = self.list_archives()
        
        total_records = sum(a["total_records"] for a in archives)
        total_files = sum(a["file_count"] for a in archives)
        
        return {
            "total_partitions": len(archives),
            "total_archived_records": total_records,
            "total_archived_files": total_files,
            "partitions": archives,
            "archive_directory": str(self.archive_dir)
        }


# Global instance
_data_archival_service = None

def get_data_archival_service() -> DataArchivalService:
    """Get or create global data archival service instance."""
    global _data_archival_service
    if _data_archival_service is None:
        _data_archival_service = DataArchivalService()
    return _data_archival_service

