"""Smart rate limiting with dynamic adjustment."""
from __future__ import annotations

import time
from typing import Optional
from collections import deque


class RateLimiter:
    """
    Smart rate limiter with dynamic wait adjustment.
    
    Automatically adjusts delays based on request success/failure.
    """
    
    def __init__(
        self,
        base_delay: float = 2.0,
        min_delay: float = 0.5,
        max_delay: float = 10.0,
        backoff_factor: float = 1.5,
        success_reduction: float = 0.9
    ):
        """
        Initialize rate limiter.
        
        Args:
            base_delay: Base delay between requests (seconds)
            min_delay: Minimum delay (seconds)
            max_delay: Maximum delay (seconds)
            backoff_factor: Factor to multiply delay on error
            success_reduction: Factor to reduce delay on success
        """
        self.current_delay = base_delay
        self.base_delay = base_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.success_reduction = success_reduction
        self.last_request_time = 0.0
        self.recent_errors = deque(maxlen=10)  # Track last 10 errors
    
    def wait(self) -> None:
        """Wait for the current delay period."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.current_delay:
            sleep_time = self.current_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def record_success(self) -> None:
        """Record a successful request and reduce delay."""
        # Gradually reduce delay on success
        self.current_delay = max(
            self.min_delay,
            self.current_delay * self.success_reduction
        )
    
    def record_error(self) -> None:
        """Record an error and increase delay (exponential backoff)."""
        self.recent_errors.append(time.time())
        
        # Increase delay on error
        self.current_delay = min(
            self.max_delay,
            self.current_delay * self.backoff_factor
        )
    
    def get_current_delay(self) -> float:
        """Get current delay value."""
        return self.current_delay
    
    def reset(self) -> None:
        """Reset to base delay."""
        self.current_delay = self.base_delay
        self.recent_errors.clear()
    
    def get_error_rate(self) -> float:
        """Get recent error rate (0.0 to 1.0)."""
        if len(self.recent_errors) == 0:
            return 0.0
        
        # Calculate errors in last minute
        current_time = time.time()
        recent_count = sum(1 for err_time in self.recent_errors if current_time - err_time < 60)
        
        return recent_count / len(self.recent_errors) if self.recent_errors else 0.0

