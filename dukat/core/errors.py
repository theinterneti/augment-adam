"""Error handling and resilience components for Dukat.

This module provides error handling and resilience components for the Dukat assistant,
including custom exceptions, error classification, and retry/circuit breaker patterns.

Version: 0.1.0
Created: 2025-04-25
"""

import functools
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union, TypeVar, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class ErrorCategory(Enum):
    """Categories of errors for better handling and reporting."""

    # System-level errors
    SYSTEM = "system"  # System-level errors (OS, hardware, etc.)
    NETWORK = "network"  # Network-related errors
    TIMEOUT = "timeout"  # Timeout errors
    RESOURCE = "resource"  # Resource-related errors (memory, disk, etc.)

    # Application-level errors
    VALIDATION = "validation"  # Input validation errors
    AUTHENTICATION = "authentication"  # Authentication errors
    AUTHORIZATION = "authorization"  # Authorization errors
    NOT_FOUND = "not_found"  # Resource not found errors

    # Integration-level errors
    DATABASE = "database"  # Database-related errors
    API = "api"  # External API-related errors
    MODEL = "model"  # AI model-related errors
    PLUGIN = "plugin"  # Plugin-related errors
    DEPENDENCY = "dependency"  # External dependency errors

    # Other errors
    UNKNOWN = "unknown"  # Unknown or unclassified errors


class DukatError(Exception):
    """Base exception class for all Dukat-specific exceptions."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            category: The error category.
            original_error: The original exception that caused this error.
            details: Additional details about the error.
        """
        self.message = message
        self.category = category
        self.original_error = original_error
        self.details = details or {}

        # Construct the full error message
        full_message = f"{category.value.upper()}: {message}"
        if original_error:
            full_message += f" (Original error: {str(original_error)})"

        super().__init__(full_message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the exception to a dictionary.

        Returns:
            A dictionary representation of the exception.
        """
        result = {
            "message": self.message,  # Used by tests
            "error_message": self.message,  # Renamed to avoid conflict with LogRecord
            "category": self.category.value,
            "details": self.details,
        }

        if self.original_error:
            result["original_error"] = str(self.original_error)
            result["original_error_type"] = type(self.original_error).__name__

        return result


# System-level exceptions
class SystemError(DukatError):
    """Exception raised for system-level errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM,
            original_error=original_error,
            details=details,
        )


class NetworkError(DukatError):
    """Exception raised for network-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            original_error=original_error,
            details=details,
        )


class TimeoutError(DukatError):
    """Exception raised for timeout errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT,
            original_error=original_error,
            details=details,
        )


class ResourceError(DukatError):
    """Exception raised for resource-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.RESOURCE,
            original_error=original_error,
            details=details,
        )


# Application-level exceptions
class ValidationError(DukatError):
    """Exception raised for input validation errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            original_error=original_error,
            details=details,
        )


class AuthenticationError(DukatError):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            original_error=original_error,
            details=details,
        )


class AuthorizationError(DukatError):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            original_error=original_error,
            details=details,
        )


class NotFoundError(DukatError):
    """Exception raised for resource not found errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.NOT_FOUND,
            original_error=original_error,
            details=details,
        )


# Integration-level exceptions
class DatabaseError(DukatError):
    """Exception raised for database-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            original_error=original_error,
            details=details,
        )


class ApiError(DukatError):
    """Exception raised for external API-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.API,
            original_error=original_error,
            details=details,
        )


class ModelError(DukatError):
    """Exception raised for AI model-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.MODEL,
            original_error=original_error,
            details=details,
        )


class PluginError(DukatError):
    """Exception raised for plugin-related errors."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.PLUGIN,
            original_error=original_error,
            details=details,
        )


# Error handling utilities
def classify_error(error: Exception) -> ErrorCategory:
    """Classify an error into a category.

    Args:
        error: The error to classify.

    Returns:
        The error category.
    """
    if isinstance(error, DukatError):
        return error.category

    error_type = type(error).__name__.lower()
    error_str = str(error).lower()

    # Network errors
    if any(term in error_type for term in ["network", "connection", "socket", "http"]):
        return ErrorCategory.NETWORK

    # Timeout errors
    if any(term in error_type for term in ["timeout", "timed out"]) or "timeout" in error_str:
        return ErrorCategory.TIMEOUT

    # Resource errors
    if any(term in error_type for term in ["memory", "disk", "resource"]):
        return ErrorCategory.RESOURCE

    # Database errors
    if any(term in error_type for term in ["database", "db", "sql"]):
        return ErrorCategory.DATABASE

    # API errors
    if any(term in error_type for term in ["api", "http", "request"]):
        return ErrorCategory.API

    # Default to unknown
    return ErrorCategory.UNKNOWN


def wrap_error(
    error: Exception,
    message: Optional[str] = None,
    category: Optional[ErrorCategory] = None,
    details: Optional[Dict[str, Any]] = None,
) -> DukatError:
    """Wrap an error in a DukatError.

    Args:
        error: The error to wrap.
        message: The error message. If None, the original error message is used.
        category: The error category. If None, the category is determined automatically.
        details: Additional details about the error.

    Returns:
        A DukatError wrapping the original error.
    """
    if isinstance(error, DukatError):
        return error

    error_message = message or str(error)
    error_category = category or classify_error(error)

    # Create the appropriate error type based on the category
    if error_category == ErrorCategory.NETWORK:
        return NetworkError(error_message, original_error=error, details=details)
    elif error_category == ErrorCategory.TIMEOUT:
        return TimeoutError(error_message, original_error=error, details=details)
    elif error_category == ErrorCategory.RESOURCE:
        return ResourceError(error_message, original_error=error, details=details)
    elif error_category == ErrorCategory.DATABASE:
        return DatabaseError(error_message, original_error=error, details=details)
    elif error_category == ErrorCategory.API:
        return ApiError(error_message, original_error=error, details=details)
    elif error_category == ErrorCategory.MODEL:
        return ModelError(error_message, original_error=error, details=details)
    elif error_category == ErrorCategory.PLUGIN:
        return PluginError(error_message, original_error=error, details=details)
    else:
        return DukatError(error_message, error_category, original_error=error, details=details)


def log_error(
    error: Exception,
    logger: logging.Logger = logger,
    level: int = logging.ERROR,
    include_traceback: bool = True,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log an error with appropriate context.

    Args:
        error: The error to log.
        logger: The logger to use.
        level: The logging level.
        include_traceback: Whether to include the traceback.
        context: Additional context to include in the log.
    """
    context = context or {}

    # Create a safe copy of context without reserved keys
    safe_context = {}
    reserved_keys = {"message", "asctime"}

    for key, value in context.items():
        if key not in reserved_keys:
            safe_context[key] = value

    if isinstance(error, DukatError):
        error_dict = error.to_dict()

        # Remove reserved keys from error_dict
        for key in reserved_keys:
            if key in error_dict:
                error_dict[f"error_{key}"] = error_dict.pop(key)

        # Update with safe context
        error_dict.update(safe_context)

        if include_traceback:
            logger.log(level, f"Error: {error}",
                       extra=error_dict, exc_info=True)
        else:
            logger.log(level, f"Error: {error}", extra=error_dict)
    else:
        error_category = classify_error(error)
        error_dict = {
            "error_message": str(error),  # Renamed to avoid conflict
            "category": error_category.value,
            "error_type": type(error).__name__,
        }

        # Update with safe context
        error_dict.update(safe_context)

        if include_traceback:
            logger.log(level, f"Error: {error}",
                       extra=error_dict, exc_info=True)
        else:
            logger.log(level, f"Error: {error}", extra=error_dict)


# Retry decorator
def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    exceptions: List[Type[Exception]] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
) -> Callable[[F], F]:
    """Retry decorator for functions that might fail.

    Args:
        max_attempts: Maximum number of attempts.
        delay: Initial delay between attempts in seconds.
        backoff_factor: Factor by which the delay increases.
        max_delay: Maximum delay between attempts in seconds.
        exceptions: List of exceptions to catch. If None, all exceptions are caught.
        on_retry: Function to call before each retry.

    Returns:
        A decorator function.
    """
    exceptions = exceptions or [Exception]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    if attempt == max_attempts:
                        # Last attempt failed, re-raise the exception
                        raise

                    # Call the on_retry function if provided
                    if on_retry:
                        on_retry(e, attempt, current_delay)

                    # Get function name safely (handles MagicMock objects in tests)
                    func_name = getattr(func, "__name__", str(func))

                    # Log the retry
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func_name} after error: {e}",
                        extra={
                            "function": func_name,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "delay": current_delay,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    )

                    # Wait before retrying
                    time.sleep(current_delay)

                    # Increase the delay for the next attempt
                    current_delay = min(
                        current_delay * backoff_factor, max_delay)
                    attempt += 1

        return cast(F, wrapper)

    return decorator


# Circuit breaker implementation
class CircuitBreakerState(Enum):
    """States for the circuit breaker."""

    CLOSED = "closed"  # Circuit is closed, requests are allowed
    OPEN = "open"  # Circuit is open, requests are not allowed
    HALF_OPEN = "half_open"  # Circuit is half-open, limited requests are allowed


class CircuitBreaker:
    """Implementation of the circuit breaker pattern."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exceptions: List[Type[Exception]] = None,
        on_open: Optional[Callable[[str, Exception], None]] = None,
        on_close: Optional[Callable[[str], None]] = None,
        on_half_open: Optional[Callable[[str], None]] = None,
    ):
        """Initialize the circuit breaker.

        Args:
            name: Name of the circuit breaker.
            failure_threshold: Number of consecutive failures before opening the circuit.
            recovery_timeout: Time in seconds before attempting recovery.
            expected_exceptions: List of exceptions that are considered failures.
            on_open: Function to call when the circuit opens.
            on_close: Function to call when the circuit closes.
            on_half_open: Function to call when the circuit half-opens.
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions or [Exception]
        self.on_open = on_open
        self.on_close = on_close
        self.on_half_open = on_half_open

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._last_success_time = 0.0

    @property
    def state(self) -> CircuitBreakerState:
        """Get the current state of the circuit breaker.

        Returns:
            The current state.
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if (
            self._state == CircuitBreakerState.OPEN
            and time.time() - self._last_failure_time >= self.recovery_timeout
        ):
            self._state = CircuitBreakerState.HALF_OPEN
            if self.on_half_open:
                self.on_half_open(self.name)

        return self._state

    def __call__(self, func: F) -> F:
        """Decorator for functions that might fail.

        Args:
            func: The function to decorate.

        Returns:
            The decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.call(func, *args, **kwargs)

        return cast(F, wrapper)

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Call a function with circuit breaker protection.

        Args:
            func: The function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the function call.

        Raises:
            CircuitBreakerError: If the circuit is open.
            Exception: Any exception raised by the function.
        """
        current_state = self.state

        if current_state == CircuitBreakerState.OPEN:
            raise CircuitBreakerError(
                f"Circuit {self.name} is OPEN until {self._last_failure_time + self.recovery_timeout}",
                circuit_name=self.name,
                state=current_state,
            )

        try:
            result = func(*args, **kwargs)

            # Success, reset failure count and update last success time
            self._handle_success()

            return result
        except tuple(self.expected_exceptions) as e:
            # Failure, increment failure count and update last failure time
            self._handle_failure(e)

            # Re-raise the exception
            raise

    def _handle_success(self) -> None:
        """Handle a successful call."""
        self._last_success_time = time.time()

        if self._state == CircuitBreakerState.HALF_OPEN:
            # Successful call in HALF_OPEN state, close the circuit
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0

            if self.on_close:
                self.on_close(self.name)
        elif self._state == CircuitBreakerState.CLOSED:
            # Successful call in CLOSED state, reset failure count
            self._failure_count = 0

    def _handle_failure(self, exception: Exception) -> None:
        """Handle a failed call.

        Args:
            exception: The exception that caused the failure.
        """
        self._last_failure_time = time.time()

        if self._state == CircuitBreakerState.CLOSED:
            # Increment failure count
            self._failure_count += 1

            # Check if we should open the circuit
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitBreakerState.OPEN

                if self.on_open:
                    self.on_open(self.name, exception)
        elif self._state == CircuitBreakerState.HALF_OPEN:
            # Failed call in HALF_OPEN state, open the circuit again
            self._state = CircuitBreakerState.OPEN

            if self.on_open:
                self.on_open(self.name, exception)

    def reset(self) -> None:
        """Reset the circuit breaker to its initial state."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._last_success_time = 0.0

        if self.on_close:
            self.on_close(self.name)


class CircuitBreakerError(DukatError):
    """Exception raised when a circuit breaker is open."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.DEPENDENCY,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            category: The error category.
            original_error: The original exception that caused this error.
            details: Additional details about the error.
        """
        super().__init__(
            message=message,
            category=category,
            original_error=original_error,
            details=details,
        )
