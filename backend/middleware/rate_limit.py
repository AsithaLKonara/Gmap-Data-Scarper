"""Enhanced rate limiting middleware with per-user and per-endpoint limits."""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
import time
import os


class RateLimitConfig:
    """Rate limit configuration for endpoints."""
    
    # Default limits (requests per window)
    DEFAULT_LIMITS = {
        "/api/scraper/start": (10, 60),  # 10 requests per minute
        "/api/scraper/stop": (20, 60),   # 20 requests per minute
        "/api/export": (30, 60),         # 30 requests per minute
        "/api/analytics": (60, 60),      # 60 requests per minute
        "/api/enrichment": (20, 60),     # 20 requests per minute
        "default": (100, 60),            # 100 requests per minute
    }
    
    # Per-user limits (higher for authenticated users)
    USER_LIMITS = {
        "default": (200, 60),  # 200 requests per minute for authenticated users
    }
    
    @classmethod
    def get_limit(cls, endpoint: str, is_authenticated: bool = False) -> Tuple[int, int]:
        """
        Get rate limit for endpoint.
        
        Args:
            endpoint: API endpoint path
            is_authenticated: Whether user is authenticated
            
        Returns:
            Tuple of (max_requests, window_seconds)
        """
        # Check endpoint-specific limits
        for path, limit in cls.DEFAULT_LIMITS.items():
            if endpoint.startswith(path):
                if is_authenticated:
                    # Authenticated users get 2x limit
                    return (limit[0] * 2, limit[1])
                return limit
        
        # Use default
        if is_authenticated:
            return cls.USER_LIMITS["default"]
        return cls.DEFAULT_LIMITS["default"]


class RateLimiter:
    """In-memory rate limiter (can be replaced with Redis for distributed systems)."""
    
    def __init__(self):
        # Track requests: {key: deque of timestamps}
        self.requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        # Track user requests: {user_id: {endpoint: deque}}
        self.user_requests: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=1000))
        )
    
    def _get_key(self, request: Request) -> str:
        """Get rate limit key from request (IP address)."""
        # Try to get real IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request if authenticated."""
        # Try to get from auth middleware
        if hasattr(request.state, "user") and request.state.user:
            return request.state.user.get("user_id")
        return None
    
    def check_rate_limit(
        self, 
        request: Request, 
        endpoint: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limit.
        
        Args:
            request: FastAPI request
            endpoint: API endpoint
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        # Skip rate limiting in test environment
        if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMIT") == "true":
            return (True, {"remaining": max_requests, "reset_at": int(time.time()) + window_seconds})
        
        current_time = time.time()
        user_id = self._get_user_id(request)
        
        # Clean old requests outside window
        cutoff_time = current_time - window_seconds
        
        if user_id:
            # Per-user rate limiting
            user_endpoint_key = f"{user_id}:{endpoint}"
            user_requests = self.user_requests[user_id][endpoint]
            
            # Remove old requests
            while user_requests and user_requests[0] < cutoff_time:
                user_requests.popleft()
            
            request_count = len(user_requests)
            
            if request_count >= max_requests:
                # Calculate reset time
                oldest_request = user_requests[0] if user_requests else current_time
                reset_time = int(oldest_request + window_seconds)
                
                return False, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": reset_time,
                    "retry_after": max(1, int(reset_time - current_time))
                }
            
            # Add current request
            user_requests.append(current_time)
            
            return True, {
                "limit": max_requests,
                "remaining": max_requests - request_count - 1,
                "reset": int(current_time + window_seconds),
                "retry_after": 0
            }
        else:
            # Per-IP rate limiting
            ip_key = self._get_key(request)
            ip_requests = self.requests[ip_key]
            
            # Remove old requests
            while ip_requests and ip_requests[0] < cutoff_time:
                ip_requests.popleft()
            
            request_count = len(ip_requests)
            
            if request_count >= max_requests:
                # Calculate reset time
                oldest_request = ip_requests[0] if ip_requests else current_time
                reset_time = int(oldest_request + window_seconds)
                
                return False, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": reset_time,
                    "retry_after": max(1, int(reset_time - current_time))
                }
            
            # Add current request
            ip_requests.append(current_time)
            
            return True, {
                "limit": max_requests,
                "remaining": max_requests - request_count - 1,
                "reset": int(current_time + window_seconds),
                "retry_after": 0
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits on all requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting in test environment
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING") == "true":
            return await call_next(request)
        
        # Skip rate limiting for health checks, docs, and test endpoints
        skip_paths = ["/health", "/api/health", "/docs", "/openapi.json", "/redoc", "/api/metrics"]
        if request.url.path in skip_paths or request.url.path.startswith("/api/health"):
            return await call_next(request)
        
        # Get endpoint
        endpoint = request.url.path
        
        # Check if user is authenticated
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("user_id")
        
        is_authenticated = user_id is not None
        
        # Get rate limit config
        max_requests, window_seconds = RateLimitConfig.get_limit(endpoint, is_authenticated)
        
        # Check rate limit
        is_allowed, rate_info = rate_limiter.check_rate_limit(
            request, endpoint, max_requests, window_seconds
        )
        
        if not is_allowed:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_info['limit']} per {window_seconds} seconds",
                    "retry_after": rate_info["retry_after"]
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["retry_after"])
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response

