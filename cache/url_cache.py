"""SQLite-based URL cache for avoiding duplicate scrapes."""
from __future__ import annotations

import sqlite3
import os
from typing import Optional, Set
from datetime import datetime, timedelta


class URLCache:
    """
    SQLite-based cache for storing scraped URLs.
    
    Prevents re-scraping URLs that have been processed recently.
    """
    
    def __init__(self, db_path: str = "cache/url_cache.db", ttl_days: int = 30):
        """
        Initialize URL cache.
        
        Args:
            db_path: Path to SQLite database
            ttl_days: Time-to-live in days (URLs older than this are expired)
        """
        self.db_path = db_path
        self.ttl_days = ttl_days
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS url_cache (
                url TEXT PRIMARY KEY,
                platform TEXT,
                scraped_at TIMESTAMP,
                data_hash TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scraped_at ON url_cache(scraped_at)
        """)
        
        conn.commit()
        conn.close()
    
    def is_cached(self, url: str) -> bool:
        """
        Check if URL is cached and not expired.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is cached and not expired
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scraped_at FROM url_cache
            WHERE url = ?
        """, (url,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        scraped_at = datetime.fromisoformat(result[0])
        expiry_date = datetime.now() - timedelta(days=self.ttl_days)
        
        return scraped_at > expiry_date
    
    def add(self, url: str, platform: str, data_hash: Optional[str] = None) -> None:
        """
        Add URL to cache.
        
        Args:
            url: URL to cache
            platform: Platform name
            data_hash: Optional hash of scraped data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO url_cache (url, platform, scraped_at, data_hash)
            VALUES (?, ?, ?, ?)
        """, (url, platform, datetime.now().isoformat(), data_hash))
        
        conn.commit()
        conn.close()
    
    def get_cached_urls(self, platform: Optional[str] = None) -> Set[str]:
        """
        Get all cached URLs (optionally filtered by platform).
        
        Args:
            platform: Optional platform filter
            
        Returns:
            Set of cached URLs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if platform:
            cursor.execute("""
                SELECT url FROM url_cache WHERE platform = ?
            """, (platform,))
        else:
            cursor.execute("SELECT url FROM url_cache")
        
        urls = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        return urls
    
    def clear_expired(self) -> int:
        """
        Clear expired entries from cache.
        
        Returns:
            Number of entries cleared
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expiry_date = datetime.now() - timedelta(days=self.ttl_days)
        
        cursor.execute("""
            DELETE FROM url_cache
            WHERE scraped_at < ?
        """, (expiry_date.isoformat(),))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def clear_all(self) -> None:
        """Clear all entries from cache."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM url_cache")
        
        conn.commit()
        conn.close()

