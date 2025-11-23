"""Migration script to migrate CSV data to PostgreSQL."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import csv
from datetime import datetime
from typing import Dict
from backend.services.postgresql_storage import get_postgresql_storage
from backend.models.database import init_db


def migrate_csv_file(csv_path: Path, task_id: str = None) -> int:
    """
    Migrate a single CSV file to PostgreSQL.
    
    Args:
        csv_path: Path to CSV file
        task_id: Optional task ID (extracted from filename if not provided)
        
    Returns:
        Number of records migrated
    """
    storage = get_postgresql_storage()
    count = 0
    
    if not csv_path.exists():
        print(f"[MIGRATE] File not found: {csv_path}")
        return 0
    
    # Extract task_id from filename if not provided
    if not task_id:
        # Format: leads_{task_id}.csv
        filename = csv_path.stem
        if filename.startswith("leads_"):
            task_id = filename.replace("leads_", "")
        else:
            task_id = "migrated"
    
    print(f"[MIGRATE] Migrating {csv_path} (task_id: {task_id})...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Convert CSV row to result dictionary
                result = {
                    "search_query": row.get("Search Query", ""),
                    "platform": row.get("Platform", ""),
                    "profile_url": row.get("Profile URL", ""),
                    "handle": row.get("Handle", ""),
                    "display_name": row.get("Display Name", ""),
                    "bio_about": row.get("Bio/About", ""),
                    "website": row.get("Website", ""),
                    "email": row.get("Email", ""),
                    "phone": row.get("Phone", ""),
                    "followers": row.get("Followers", ""),
                    "location": row.get("Location", ""),
                    "field_of_study": row.get("Field of Study", ""),
                    "institution_name": row.get("Institution", ""),
                    "business_type": row.get("Business Type", ""),
                    "industry": row.get("Industry", ""),
                    "city": row.get("City", ""),
                    "region": row.get("Region", ""),
                    "country": row.get("Country", ""),
                    "job_title": row.get("Job Title", ""),
                    "seniority_level": row.get("Seniority Level", ""),
                    "education_level": row.get("Education Level", ""),
                    "lead_type": row.get("Lead Type", ""),
                    "degree_program": row.get("Degree Program", ""),
                    "graduation_year": int(row.get("Graduation Year", 0)) if row.get("Graduation Year") else None,
                }
                
                # Save to PostgreSQL
                if storage.save_lead(task_id, result):
                    count += 1
                
                if count % 100 == 0:
                    print(f"[MIGRATE] Migrated {count} records...")
        
        print(f"[MIGRATE] Completed: {count} records migrated from {csv_path}")
        return count
    except Exception as e:
        print(f"[MIGRATE] Error migrating {csv_path}: {e}")
        return count


def migrate_all_csv_files(data_dir: Path = Path("data")) -> Dict[str, int]:
    """
    Migrate all CSV files in data directory.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary mapping filenames to record counts
    """
    print(f"[MIGRATE] Starting migration from {data_dir}...")
    
    # Initialize database
    init_db()
    
    results = {}
    csv_files = list(data_dir.glob("leads_*.csv"))
    
    if not csv_files:
        print(f"[MIGRATE] No CSV files found in {data_dir}")
        return results
    
    print(f"[MIGRATE] Found {len(csv_files)} CSV files to migrate")
    
    total_count = 0
    for csv_file in csv_files:
        count = migrate_csv_file(csv_file)
        results[csv_file.name] = count
        total_count += count
    
    print(f"[MIGRATE] Migration complete! Total records: {total_count}")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate CSV data to PostgreSQL")
    parser.add_argument("--file", type=str, help="Specific CSV file to migrate")
    parser.add_argument("--task-id", type=str, help="Task ID for the migration")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")
    
    args = parser.parse_args()
    
    if args.file:
        # Migrate single file
        csv_path = Path(args.file)
        migrate_csv_file(csv_path, args.task_id)
    else:
        # Migrate all files
        data_dir = Path(args.data_dir)
        migrate_all_csv_files(data_dir)

