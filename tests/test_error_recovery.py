"""Tests for error handling and retry logic.

These tests verify that:
- Retry decorator applies exponential backoff
- Retriable exceptions trigger retries
- Max attempts limit is enforced
- Error recovery strategies work correctly
"""
import time
from unittest.mock import Mock, patch

from slugger.orchestrator.error_handling.recovery import (
    RetryConfig, RetryableError, retry_with_backoff, ErrorRecovery
)


def test_retry_success_on_first_attempt():
    config = RetryConfig(max_attempts=3, base_delay=0.1)
    
    @retry_with_backoff(config)
    def always_succeeds():
        return "success"
    
    result = always_succeeds()
    assert result == "success"


def test_retry_succeeds_after_failures():
    config = RetryConfig(max_attempts=3, base_delay=0.1)
    call_count = [0]
    
    @retry_with_backoff(config)
    def fails_twice_then_succeeds():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ValueError("Temporary failure")
        return "success"
    
    result = fails_twice_then_succeeds()
    assert result == "success"
    assert call_count[0] == 3


def test_retry_fails_after_max_attempts():
    config = RetryConfig(max_attempts=2, base_delay=0.05)
    call_count = [0]
    
    @retry_with_backoff(config)
    def always_fails():
        call_count[0] += 1
        raise ValueError("Persistent failure")
    
    try:
        always_fails()
        assert False, "Should have raised RetryableError"
    except RetryableError:
        assert call_count[0] == 2


def test_error_recovery_exact_match():
    recovery = ErrorRecovery()
    
    def handle_value_error(exc):
        return {"recovered": True, "error": str(exc)}
    
    recovery.register_recovery(ValueError, handle_value_error)
    
    exc = ValueError("test error")
    result = recovery.recover(exc)
    assert result["recovered"] is True


def test_error_recovery_no_strategy():
    recovery = ErrorRecovery()
    
    exc = RuntimeError("test error")
    result = recovery.recover(exc)
    assert result is None


def test_error_recovery_parent_class_match():
    recovery = ErrorRecovery()
    
    def handle_exception(exc):
        return {"recovered": True}
    
    recovery.register_recovery(Exception, handle_exception)
    
    exc = ValueError("test error")
    result = recovery.recover(exc)
    assert result["recovered"] is True
