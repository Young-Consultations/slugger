"""Error handling and retry logic.

This module provides resilient execution with automatic retries,
exponential backoff, and graceful error handling.
"""
import time
from typing import Any, Callable, Dict, Optional, Type
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, backoff_factor: float = 2.0,
                 retriable_exceptions: tuple = (Exception,)):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Multiplier for exponential backoff
            retriable_exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retriable_exceptions = retriable_exceptions


class RetryableError(Exception):
    """Raised when a retriable operation fails after all retries."""
    pass


def retry_with_backoff(config: RetryConfig) -> Callable:
    """Decorator for automatic retry with exponential backoff.
    
    Args:
        config: RetryConfig instance with retry parameters
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            delay = config.base_delay
            
            while attempt < config.max_attempts:
                try:
                    logger.debug(f"Attempt {attempt + 1}/{config.max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except config.retriable_exceptions as e:
                    attempt += 1
                    if attempt >= config.max_attempts:
                        logger.error(f"Failed after {config.max_attempts} attempts: {e}")
                        raise RetryableError(f"Failed to execute {func.__name__} after {config.max_attempts} attempts") from e
                    
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * config.backoff_factor, config.max_delay)
        
        return wrapper
    return decorator


class ErrorRecovery:
    """Handle errors and provide recovery strategies."""

    def __init__(self):
        """Initialize error recovery handler."""
        self.recovery_strategies: Dict[Type[Exception], Callable] = {}

    def register_recovery(self, exception_type: Type[Exception], 
                         recovery_fn: Callable[[Exception], Any]) -> None:
        """Register a recovery strategy for an exception type.
        
        Args:
            exception_type: Exception class to handle
            recovery_fn: Callable that handles the exception and returns recovery result
        """
        self.recovery_strategies[exception_type] = recovery_fn

    def recover(self, exception: Exception) -> Optional[Any]:
        """Attempt to recover from an exception.
        
        Args:
            exception: The exception that occurred
            
        Returns:
            Recovery result or None if no recovery strategy found
        """
        # Check for exact match first
        if type(exception) in self.recovery_strategies:
            recovery_fn = self.recovery_strategies[type(exception)]
            logger.info(f"Executing recovery strategy for {type(exception).__name__}")
            return recovery_fn(exception)
        
        # Check for parent class match
        for exc_type, recovery_fn in self.recovery_strategies.items():
            if isinstance(exception, exc_type):
                logger.info(f"Executing recovery strategy for {exc_type.__name__}")
                return recovery_fn(exception)
        
        logger.warning(f"No recovery strategy found for {type(exception).__name__}")
        return None


class AgentExecutionError(Exception):
    """Raised when agent execution fails."""
    pass


class ProviderError(Exception):
    """Raised when provider request fails."""
    pass


def create_default_error_recovery() -> ErrorRecovery:
    """Create error recovery with default strategies.
    
    Returns:
        Configured ErrorRecovery instance
    """
    recovery = ErrorRecovery()
    
    # Retry strategy for provider errors
    def retry_provider_error(exc: Exception) -> Dict[str, Any]:
        return {"status": "error", "message": "Provider error, will retry", "retriable": True}
    
    # Fallback strategy for agent errors
    def fallback_agent_error(exc: Exception) -> Dict[str, Any]:
        return {"status": "error", "message": str(exc), "retriable": False}
    
    recovery.register_recovery(ProviderError, retry_provider_error)
    recovery.register_recovery(AgentExecutionError, fallback_agent_error)
    
    return recovery
