"""Enhanced opt-out request service with tracking."""
import os
import sqlite3
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path


class OptOutService:
    """Manages opt-out requests with tracking."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize opt-out service.
        
        Args:
            db_path: Path to SQLite database (default: ~/.gmap_scraper/optout.db)
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.expanduser("~"),
                ".gmap_scraper",
                "optout.db"
            )
        
        self.db_path = db_path
        Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize opt-out database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optout_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT NOT NULL,
                email TEXT,
                request_timestamp TEXT,
                status TEXT DEFAULT 'pending',
                processed_timestamp TEXT,
                removed_count INTEGER DEFAULT 0,
                files_processed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_profile_url ON optout_requests(profile_url)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON optout_requests(status)
        """)
        
        conn.commit()
        conn.close()
    
    def create_request(
        self,
        profile_url: str,
        email: Optional[str] = None
    ) -> int:
        """
        Create an opt-out request.
        
        Args:
            profile_url: Profile URL to remove
            email: Optional email for confirmation
            
        Returns:
            Request ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO optout_requests (profile_url, email, request_timestamp, status)
            VALUES (?, ?, ?, 'pending')
        """, (
            profile_url,
            email,
            datetime.now().isoformat()
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def update_request_status(
        self,
        request_id: int,
        status: str,
        removed_count: int = 0,
        files_processed: int = 0
    ):
        """
        Update opt-out request status.
        
        Args:
            request_id: Request ID
            status: New status (pending, processing, completed, failed)
            removed_count: Number of records removed
            files_processed: Number of files processed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE optout_requests
            SET status = ?, processed_timestamp = ?, removed_count = ?, files_processed = ?
            WHERE id = ?
        """, (
            status,
            datetime.now().isoformat(),
            removed_count,
            files_processed,
            request_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_request(self, request_id: int) -> Optional[Dict]:
        """Get opt-out request by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM optout_requests WHERE id = ?
        """, (request_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "profile_url": row[1],
            "email": row[2],
            "request_timestamp": row[3],
            "status": row[4],
            "processed_timestamp": row[5],
            "removed_count": row[6],
            "files_processed": row[7],
            "created_at": row[8],
        }
    
    def get_requests_by_status(self, status: str) -> List[Dict]:
        """Get all requests by status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM optout_requests WHERE status = ? ORDER BY created_at DESC
        """, (status,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "profile_url": row[1],
                "email": row[2],
                "request_timestamp": row[3],
                "status": row[4],
                "processed_timestamp": row[5],
                "removed_count": row[6],
                "files_processed": row[7],
                "created_at": row[8],
            }
            for row in rows
        ]
    
    def get_stats(self) -> Dict:
        """Get opt-out request statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM optout_requests")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM optout_requests WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM optout_requests WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_requests": total,
            "completed": completed,
            "pending": pending,
        }


# Global opt-out service instance
optout_service = OptOutService()

