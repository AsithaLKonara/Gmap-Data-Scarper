"""Consent management service."""
import os
import json
import sqlite3
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path


class ConsentService:
    """Manages user consent tracking."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize consent service.
        
        Args:
            db_path: Path to SQLite database (default: ~/.gmap_scraper/consent.db)
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.expanduser("~"),
                ".gmap_scraper",
                "consent.db"
            )
        
        self.db_path = db_path
        Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize consent database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                consent_given BOOLEAN,
                consent_timestamp TEXT,
                ip_address TEXT,
                user_agent TEXT,
                consent_version TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                withdrawal_timestamp TEXT,
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_consent(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        consent_version: str = "1.0"
    ) -> bool:
        """
        Record user consent.
        
        Args:
            user_id: User identifier (optional)
            ip_address: IP address
            user_agent: User agent string
            consent_version: Version of consent policy
            
        Returns:
            True if recorded successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO consent (user_id, consent_given, consent_timestamp, ip_address, user_agent, consent_version)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                True,
                datetime.now().isoformat(),
                ip_address,
                user_agent,
                consent_version
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def record_withdrawal(
        self,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Record consent withdrawal.
        
        Args:
            user_id: User identifier (optional)
            reason: Reason for withdrawal
            
        Returns:
            True if recorded successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO consent_withdrawals (user_id, withdrawal_timestamp, reason)
                VALUES (?, ?, ?)
            """, (
                user_id,
                datetime.now().isoformat(),
                reason
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def has_consent(self, user_id: Optional[str] = None) -> bool:
        """
        Check if user has given consent.
        
        Args:
            user_id: User identifier (optional)
            
        Returns:
            True if consent exists
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM consent
                    WHERE user_id = ? AND consent_given = 1
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM consent
                    WHERE consent_given = 1
                    ORDER BY consent_timestamp DESC
                    LIMIT 1
                """)
            
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False
    
    def get_consent_stats(self) -> Dict:
        """Get consent statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM consent WHERE consent_given = 1")
            total_consents = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM consent_withdrawals")
            total_withdrawals = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT consent_timestamp FROM consent
                WHERE consent_given = 1
                ORDER BY consent_timestamp DESC
                LIMIT 1
            """)
            latest_consent = cursor.fetchone()
            latest_consent_time = latest_consent[0] if latest_consent else None
            
            conn.close()
            
            return {
                "total_consents": total_consents,
                "total_withdrawals": total_withdrawals,
                "latest_consent": latest_consent_time,
            }
        except Exception:
            return {
                "total_consents": 0,
                "total_withdrawals": 0,
                "latest_consent": None,
            }


# Global consent service instance
consent_service = ConsentService()

