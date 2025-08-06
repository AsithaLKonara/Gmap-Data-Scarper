# Enhanced Caching System for LeadTap Backend Performance Optimization
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps
import hashlib

logger = logging.getLogger("cache")

class MemoryCache:
    """Simple in-memory cache for development"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        # Check expiry
        if key in self._expiry and datetime.now() > self._expiry[key]:
            del self._cache[key]
            del self._expiry[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL"""
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)

# Global cache instance
cache = MemoryCache()

def cache_result(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args and kwargs to key
            if args:
                key_parts.append(str(args))
            if kwargs:
                key_parts.append(str(sorted(kwargs.items())))
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str = ""):
    """Clear cache entries matching pattern"""
    if not pattern:
        cache.clear()
        return
    
    keys_to_delete = []
    for key in cache._cache.keys():
        if pattern in key:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete(key)

def cache_user_data(user_id: int, data: Dict[str, Any], ttl_seconds: int = 600):
    """Cache user-specific data"""
    cache.set(f"user:{user_id}", data, ttl_seconds)

def get_cached_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached user data"""
    return cache.get(f"user:{user_id}")

def cache_job_results(job_id: int, results: Any, ttl_seconds: int = 3600):
    """Cache job results"""
    cache.set(f"job:{job_id}", results, ttl_seconds)

def get_cached_job_results(job_id: int) -> Optional[Any]:
    """Get cached job results"""
    return cache.get(f"job:{job_id}")

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    pattern = f"user:{user_id}"
    invalidate_cache(pattern)

def invalidate_job_cache(job_id: int):
    """Invalidate all cache entries for a job"""
    pattern = f"job:{job_id}"
    invalidate_cache(pattern) 
 