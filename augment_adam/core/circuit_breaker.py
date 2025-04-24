"""Circuit breaker implementation for external dependencies.

This module provides a circuit breaker pattern implementation to prevent
cascading failures when external dependencies are unavailable.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import enum
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union, cast

from augment_adam.core.errors import CircuitBreakerError, ErrorCategory

logger = logging.getLogger(__name__)

# Type variables for function signatures
T = TypeVar("T")
AsyncFunc = Callable[..., Any]
SyncFunc = Callable[..., Any]
AnyFunc = Union[AsyncFunc, SyncFunc]


class CircuitBreakerState(enum.Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"      # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if the service is back online


# Alias for backward compatibility
CircuitState = CircuitBreakerState


class CircuitBreaker:
    """Circuit breaker implementation.

    The circuit breaker prevents cascading failures by failing fast when
    a dependency is unavailable. It has three states:

    - CLOSED: Normal operation, requests pass through
    - OPEN: Circuit is open, requests fail fast
    - HALF_OPEN: Testing if the service is back online

    When the failure count exceeds the threshold, the circuit opens and
    remains open for the timeout period. After the timeout, it transitions
    to half-open and allows a single request through. If that request
    succeeds, the circuit closes; if it fails, the circuit opens again.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0,
        half_open_max_calls: int = 1,
        excluded_exceptions: Optional[Set[type]] = None,
    ):
        """Initialize the circuit breaker.

        Args:
            name: Name of the circuit breaker for identification
            failure_threshold: Number of failures before opening the circuit
            timeout_seconds: Time in seconds to keep the circuit open
            half_open_max_calls: Maximum number of calls allowed in half-open state
            excluded_exceptions: Exceptions that should not count as failures
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_max_calls = half_open_max_calls
        self.excluded_exceptions = excluded_exceptions or set()

        self._state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.half_open_calls = 0
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0

        logger.info(f"Circuit breaker '{name}' initialized")

    def __str__(self) -> str:
        """Return a string representation of the circuit breaker."""
        return (
            f"CircuitBreaker(name='{self.name}', state={self.state.value}, "
            f"failure_count={self.failure_count}/{self.failure_threshold})"
        )

    def reset(self) -> None:
        """Reset the circuit breaker to its initial state."""
        self._state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.half_open_calls = 0
        logger.info(f"Circuit breaker '{self.name}' reset")

    def success(self) -> None:
        """Record a successful call."""
        self.total_calls += 1
        self.successful_calls += 1
        self.last_success_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # If we're in half-open state and a call succeeds, close the circuit
            logger.info(
                f"Circuit breaker '{self.name}' closing after successful test")
            self._state = CircuitState.CLOSED
            self.failure_count = 0
            self.half_open_calls = 0

    def failure(self, exception: Exception) -> None:
        """Record a failed call.

        Args:
            exception: The exception that caused the failure
        """
        self.total_calls += 1
        self.failed_calls += 1

        # Check if this exception should be excluded
        if type(exception) in self.excluded_exceptions:
            logger.debug(
                f"Circuit breaker '{self.name}' ignoring excluded exception: {type(exception).__name__}"
            )
            return

        self.last_failure_time = time.time()

        if self.state == CircuitState.CLOSED:
            self.failure_count += 1

            if self.failure_count >= self.failure_threshold:
                logger.warning(
                    f"Circuit breaker '{self.name}' opening after {self.failure_count} failures"
                )
                self._state = CircuitState.OPEN

        elif self.state == CircuitState.HALF_OPEN:
            # If we're testing the service and it fails, open the circuit again
            logger.warning(
                f"Circuit breaker '{self.name}' opening after failed test")
            self._state = CircuitState.OPEN
            self.half_open_calls = 0

    @property
    def state(self) -> CircuitBreakerState:
        """Get the current state of the circuit breaker.

        This property automatically transitions from OPEN to HALF_OPEN
        when the timeout has elapsed.

        Returns:
            The current state of the circuit breaker.
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout_seconds:
                # Timeout elapsed, transition to half-open
                logger.info(
                    f"Circuit breaker '{self.name}' transitioning to half-open after timeout"
                )
                self._state = CircuitState.HALF_OPEN
                self.half_open_calls = 0

        return self._state

    @state.setter
    def state(self, value: CircuitBreakerState) -> None:
        """Set the state of the circuit breaker.

        Args:
            value: The new state.
        """
        self._state = value

    def allow_request(self) -> bool:
        """Check if a request should be allowed through the circuit breaker.

        Returns:
            True if the request should be allowed, False otherwise
        """
        current_state = self.state  # This will check for auto-transition

        if current_state == CircuitState.CLOSED:
            # Circuit is closed, allow the request
            return True

        elif current_state == CircuitState.OPEN:
            # Circuit is open, reject the request
            return False

        elif current_state == CircuitState.HALF_OPEN:
            # In half-open state, allow limited requests to test the service
            return self._check_half_open()

        # Default case (shouldn't happen)
        return False

    def _check_half_open(self) -> bool:
        """Check if a request should be allowed in half-open state.

        Returns:
            True if the request should be allowed, False otherwise
        """
        if self.half_open_calls < self.half_open_max_calls:
            self.half_open_calls += 1
            return True
        return False

    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the circuit breaker.

        Returns:
            A dictionary with the current state
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "timeout_seconds": self.timeout_seconds,
            "half_open_calls": self.half_open_calls,
            "half_open_max_calls": self.half_open_max_calls,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
        }


def circuit_breaker(
    name: Optional[str] = None,
    failure_threshold: int = 5,
    timeout_seconds: float = 60.0,
    excluded_exceptions: Optional[Set[type]] = None,
) -> Callable[[AnyFunc], AnyFunc]:
    """Decorator to apply a circuit breaker to a function.

    Args:
        name: Name of the circuit breaker (defaults to function name)
        failure_threshold: Number of failures before opening the circuit
        timeout_seconds: Time in seconds to keep the circuit open
        excluded_exceptions: Exceptions that should not count as failures

    Returns:
        A decorator function
    """
    def decorator(func: AnyFunc) -> AnyFunc:
        # Use function name if no name is provided
        breaker_name = name or func.__name__

        # Create a circuit breaker for this function
        breaker = CircuitBreaker(
            name=breaker_name,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds,
            excluded_exceptions=excluded_exceptions,
        )

        # Register the circuit breaker
        register_circuit_breaker(breaker)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Async wrapper for the decorated function."""
            if not breaker.allow_request():
                # Circuit is open, fail fast
                raise CircuitBreakerError(
                    f"Circuit breaker '{breaker_name}' is open",
                    category=ErrorCategory.DEPENDENCY,
                    details={
                        "circuit_breaker": breaker.get_state(),
                    },
                )

            try:
                # Call the original function
                result = await func(*args, **kwargs)

                # Record success
                breaker.success()

                return result

            except Exception as e:
                # Record failure
                breaker.failure(e)

                # Re-raise the exception
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Sync wrapper for the decorated function."""
            if not breaker.allow_request():
                # Circuit is open, fail fast
                raise CircuitBreakerError(
                    f"Circuit breaker '{breaker_name}' is open",
                    category=ErrorCategory.DEPENDENCY,
                    details={
                        "circuit_breaker": breaker.get_state(),
                    },
                )

            try:
                # Call the original function
                result = func(*args, **kwargs)

                # Record success
                breaker.success()

                return result

            except Exception as e:
                # Record failure
                breaker.failure(e)

                # Re-raise the exception
                raise

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return cast(AnyFunc, async_wrapper)
        else:
            return cast(AnyFunc, sync_wrapper)

    return decorator


# Global registry of circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def register_circuit_breaker(breaker: CircuitBreaker) -> None:
    """Register a circuit breaker in the global registry.

    Args:
        breaker: The circuit breaker to register
    """
    _circuit_breakers[breaker.name] = breaker
    logger.debug(f"Registered circuit breaker '{breaker.name}'")


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get a circuit breaker from the global registry.

    Args:
        name: Name of the circuit breaker

    Returns:
        The circuit breaker, or None if not found
    """
    return _circuit_breakers.get(name)


def get_all_circuit_breakers() -> List[CircuitBreaker]:
    """Get all circuit breakers from the global registry.

    Returns:
        A list of all circuit breakers
    """
    return list(_circuit_breakers.values())


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers in the global registry."""
    for breaker in _circuit_breakers.values():
        breaker.reset()
    logger.info("Reset all circuit breakers")


def get_circuit_breaker_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all circuit breakers.

    Returns:
        A dictionary mapping circuit breaker names to their states
    """
    return {name: breaker.get_state() for name, breaker in _circuit_breakers.items()}
