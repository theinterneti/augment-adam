"""Unit tests for error handling and resilience components.

This module contains tests for the error handling and resilience components.

Version: 0.1.0
Created: 2025-04-25
"""

import logging
import time
import unittest
from unittest.mock import MagicMock, patch

import pytest

from dukat.core.errors import (
    ApiError,
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerState,
    DatabaseError,
    DukatError,
    ErrorCategory,
    ModelError,
    NetworkError,
    PluginError,
    ResourceError,
    TimeoutError,
    ValidationError,
    classify_error,
    log_error,
    retry,
    wrap_error,
)


class TestErrorCategories(unittest.TestCase):
    """Test error categories."""

    def test_error_categories(self):
        """Test that error categories are defined correctly."""
        self.assertEqual(ErrorCategory.SYSTEM.value, "system")
        self.assertEqual(ErrorCategory.NETWORK.value, "network")
        self.assertEqual(ErrorCategory.TIMEOUT.value, "timeout")
        self.assertEqual(ErrorCategory.RESOURCE.value, "resource")
        self.assertEqual(ErrorCategory.VALIDATION.value, "validation")
        self.assertEqual(ErrorCategory.AUTHENTICATION.value, "authentication")
        self.assertEqual(ErrorCategory.AUTHORIZATION.value, "authorization")
        self.assertEqual(ErrorCategory.NOT_FOUND.value, "not_found")
        self.assertEqual(ErrorCategory.DATABASE.value, "database")
        self.assertEqual(ErrorCategory.API.value, "api")
        self.assertEqual(ErrorCategory.MODEL.value, "model")
        self.assertEqual(ErrorCategory.PLUGIN.value, "plugin")
        self.assertEqual(ErrorCategory.UNKNOWN.value, "unknown")


class TestDukatError(unittest.TestCase):
    """Test DukatError class."""

    def test_dukat_error_init(self):
        """Test DukatError initialization."""
        error = DukatError("Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.category, ErrorCategory.UNKNOWN)
        self.assertIsNone(error.original_error)
        self.assertEqual(error.details, {})

    def test_dukat_error_with_category(self):
        """Test DukatError with category."""
        error = DukatError("Test error", category=ErrorCategory.NETWORK)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.category, ErrorCategory.NETWORK)

    def test_dukat_error_with_original_error(self):
        """Test DukatError with original error."""
        original = ValueError("Original error")
        error = DukatError("Test error", original_error=original)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.original_error, original)

    def test_dukat_error_with_details(self):
        """Test DukatError with details."""
        details = {"key": "value"}
        error = DukatError("Test error", details=details)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details, details)

    def test_dukat_error_to_dict(self):
        """Test DukatError to_dict method."""
        original = ValueError("Original error")
        details = {"key": "value"}
        error = DukatError(
            "Test error",
            category=ErrorCategory.NETWORK,
            original_error=original,
            details=details,
        )

        error_dict = error.to_dict()
        self.assertEqual(error_dict["error_message"], "Test error")
        self.assertEqual(error_dict["category"], "network")
        self.assertEqual(error_dict["details"], details)
        self.assertEqual(error_dict["original_error"], "Original error")
        self.assertEqual(error_dict["original_error_type"], "ValueError")


class TestSpecificErrors(unittest.TestCase):
    """Test specific error classes."""

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Network error")
        self.assertEqual(error.message, "Network error")
        self.assertEqual(error.category, ErrorCategory.NETWORK)

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("Timeout error")
        self.assertEqual(error.message, "Timeout error")
        self.assertEqual(error.category, ErrorCategory.TIMEOUT)

    def test_resource_error(self):
        """Test ResourceError."""
        error = ResourceError("Resource error")
        self.assertEqual(error.message, "Resource error")
        self.assertEqual(error.category, ErrorCategory.RESOURCE)

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Validation error")
        self.assertEqual(error.message, "Validation error")
        self.assertEqual(error.category, ErrorCategory.VALIDATION)

    def test_database_error(self):
        """Test DatabaseError."""
        error = DatabaseError("Database error")
        self.assertEqual(error.message, "Database error")
        self.assertEqual(error.category, ErrorCategory.DATABASE)

    def test_api_error(self):
        """Test ApiError."""
        error = ApiError("API error")
        self.assertEqual(error.message, "API error")
        self.assertEqual(error.category, ErrorCategory.API)

    def test_model_error(self):
        """Test ModelError."""
        error = ModelError("Model error")
        self.assertEqual(error.message, "Model error")
        self.assertEqual(error.category, ErrorCategory.MODEL)

    def test_plugin_error(self):
        """Test PluginError."""
        error = PluginError("Plugin error")
        self.assertEqual(error.message, "Plugin error")
        self.assertEqual(error.category, ErrorCategory.PLUGIN)


class TestErrorClassification(unittest.TestCase):
    """Test error classification."""

    def test_classify_dukat_error(self):
        """Test classifying a DukatError."""
        error = DukatError("Test error", category=ErrorCategory.NETWORK)
        category = classify_error(error)
        self.assertEqual(category, ErrorCategory.NETWORK)

    def test_classify_network_error(self):
        """Test classifying a network error."""
        error = ConnectionError("Connection error")
        category = classify_error(error)
        self.assertEqual(category, ErrorCategory.NETWORK)

    def test_classify_timeout_error(self):
        """Test classifying a timeout error."""
        error = TimeoutError("Timeout error")
        category = classify_error(error)
        self.assertEqual(category, ErrorCategory.TIMEOUT)

    def test_classify_unknown_error(self):
        """Test classifying an unknown error."""
        error = Exception("Unknown error")
        category = classify_error(error)
        self.assertEqual(category, ErrorCategory.UNKNOWN)


class TestErrorWrapping(unittest.TestCase):
    """Test error wrapping."""

    def test_wrap_dukat_error(self):
        """Test wrapping a DukatError."""
        original = DukatError("Original error", category=ErrorCategory.NETWORK)
        wrapped = wrap_error(original)
        self.assertIs(wrapped, original)

    def test_wrap_network_error(self):
        """Test wrapping a network error."""
        original = ConnectionError("Connection error")
        wrapped = wrap_error(original)
        self.assertIsInstance(wrapped, NetworkError)
        self.assertEqual(wrapped.message, "Connection error")
        self.assertEqual(wrapped.original_error, original)

    def test_wrap_with_custom_message(self):
        """Test wrapping with a custom message."""
        original = Exception("Original error")
        wrapped = wrap_error(original, message="Custom message")
        self.assertEqual(wrapped.message, "Custom message")

    def test_wrap_with_custom_category(self):
        """Test wrapping with a custom category."""
        original = Exception("Original error")
        wrapped = wrap_error(original, category=ErrorCategory.DATABASE)
        self.assertEqual(wrapped.category, ErrorCategory.DATABASE)
        self.assertIsInstance(wrapped, DatabaseError)

    def test_wrap_with_details(self):
        """Test wrapping with details."""
        original = Exception("Original error")
        details = {"key": "value"}
        wrapped = wrap_error(original, details=details)
        self.assertEqual(wrapped.details, details)


class TestErrorLogging(unittest.TestCase):
    """Test error logging."""

    def test_log_dukat_error(self):
        """Test logging a DukatError."""
        error = DukatError("Test error", category=ErrorCategory.NETWORK)
        mock_logger = MagicMock(spec=logging.Logger)

        log_error(error, logger=mock_logger)

        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        self.assertEqual(args[0], logging.ERROR)
        self.assertTrue(args[1].startswith("Error:"))
        self.assertTrue("extra" in kwargs)
        self.assertEqual(kwargs["extra"]["error_message"], "Test error")
        self.assertEqual(kwargs["extra"]["category"], "network")

    def test_log_standard_error(self):
        """Test logging a standard error."""
        error = ValueError("Test error")
        mock_logger = MagicMock(spec=logging.Logger)

        log_error(error, logger=mock_logger)

        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        self.assertEqual(args[0], logging.ERROR)
        self.assertTrue(args[1].startswith("Error:"))
        self.assertTrue("extra" in kwargs)
        self.assertEqual(kwargs["extra"]["error_message"], "Test error")
        self.assertEqual(kwargs["extra"]["error_type"], "ValueError")

    def test_log_with_context(self):
        """Test logging with context."""
        error = DukatError("Test error")
        mock_logger = MagicMock(spec=logging.Logger)
        context = {"request_id": "123", "user_id": "456"}

        log_error(error, logger=mock_logger, context=context)

        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        self.assertEqual(kwargs["extra"]["request_id"], "123")
        self.assertEqual(kwargs["extra"]["user_id"], "456")


class TestRetryDecorator(unittest.TestCase):
    """Test retry decorator."""

    def test_retry_success_first_attempt(self):
        """Test retry with success on first attempt."""
        mock_func = MagicMock(return_value="success")
        decorated = retry()(mock_func)

        result = decorated("arg1", kwarg1="kwarg1")

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", kwarg1="kwarg1")

    def test_retry_success_after_failure(self):
        """Test retry with success after failure."""
        mock_func = MagicMock(side_effect=[ValueError("Error"), "success"])
        decorated = retry(max_attempts=3, delay=0.01)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)

    def test_retry_all_attempts_fail(self):
        """Test retry with all attempts failing."""
        mock_func = MagicMock(side_effect=ValueError("Error"))
        decorated = retry(max_attempts=3, delay=0.01)(mock_func)

        with self.assertRaises(ValueError):
            decorated()

        self.assertEqual(mock_func.call_count, 3)

    def test_retry_with_specific_exceptions(self):
        """Test retry with specific exceptions."""
        mock_func = MagicMock(side_effect=[ValueError("Error"), "success"])
        decorated = retry(max_attempts=3, delay=0.01,
                          exceptions=[ValueError])(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)

    def test_retry_with_on_retry_callback(self):
        """Test retry with on_retry callback."""
        mock_func = MagicMock(side_effect=[ValueError("Error"), "success"])
        on_retry_mock = MagicMock()
        decorated = retry(max_attempts=3, delay=0.01,
                          on_retry=on_retry_mock)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)
        on_retry_mock.assert_called_once()
        args, _ = on_retry_mock.call_args
        self.assertIsInstance(args[0], ValueError)
        self.assertEqual(args[1], 1)  # attempt number
        self.assertEqual(args[2], 0.01)  # delay


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker."""

    def setUp(self):
        """Set up test fixtures."""
        self.on_open_mock = MagicMock()
        self.on_close_mock = MagicMock()
        self.on_half_open_mock = MagicMock()

        self.circuit_breaker = CircuitBreaker(
            name="test_circuit",
            failure_threshold=2,
            recovery_timeout=0.1,
            on_open=self.on_open_mock,
            on_close=self.on_close_mock,
            on_half_open=self.on_half_open_mock,
        )

    def test_initial_state(self):
        """Test initial state."""
        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.CLOSED)
        self.assertEqual(self.circuit_breaker._failure_count, 0)

    def test_success_call(self):
        """Test successful call."""
        mock_func = MagicMock(return_value="success")

        result = self.circuit_breaker.call(mock_func, "arg1", kwarg1="kwarg1")

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", kwarg1="kwarg1")
        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.CLOSED)
        self.assertEqual(self.circuit_breaker._failure_count, 0)

    def test_failure_below_threshold(self):
        """Test failure below threshold."""
        mock_func = MagicMock(side_effect=ValueError("Error"))

        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.CLOSED)
        self.assertEqual(self.circuit_breaker._failure_count, 1)
        self.on_open_mock.assert_not_called()

    def test_failure_above_threshold(self):
        """Test failure above threshold."""
        mock_func = MagicMock(side_effect=ValueError("Error"))

        # First failure
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        # Second failure, should open the circuit
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)
        self.assertEqual(self.circuit_breaker._failure_count, 2)
        self.on_open_mock.assert_called_once()

        # Third call should fail with CircuitBreakerError
        with self.assertRaises(CircuitBreakerError):
            self.circuit_breaker.call(mock_func)

    def test_half_open_after_timeout(self):
        """Test half-open after timeout."""
        mock_func = MagicMock(side_effect=[ValueError(
            "Error"), ValueError("Error"), "success"])

        # First failure
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        # Second failure, should open the circuit
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)

        # Wait for recovery timeout
        time.sleep(0.2)

        # Circuit should be half-open now
        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.HALF_OPEN)
        self.on_half_open_mock.assert_called_once()

        # Successful call should close the circuit
        result = self.circuit_breaker.call(mock_func)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.CLOSED)
        self.on_close_mock.assert_called_once()

    def test_failure_in_half_open(self):
        """Test failure in half-open state."""
        mock_func = MagicMock(side_effect=[ValueError(
            "Error"), ValueError("Error"), ValueError("Error")])

        # First failure
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        # Second failure, should open the circuit
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)

        # Wait for recovery timeout
        time.sleep(0.2)

        # Circuit should be half-open now
        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.HALF_OPEN)

        # Failure in half-open should open the circuit again
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)
        self.assertEqual(self.on_open_mock.call_count, 2)

    def test_decorator(self):
        """Test circuit breaker as decorator."""
        mock_func = MagicMock(return_value="success")
        decorated = self.circuit_breaker(mock_func)

        result = decorated("arg1", kwarg1="kwarg1")

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", kwarg1="kwarg1")

    def test_reset(self):
        """Test reset."""
        mock_func = MagicMock(side_effect=ValueError("Error"))

        # First failure
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        # Second failure, should open the circuit
        with self.assertRaises(ValueError):
            self.circuit_breaker.call(mock_func)

        self.assertEqual(self.circuit_breaker.state, CircuitBreakerState.OPEN)

        # Reset the circuit breaker
        self.circuit_breaker.reset()

        self.assertEqual(self.circuit_breaker.state,
                         CircuitBreakerState.CLOSED)
        self.assertEqual(self.circuit_breaker._failure_count, 0)
        self.on_close_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
