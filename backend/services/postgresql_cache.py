"""PostgreSQL-based URL cache with connection pooling."""
import os
from typing import Optional, Set
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


class PostgreSQLCache:
    """PostgreSQL-based URL cache with connection pooling."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        min_connections: int = 2,
        max_connections: int = 10
    ):
        """
        Initialize PostgreSQL cache.
        
        Args:
            database_url: PostgreSQL connection URL (or from env DATABASE_URL)
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        
        if self.database_url:
            self._initialize_pool()
            self._create_tables()
    
    def _initialize_pool(self):
        """Initialize connection pool."""
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                self.database_url
            )
        except Exception as e:
            print(f"Failed to initialize PostgreSQL pool: {e}")
            self.connection_pool = None
    
    def _create_tables(self):
        """Create cache tables if they don't exist."""
        if not self.connection_pool:
            return
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS url_cache (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL UNIQUE,
            platform TEXT NOT NULL,
            scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            result_data JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_url_cache_url ON url_cache(url);
        CREATE INDEX IF NOT EXISTS idx_url_cache_platform ON url_cache(platform);
        CREATE INDEX IF NOT EXISTS idx_url_cache_scraped_at ON url_cache(scraped_at);
        CREATE INDEX IF NOT EXISTS idx_url_cache_created_at ON url_cache(created_at);
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_sql)
                    conn.commit()
        except Exception as e:
            print(f"Failed to create tables: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get connection from pool."""
        if not self.connection_pool:
            raise RuntimeError("PostgreSQL pool not initialized")
        
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def is_cached(self, url: str, platform: str) -> bool:
        """
        Check if URL is cached.
        
        Args:
            url: URL to check
            platform: Platform name
        
        Returns:
            True if cached, False otherwise
        """
        if not self.connection_pool:
            return False
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM url_cache WHERE url = %s AND platform = %s",
                        (url, platform)
                    )
                    return cur.fetchone() is not None
        except Exception:
            return False
    
    def add_to_cache(self, url: str, platform: str, result_data: Optional[dict] = None):
        """
        Add URL to cache.
        
        Args:
            url: URL to cache
            platform: Platform name
            result_data: Optional result data to store
        """
        if not self.connection_pool:
            return
        
        try:
            import json
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO url_cache (url, platform, scraped_at, result_data)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE
                        SET scraped_at = EXCLUDED.scraped_at,
                            result_data = EXCLUDED.result_data
                        """,
                        (url, platform, datetime.now(), json.dumps(result_data) if result_data else None)
                    )
                    conn.commit()
        except Exception:
            pass  # Cache write failure is not critical
    
    def get_cached_result(self, url: str, platform: str) -> Optional[dict]:
        """
        Get cached result for URL.
        
        Args:
            url: URL to retrieve
            platform: Platform name
        
        Returns:
            Cached result data or None
        """
        if not self.connection_pool:
            return None
        
        try:
            import json
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT result_data FROM url_cache WHERE url = %s AND platform = %s",
                        (url, platform)
                    )
                    row = cur.fetchone()
                    if row and row["result_data"]:
                        return json.loads(row["result_data"])
        except Exception as e:
            import logging
            logging.debug(f"Error retrieving from PostgreSQL cache for {url}: {e}")
        
        return None
    
    def cleanup_old_records(self, days: int = 30):
        """
        Clean up records older than specified days.
        
        Args:
            days: Number of days to keep
        """
        if not self.connection_pool:
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM url_cache WHERE created_at < %s",
                        (cutoff_date,)
                    )
                    deleted = cur.rowcount
                    conn.commit()
                    return deleted
        except Exception:
            return 0
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        if not self.connection_pool:
            return {"total": 0, "by_platform": {}}
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Total count
                    cur.execute("SELECT COUNT(*) as total FROM url_cache")
                    total = cur.fetchone()["total"]
                    
                    # By platform
                    cur.execute(
                        "SELECT platform, COUNT(*) as count FROM url_cache GROUP BY platform"
                    )
                    by_platform = {row["platform"]: row["count"] for row in cur.fetchall()}
                    
                    return {
                        "total": total,
                        "by_platform": by_platform
                    }
        except Exception:
            return {"total": 0, "by_platform": {}}
    
    def close(self):
        """Close connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None


# Global instance
_postgresql_cache: Optional[PostgreSQLCache] = None

def get_postgresql_cache() -> Optional[PostgreSQLCache]:
    """Get or create global PostgreSQL cache instance."""
    global _postgresql_cache
    if _postgresql_cache is None:
        _postgresql_cache = PostgreSQLCache()
    return _postgresql_cache

