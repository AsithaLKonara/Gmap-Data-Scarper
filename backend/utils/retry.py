"""Retry logic and circuit breaker utilities."""
import time
import logging
from typing import Callable, TypeVar, Optional, List
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorCategory(Enum):
    """Error categories for retry logic."""
    RETRYABLE = "retryable"  # Network errors, timeouts, transient failures
    FATAL = "fatal"  # Invalid input, authentication errors, permanent failures
    UNKNOWN = "unknown"  # Unknown errors, default to retryable


def categorize_error(error: Exception) -> ErrorCategory:
    """
    Categorize an error as retryable or fatal.
    
    Args:
        error: The exception to categorize
        
    Returns:
        ErrorCategory
    """
    error_type = type(error).__name__
    error_msg = str(error).lower()
    
    # Network-related errors (retryable)
    network_errors = [
        'connection', 'timeout', 'network', 'dns', 'socket',
        'connectionerror', 'timeouterror', 'httperror'
    ]
    
    # Fatal errors (don't retry)
    fatal_errors = [
        'authentication', 'authorization', 'forbidden', 'notfound',
        'valueerror', 'typeerror', 'attributeerror', 'keyerror'
    ]
    
    if any(net_err in error_type.lower() or net_err in error_msg for net_err in network_errors):
        return ErrorCategory.RETRYABLE
    
    if any(fatal_err in error_type.lower() or fatal_err in error_msg for fatal_err in fatal_errors):
        return ErrorCategory.FATAL
    
    return ErrorCategory.UNKNOWN


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            half_open_max_calls: Max calls in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0
    
    def call(self, func: Callable[[], T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "half_open"
                self.half_open_calls = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == "half_open":
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                # Circuit breaker closed (recovered)
                self.state = "closed"
                self.failure_count = 0
                self.half_open_calls = 0
        else:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
        
        if self.state == "half_open":
            # Failure in half-open state, open circuit again
            self.state = "open"
            self.half_open_calls = 0


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_errors: Optional[List[type]] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        retryable_errors: List of exception types to retry (None = all)
    """
    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    # Check if error is retryable
                    if retryable_errors and type(e) not in retryable_errors:
                        raise
                    
                    # Check error category
                    error_category = categorize_error(e)
                    if error_category == ErrorCategory.FATAL:
                        raise
                    
                    # Don't retry on last attempt
                    if attempt == max_retries:
                        break
                    
                    # Wait before retrying
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after error: {str(e)}"
                    )
                    time.sleep(min(delay, max_delay))
                    delay *= exponential_base
            
            # All retries exhausted
            raise last_error
        
        return wrapper
    return decorator


# Alias for convenience - supports both old and new parameter styles
def retry(attempts: int = 3, delay: float = 1.0, exceptions: Optional[List[type]] = None, **kwargs):
    """
    Retry decorator with backward compatibility.
    
    Args:
        attempts: Number of retry attempts (maps to max_retries)
        delay: Initial delay in seconds (maps to initial_delay)
        exceptions: List of exception types to retry
        **kwargs: Additional arguments passed to retry_with_backoff
    """
    return retry_with_backoff(
        max_retries=attempts - 1,  # attempts includes initial try
        initial_delay=delay,
        retryable_errors=exceptions,
        **kwargs
    )

