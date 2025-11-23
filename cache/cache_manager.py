"""Cache manager for coordinating URL and data caching."""
from __future__ import annotations

from typing import Optional
from .url_cache import URLCache


class CacheManager:
    """
    Central cache manager for coordinating all caching operations.
    """
    
    def __init__(self, cache_dir: str = "cache", ttl_days: int = 30):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files
            ttl_days: Time-to-live in days
        """
        self.cache_dir = cache_dir
        self.url_cache = URLCache(
            db_path=f"{cache_dir}/url_cache.db",
            ttl_days=ttl_days
        )
    
    def is_url_cached(self, url: str) -> bool:
        """Check if URL is cached."""
        return self.url_cache.is_cached(url)
    
    def cache_url(self, url: str, platform: str, data_hash: Optional[str] = None) -> None:
        """Cache a URL."""
        self.url_cache.add(url, platform, data_hash)
    
    def clear_expired(self) -> int:
        """Clear expired cache entries."""
        return self.url_cache.clear_expired()
    
    def clear_all(self) -> None:
        """Clear all cache entries."""
        self.url_cache.clear_all()

