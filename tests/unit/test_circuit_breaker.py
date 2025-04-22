"""Tests for the circuit breaker implementation.

This module contains tests for the circuit breaker pattern implementation.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch

import pytest

from dukat.core.circuit_breaker import (
    CircuitBreaker, CircuitState,
    circuit_breaker, register_circuit_breaker, get_circuit_breaker,
    get_all_circuit_breakers, reset_all_circuit_breakers, get_circuit_breaker_stats
)
from dukat.core.errors import CircuitBreakerError, ErrorCategory


class TestCircuitBreaker(unittest.TestCase):
    """Test cases for the CircuitBreaker class."""

    def setUp(self):
        """Set up the test case."""
        # Reset all circuit breakers before each test
        reset_all_circuit_breakers()

    def test_init(self):
        """Test initialization of the circuit breaker."""
        breaker = CircuitBreaker(name="test")
        self.assertEqual(breaker.name, "test")
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.total_calls, 0)
        self.assertEqual(breaker.successful_calls, 0)
        self.assertEqual(breaker.failed_calls, 0)

    def test_success(self):
        """Test recording a successful call."""
        breaker = CircuitBreaker(name="test")
        breaker.success()
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.total_calls, 1)
        self.assertEqual(breaker.successful_calls, 1)
        self.assertEqual(breaker.failed_calls, 0)

    def test_failure(self):
        """Test recording a failed call."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)
        breaker.failure(Exception("Test error"))
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 1)
        self.assertEqual(breaker.total_calls, 1)
        self.assertEqual(breaker.successful_calls, 0)
        self.assertEqual(breaker.failed_calls, 1)

    def test_open_circuit(self):
        """Test opening the circuit after reaching the failure threshold."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)

        # Record failures until the circuit opens
        for _ in range(3):
            breaker.failure(Exception("Test error"))

        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertEqual(breaker.failure_count, 3)
        self.assertEqual(breaker.total_calls, 3)
        self.assertEqual(breaker.successful_calls, 0)
        self.assertEqual(breaker.failed_calls, 3)

    def test_half_open_circuit(self):
        """Test transitioning to half-open state after timeout."""
        breaker = CircuitBreaker(
            name="test", failure_threshold=3, timeout_seconds=0.1)

        # Open the circuit
        for _ in range(3):
            breaker.failure(Exception("Test error"))

        self.assertEqual(breaker.state, CircuitState.OPEN)

        # Wait for the timeout
        time.sleep(0.2)

        # Check if the circuit is half-open
        self.assertTrue(breaker.allow_request())
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)

    def test_close_circuit_after_success(self):
        """Test closing the circuit after a successful call in half-open state."""
        breaker = CircuitBreaker(
            name="test", failure_threshold=3, timeout_seconds=0.1)

        # Open the circuit
        for _ in range(3):
            breaker.failure(Exception("Test error"))

        # Wait for the timeout
        time.sleep(0.2)

        # Allow a request in half-open state
        self.assertTrue(breaker.allow_request())

        # Record a success
        breaker.success()

        # Check if the circuit is closed
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    def test_reopen_circuit_after_failure(self):
        """Test reopening the circuit after a failure in half-open state."""
        breaker = CircuitBreaker(
            name="test", failure_threshold=3, timeout_seconds=0.1)

        # Open the circuit
        for _ in range(3):
            breaker.failure(Exception("Test error"))

        # Wait for the timeout
        time.sleep(0.2)

        # Allow a request in half-open state
        self.assertTrue(breaker.allow_request())

        # Record a failure
        breaker.failure(Exception("Test error"))

        # Check if the circuit is open again
        self.assertEqual(breaker.state, CircuitState.OPEN)

    def test_excluded_exceptions(self):
        """Test excluding certain exceptions from failure counting."""
        excluded = {ValueError}
        breaker = CircuitBreaker(
            name="test", failure_threshold=3, excluded_exceptions=excluded)

        # Record a failure with an excluded exception
        breaker.failure(ValueError("Excluded error"))

        # Check that the failure count is still 0
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.total_calls, 1)
        self.assertEqual(breaker.failed_calls, 1)

        # Record a failure with a non-excluded exception
        breaker.failure(Exception("Non-excluded error"))

        # Check that the failure count is now 1
        self.assertEqual(breaker.failure_count, 1)
        self.assertEqual(breaker.total_calls, 2)
        self.assertEqual(breaker.failed_calls, 2)

    def test_reset(self):
        """Test resetting the circuit breaker."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)

        # Open the circuit
        for _ in range(3):
            breaker.failure(Exception("Test error"))

        self.assertEqual(breaker.state, CircuitState.OPEN)

        # Reset the circuit breaker
        breaker.reset()

        # Check if the circuit is closed
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.half_open_calls, 0)

    def test_get_state(self):
        """Test getting the state of the circuit breaker."""
        breaker = CircuitBreaker(
            name="test", failure_threshold=3, timeout_seconds=60.0)

        # Record a failure
        breaker.failure(Exception("Test error"))

        # Get the state
        state = breaker.get_state()

        # Check the state
        self.assertEqual(state["name"], "test")
        self.assertEqual(state["state"], "closed")
        self.assertEqual(state["failure_count"], 1)
        self.assertEqual(state["failure_threshold"], 3)
        self.assertEqual(state["timeout_seconds"], 60.0)
        self.assertEqual(state["total_calls"], 1)
        self.assertEqual(state["successful_calls"], 0)
        self.assertEqual(state["failed_calls"], 1)


class TestCircuitBreakerDecorator:
    """Test cases for the circuit_breaker decorator."""

    def setup_method(self):
        """Set up the test case."""
        # Reset all circuit breakers before each test
        reset_all_circuit_breakers()

    def test_sync_function_success(self):
        """Test the decorator with a successful synchronous function."""
        @circuit_breaker(name="test_sync")
        def test_function():
            return "success"

        # Call the function
        result = test_function()

        # Check the result
        assert result == "success"

        # Get the circuit breaker
        breaker = get_circuit_breaker("test_sync")

        # Check the circuit breaker state
        assert breaker is not None
        assert breaker.state == CircuitState.CLOSED
        assert breaker.total_calls == 1
        assert breaker.successful_calls == 1
        assert breaker.failed_calls == 0

    def test_sync_function_failure(self):
        """Test the decorator with a failing synchronous function."""
        @circuit_breaker(name="test_sync_fail", failure_threshold=3)
        def test_function():
            raise ValueError("Test error")

        # Call the function and expect an exception
        for i in range(3):
            with pytest.raises(ValueError):
                test_function()

        # Get the circuit breaker
        breaker = get_circuit_breaker("test_sync_fail")

        # Check the circuit breaker state
        assert breaker is not None
        assert breaker.state == CircuitState.OPEN
        assert breaker.total_calls == 3
        assert breaker.successful_calls == 0
        assert breaker.failed_calls == 3

        # Try to call the function again
        with pytest.raises(CircuitBreakerError):
            test_function()

    @pytest.mark.asyncio
    async def test_async_function_success(self):
        """Test the decorator with a successful asynchronous function."""
        @circuit_breaker(name="test_async")
        async def test_function():
            return "success"

        # Call the function
        result = await test_function()

        # Check the result
        assert result == "success"

        # Get the circuit breaker
        breaker = get_circuit_breaker("test_async")

        # Check the circuit breaker state
        assert breaker is not None
        assert breaker.state == CircuitState.CLOSED
        assert breaker.total_calls == 1
        assert breaker.successful_calls == 1
        assert breaker.failed_calls == 0

    @pytest.mark.asyncio
    async def test_async_function_failure(self):
        """Test the decorator with a failing asynchronous function."""
        @circuit_breaker(name="test_async_fail", failure_threshold=3)
        async def test_function():
            raise ValueError("Test error")

        # Call the function and expect an exception
        for i in range(3):
            with pytest.raises(ValueError):
                await test_function()

        # Get the circuit breaker
        breaker = get_circuit_breaker("test_async_fail")

        # Check the circuit breaker state
        assert breaker is not None
        assert breaker.state == CircuitState.OPEN
        assert breaker.total_calls == 3
        assert breaker.successful_calls == 0
        assert breaker.failed_calls == 3

        # Try to call the function again
        with pytest.raises(CircuitBreakerError):
            await test_function()

    def test_excluded_exceptions(self):
        """Test excluding certain exceptions from failure counting."""
        @circuit_breaker(
            name="test_excluded",
            failure_threshold=3,
            excluded_exceptions={ValueError}
        )
        def test_function(raise_value_error=False):
            if raise_value_error:
                raise ValueError("Excluded error")
            else:
                raise RuntimeError("Non-excluded error")

        # Call the function with an excluded exception
        with pytest.raises(ValueError):
            test_function(raise_value_error=True)

        # Call the function with a non-excluded exception
        for i in range(3):
            with pytest.raises(RuntimeError):
                test_function(raise_value_error=False)

        # Get the circuit breaker
        breaker = get_circuit_breaker("test_excluded")

        # Check the circuit breaker state
        assert breaker is not None
        assert breaker.state == CircuitState.OPEN
        assert breaker.total_calls == 4
        assert breaker.successful_calls == 0
        assert breaker.failed_calls == 4
        assert breaker.failure_count == 3  # Only non-excluded exceptions count


class TestCircuitBreakerRegistry(unittest.TestCase):
    """Test cases for the circuit breaker registry."""

    def setUp(self):
        """Set up the test case."""
        # Reset all circuit breakers before each test
        reset_all_circuit_breakers()

    def test_register_circuit_breaker(self):
        """Test registering a circuit breaker."""
        breaker = CircuitBreaker(name="test_register")
        register_circuit_breaker(breaker)

        # Get the circuit breaker
        retrieved = get_circuit_breaker("test_register")

        # Check that the retrieved breaker is the same
        self.assertIs(retrieved, breaker)

    def test_get_circuit_breaker(self):
        """Test getting a circuit breaker."""
        breaker = CircuitBreaker(name="test_get")
        register_circuit_breaker(breaker)

        # Get the circuit breaker
        retrieved = get_circuit_breaker("test_get")

        # Check that the retrieved breaker is the same
        self.assertIs(retrieved, breaker)

        # Try to get a non-existent circuit breaker
        non_existent = get_circuit_breaker("non_existent")

        # Check that the result is None
        self.assertIsNone(non_existent)

    def test_get_all_circuit_breakers(self):
        """Test getting all circuit breakers."""
        # Create and register some circuit breakers
        breaker1 = CircuitBreaker(name="test1")
        breaker2 = CircuitBreaker(name="test2")
        breaker3 = CircuitBreaker(name="test3")

        register_circuit_breaker(breaker1)
        register_circuit_breaker(breaker2)
        register_circuit_breaker(breaker3)

        # Get all circuit breakers
        all_breakers = get_all_circuit_breakers()

        # Check that our breakers are in the list
        self.assertIn(breaker1, all_breakers)
        self.assertIn(breaker2, all_breakers)
        self.assertIn(breaker3, all_breakers)

    def test_reset_all_circuit_breakers(self):
        """Test resetting all circuit breakers."""
        # Create and register some circuit breakers
        breaker1 = CircuitBreaker(name="test1", failure_threshold=1)
        breaker2 = CircuitBreaker(name="test2", failure_threshold=1)

        register_circuit_breaker(breaker1)
        register_circuit_breaker(breaker2)

        # Open the circuits
        breaker1.failure(Exception("Test error"))
        breaker2.failure(Exception("Test error"))

        self.assertEqual(breaker1.state, CircuitState.OPEN)
        self.assertEqual(breaker2.state, CircuitState.OPEN)

        # Reset all circuit breakers
        reset_all_circuit_breakers()

        # Check that all circuits are closed
        self.assertEqual(breaker1.state, CircuitState.CLOSED)
        self.assertEqual(breaker2.state, CircuitState.CLOSED)
        self.assertEqual(breaker1.failure_count, 0)
        self.assertEqual(breaker2.failure_count, 0)

    def test_get_circuit_breaker_stats(self):
        """Test getting statistics for all circuit breakers."""
        # Create and register some circuit breakers
        breaker1 = CircuitBreaker(name="test_stats1")
        breaker2 = CircuitBreaker(name="test_stats2")

        register_circuit_breaker(breaker1)
        register_circuit_breaker(breaker2)

        # Record some activity
        breaker1.success()
        breaker2.failure(Exception("Test error"))

        # Get the stats
        stats = get_circuit_breaker_stats()

        # Check the stats for our test breakers
        self.assertIn("test_stats1", stats)
        self.assertIn("test_stats2", stats)

        self.assertEqual(stats["test_stats1"]["state"], "closed")
        self.assertEqual(stats["test_stats1"]["total_calls"], 1)
        self.assertEqual(stats["test_stats1"]["successful_calls"], 1)
        self.assertEqual(stats["test_stats1"]["failed_calls"], 0)

        self.assertEqual(stats["test_stats2"]["state"], "closed")
        self.assertEqual(stats["test_stats2"]["total_calls"], 1)
        self.assertEqual(stats["test_stats2"]["successful_calls"], 0)
        self.assertEqual(stats["test_stats2"]["failed_calls"], 1)
