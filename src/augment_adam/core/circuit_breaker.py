"""Circuit breaker for Augment Adam.

This module provides functionality for implementing the circuit breaker pattern.
"""

import logging
import time
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """State of a circuit breaker."""
    CLOSED = auto()  # Normal operation, requests are allowed
    OPEN = auto()    # Failure threshold exceeded, requests are blocked
    HALF_OPEN = auto()  # Testing if the system has recovered


class CircuitBreaker:
    """Circuit breaker for Augment Adam.

    This class implements the circuit breaker pattern to prevent
    cascading failures in distributed systems.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 1,
    ):
        """Initialize the circuit breaker.

        Args:
            name: Name of the circuit breaker.
            failure_threshold: Number of consecutive failures before opening the circuit.
            recovery_timeout: Time in seconds to wait before testing if the system has recovered.
            half_open_max_calls: Maximum number of calls allowed in half-open state.
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0

        logger.info(f"Initialized circuit breaker {name}")

    def success(self) -> None:
        """Record a successful operation.

        This method should be called after a successful operation.
        """
        if self.state == CircuitBreakerState.CLOSED:
            # Reset failure count
            self.failure_count = 0
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Successful test, close the circuit
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.half_open_calls = 0
            logger.info(f"Circuit breaker {self.name} closed")

    def failure(self) -> None:
        """Record a failed operation.

        This method should be called after a failed operation.
        """
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.CLOSED:
            # Increment failure count
            self.failure_count += 1

            # Check if failure threshold is exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker {self.name} opened")
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Failed test, open the circuit again
            self.state = CircuitBreakerState.OPEN
            self.half_open_calls = 0
            logger.warning(f"Circuit breaker {self.name} reopened")

    def allow_request(self) -> bool:
        """Check if a request is allowed.

        This method should be called before performing an operation.

        Returns:
            True if the request is allowed, False otherwise.
        """
        if self.state == CircuitBreakerState.CLOSED:
            # Normal operation, allow the request
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                # Transition to half-open state
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit breaker {self.name} half-open")
                return True
            else:
                # Circuit is open, block the request
                return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited number of requests in half-open state
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            else:
                return False

        return False
