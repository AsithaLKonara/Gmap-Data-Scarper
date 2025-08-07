"""
Production-ready caching system for LeadTap Platform
Supports Redis with memory fallback and comprehensive cache management
"""

import redis
import json
import hashlib
import time
import logging
from typing import Any, Optional, Union, Dict, List
from functools import wraps
from config import settings
import structlog

logger = structlog.get_logger(__name__)

class CacheManager:
    """Production-ready cache manager with Redis and memory fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with error handling"""
        try:
            if settings.ENABLE_CACHING and settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis cache initialized successfully")
            else:
                logger.info("⚠️ Redis cache disabled, using memory fallback")
                self.redis_client = None
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}, using memory fallback")
            self.redis_client = None
    
    def _generate_key(self, key: str, prefix: str = "leadtap") -> str:
        """Generate a consistent cache key"""
        return f"{prefix}:{hashlib.md5(key.encode()).hexdigest()}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with fallback"""
        try:
            cache_key = self._generate_key(key)
            
            # Try Redis first
            if self.redis_client:
                try:
                    value = self.redis_client.get(cache_key)
                    if value:
                        self.cache_stats["hits"] += 1
                        return json.loads(value)
                except Exception as e:
                    logger.warning(f"Redis get failed: {e}")
            
            # Fallback to memory cache
            if cache_key in self.memory_cache:
                item = self.memory_cache[cache_key]
                if item["expires"] > time.time():
                    self.cache_stats["hits"] += 1
                    return item["value"]
                else:
                    del self.memory_cache[cache_key]
            
            self.cache_stats["misses"] += 1
            return default
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        try:
            cache_key = self._generate_key(key)
            ttl = ttl or settings.CACHE_TIMEOUT_SECONDS
            
            # Try Redis first
            if self.redis_client:
                try:
                    serialized_value = json.dumps(value)
                    self.redis_client.setex(cache_key, ttl, serialized_value)
                    self.cache_stats["sets"] += 1
                    return True
                except Exception as e:
                    logger.warning(f"Redis set failed: {e}")
            
            # Fallback to memory cache
            self.memory_cache[cache_key] = {
                "value": value,
                "expires": time.time() + ttl
            }
            self.cache_stats["sets"] += 1
            
            # Clean expired items from memory cache
            self._cleanup_memory_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            cache_key = self._generate_key(key)
            
            # Try Redis first
            if self.redis_client:
                try:
                    self.redis_client.delete(cache_key)
                except Exception as e:
                    logger.warning(f"Redis delete failed: {e}")
            
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            self.cache_stats["deletes"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    def clear(self, pattern: str = None) -> bool:
        """Clear cache with optional pattern"""
        try:
            if pattern:
                cache_pattern = self._generate_key(pattern)
            else:
                cache_pattern = "leadtap:*"
            
            # Try Redis first
            if self.redis_client:
                try:
                    keys = self.redis_client.keys(cache_pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis clear failed: {e}")
            
            # Clear memory cache
            if pattern:
                pattern_key = self._generate_key(pattern)
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern_key in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            else:
                self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            cache_key = self._generate_key(key)
            
            # Try Redis first
            if self.redis_client:
                try:
                    return bool(self.redis_client.exists(cache_key))
                except Exception as e:
                    logger.warning(f"Redis exists failed: {e}")
            
            # Check memory cache
            if cache_key in self.memory_cache:
                item = self.memory_cache[cache_key]
                if item["expires"] > time.time():
                    return True
                else:
                    del self.memory_cache[cache_key]
            
            return False
            
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            **self.cache_stats,
            "memory_cache_size": len(self.memory_cache),
            "redis_enabled": self.redis_client is not None,
            "cache_enabled": settings.ENABLE_CACHING
        }
    
    def _cleanup_memory_cache(self):
        """Clean up expired items from memory cache"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if item["expires"] <= current_time
        ]
        for key in expired_keys:
            del self.memory_cache[key]
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for cache system"""
        try:
            redis_healthy = False
            if self.redis_client:
                try:
                    self.redis_client.ping()
                    redis_healthy = True
                except Exception:
                    pass
            
            return {
                "status": "healthy" if redis_healthy or settings.ENABLE_CACHING else "unhealthy",
                "redis_connected": redis_healthy,
                "memory_cache_size": len(self.memory_cache),
                "stats": self.get_stats()
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global cache instance
cache_manager = CacheManager()

# Cache decorator for functions
def cached(ttl: int = None, key_prefix: str = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Cache decorator for async functions
def async_cached(ttl: int = None, key_prefix: str = None):
    """Decorator to cache async function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Utility functions
def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return cache_manager.get_stats()

def clear_cache(pattern: str = None) -> bool:
    """Clear cache with optional pattern"""
    return cache_manager.clear(pattern)

def cache_health_check() -> Dict[str, Any]:
    """Check cache system health"""
    return cache_manager.health_check()

# Cache keys for common operations
class CacheKeys:
    """Common cache key patterns"""
    
    @staticmethod
    def user_profile(user_id: int) -> str:
        return f"user:profile:{user_id}"
    
    @staticmethod
    def user_permissions(user_id: int) -> str:
        return f"user:permissions:{user_id}"
    
    @staticmethod
    def analytics_dashboard(user_id: int) -> str:
        return f"analytics:dashboard:{user_id}"
    
    @staticmethod
    def lead_stats(user_id: int) -> str:
        return f"leads:stats:{user_id}"
    
    @staticmethod
    def job_status(job_id: int) -> str:
        return f"job:status:{job_id}"
    
    @staticmethod
    def plan_features(plan_id: int) -> str:
        return f"plan:features:{plan_id}"
    
    @staticmethod
    def system_config(key: str) -> str:
        return f"system:config:{key}"
    
    @staticmethod
    def api_rate_limit(user_id: int) -> str:
        return f"api:rate_limit:{user_id}"
    
    @staticmethod
    def search_results(query_hash: str) -> str:
        return f"search:results:{query_hash}"
    
    @staticmethod
    def whatsapp_campaign(campaign_id: int) -> str:
        return f"whatsapp:campaign:{campaign_id}" 
 