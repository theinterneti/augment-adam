"""Unit tests for AsyncAssistant parallel execution and scheduling capabilities.

This module contains unit tests for the parallel execution and task scheduling
capabilities of the AsyncAssistant class.

Version: 0.1.0
Created: 2025-04-27
"""

import asyncio
import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Set

from dukat.core.async_assistant import AsyncAssistant, get_async_assistant
from dukat.core.parallel_executor import (
    ParallelTaskExecutor,
    ResourceRequirement,
    ResourceType,
)
from dukat.core.task_queue import Task, TaskStatus
from dukat.core.circuit_breaker import CircuitBreaker, CircuitBreakerState


class TestAsyncAssistantParallel(unittest.IsolatedAsyncioTestCase):
    """Tests for AsyncAssistant parallel execution capabilities."""

    async def asyncSetUp(self):
        """Set up the test environment."""
        # Create an AsyncAssistant with mocked components
        self.assistant = AsyncAssistant(
            model_name="test_model",
            ollama_host="http://localhost:11434",
            max_messages=100,
            conversation_id="test_conversation",
            max_parallel_tasks=3,
        )

        # Mock the parallel executor
        self.parallel_executor_mock = MagicMock(spec=ParallelTaskExecutor)
        self.parallel_executor_mock.add_task = AsyncMock()
        self.parallel_executor_mock.execute_all = AsyncMock(return_value={
            "task1": "result1",
            "task2": "result2",
        })
        self.parallel_executor_mock.get_task_metrics = MagicMock(return_value={
            "total_tasks": 2,
            "completed_tasks": 2,
            "running_tasks": 0,
            "pending_tasks": 0,
        })

        # Replace the parallel executor
        self.assistant.parallel_executor = self.parallel_executor_mock

    async def test_execute_tasks_in_parallel(self):
        """Test executing tasks in parallel."""
        # Create mock tasks
        async def task_1():
            return "result1"

        async def task_2():
            return "result2"

        # Define tasks
        tasks = [
            {
                "func": task_1,
                "task_id": "task1",
                "description": "Task 1",
            },
            {
                "func": task_2,
                "task_id": "task2",
                "description": "Task 2",
                "dependencies": ["task1"],
            },
        ]

        # Execute tasks in parallel
        results = await self.assistant.execute_tasks_in_parallel(tasks)

        # Check results
        self.assertEqual(results, {
            "task1": "result1",
            "task2": "result2",
        })

        # Check that add_task was called for each task
        self.assertEqual(self.parallel_executor_mock.add_task.call_count, 2)

        # Check that execute_all was called
        self.parallel_executor_mock.execute_all.assert_called_once()

        # Check that tasks are tracked
        self.assertEqual(self.assistant.active_tasks, {
            "task1": "parallel_task",
            "task2": "parallel_task",
        })

    async def test_execute_tasks_with_resources(self):
        """Test executing tasks with resource requirements."""
        # Create mock tasks
        async def task_1():
            return "result1"

        async def task_2():
            return "result2"

        # Define tasks with resource requirements
        tasks = [
            {
                "func": task_1,
                "task_id": "task1",
                "description": "Task 1",
                "resource_requirements": [
                    ResourceRequirement(ResourceType.CPU, amount=0.5),
                ],
            },
            {
                "func": task_2,
                "task_id": "task2",
                "description": "Task 2",
                "resource_requirements": [
                    ResourceRequirement(ResourceType.MEMORY, amount=0.3),
                ],
            },
        ]

        # Execute tasks in parallel
        results = await self.assistant.execute_tasks_in_parallel(tasks)

        # Check results
        self.assertEqual(results, {
            "task1": "result1",
            "task2": "result2",
        })

        # Check that add_task was called with resource requirements
        call_args_list = self.parallel_executor_mock.add_task.call_args_list
        self.assertEqual(len(call_args_list), 2)

        # Check first call
        first_call = call_args_list[0]
        self.assertEqual(first_call[1]["resource_requirements"][0].resource_type, ResourceType.CPU)
        self.assertEqual(first_call[1]["resource_requirements"][0].amount, 0.5)

        # Check second call
        second_call = call_args_list[1]
        self.assertEqual(second_call[1]["resource_requirements"][0].resource_type, ResourceType.MEMORY)
        self.assertEqual(second_call[1]["resource_requirements"][0].amount, 0.3)

    async def test_execute_tasks_with_circuit_breaker(self):
        """Test executing tasks with circuit breaker."""
        # Create mock tasks
        async def task_1():
            return "result1"

        # Define tasks with circuit breaker
        tasks = [
            {
                "func": task_1,
                "task_id": "task1",
                "description": "Task 1",
                "circuit_breaker_name": "test_breaker",
            },
        ]

        # Execute tasks in parallel
        results = await self.assistant.execute_tasks_in_parallel(tasks)

        # Check results
        self.assertEqual(results, {
            "task1": "result1",
            "task2": "result2",
        })

        # Check that add_task was called with circuit breaker
        call_args = self.parallel_executor_mock.add_task.call_args_list[0]
        self.assertEqual(call_args[1]["circuit_breaker_name"], "test_breaker")

    async def test_get_queue_stats_with_parallel_executor(self):
        """Test getting queue stats with parallel executor metrics."""
        # Mock the get_queue_stats function
        with patch("dukat.core.async_assistant.get_queue_stats") as mock_get_queue_stats:
            mock_get_queue_stats.return_value = {
                "active_tasks": 2,
                "completed_tasks": 5,
                "failed_tasks": 1,
            }

            # Add a circuit breaker
            self.assistant.circuit_breakers["test_breaker"] = MagicMock(spec=CircuitBreaker)
            self.assistant.circuit_breakers["test_breaker"].state = CircuitBreakerState.CLOSED
            self.assistant.circuit_breakers["test_breaker"].failure_count = 0
            self.assistant.circuit_breakers["test_breaker"].last_failure_time = 0
            self.assistant.circuit_breakers["test_breaker"].last_success_time = time.time()

            # Add response times
            self.assistant.response_times = [0.1, 0.2, 0.3]

            # Get queue stats
            stats = await self.assistant.get_queue_stats()

            # Check stats
            self.assertEqual(stats["active_tasks"], 2)
            self.assertEqual(stats["completed_tasks"], 5)
            self.assertEqual(stats["failed_tasks"], 1)

            # Check circuit breaker stats
            self.assertEqual(stats["circuit_breakers"]["test_breaker"]["state"], "closed")
            self.assertEqual(stats["circuit_breakers"]["test_breaker"]["failure_count"], 0)

            # Check response time stats
            self.assertAlmostEqual(stats["response_times"]["average"], 0.2, delta=0.001)
            self.assertEqual(stats["response_times"]["min"], 0.1)
            self.assertEqual(stats["response_times"]["max"], 0.3)
            self.assertEqual(stats["response_times"]["count"], 3)

            # Check parallel executor metrics
            self.assertEqual(stats["parallel_executor"]["total_tasks"], 2)
            self.assertEqual(stats["parallel_executor"]["completed_tasks"], 2)


class TestAsyncAssistantScheduling(unittest.IsolatedAsyncioTestCase):
    """Tests for AsyncAssistant task scheduling capabilities."""

    async def asyncSetUp(self):
        """Set up the test environment."""
        # Create an AsyncAssistant with mocked components
        self.assistant = AsyncAssistant(
            model_name="test_model",
            ollama_host="http://localhost:11434",
            max_messages=100,
            conversation_id="test_conversation",
            max_parallel_tasks=3,
        )

        # Mock the schedule_task function
        self.schedule_task_patch = patch("dukat.core.async_assistant.schedule_task")
        self.mock_schedule_task = self.schedule_task_patch.start()
        self.mock_schedule_task.return_value = "scheduled_task_id"

        # Mock the cancel_scheduled_task function
        self.cancel_task_patch = patch("dukat.core.async_assistant.cancel_scheduled_task")
        self.mock_cancel_task = self.cancel_task_patch.start()
        self.mock_cancel_task.return_value = True

    async def asyncTearDown(self):
        """Clean up after tests."""
        self.schedule_task_patch.stop()
        self.cancel_task_patch.stop()

    async def test_schedule_periodic_task(self):
        """Test scheduling a periodic task."""
        # Create a mock function
        async def mock_func(arg1, arg2=None):
            return f"{arg1} {arg2}"

        # Schedule a periodic task
        task_id = await self.assistant.schedule_periodic_task(
            func=mock_func,
            interval=10.0,
            args=["arg1"],
            kwargs={"arg2": "arg2"},
            task_id="periodic_task",
            max_runs=5,
            priority=2,
            timeout=30.0,
            retry_count=3,
            retry_delay=2.0,
            description="Periodic test task",
            task_type="test_periodic_task",
        )

        # Check task ID
        self.assertEqual(task_id, "scheduled_task_id")

        # Check that schedule_task was called with the correct arguments
        self.mock_schedule_task.assert_called_once()
        call_args = self.mock_schedule_task.call_args[1]
        self.assertEqual(call_args["func"], mock_func)
        self.assertEqual(call_args["args"], ["arg1"])
        self.assertEqual(call_args["kwargs"], {"arg2": "arg2"})
        self.assertEqual(call_args["task_id"], "periodic_task")
        self.assertEqual(call_args["interval"], 10.0)
        self.assertEqual(call_args["max_runs"], 5)
        self.assertEqual(call_args["priority"], 2)
        self.assertEqual(call_args["timeout"], 30.0)
        self.assertEqual(call_args["retry_count"], 3)
        self.assertEqual(call_args["retry_delay"], 2.0)
        self.assertEqual(call_args["description"], "Periodic test task")

        # Check that the task is tracked
        self.assertEqual(self.assistant.scheduled_tasks[task_id], "test_periodic_task")

    async def test_schedule_task_at_time(self):
        """Test scheduling a task at a specific time."""
        # Create a mock function
        def mock_func():
            return "result"

        # Schedule a task at a specific time
        future_time = datetime.now() + timedelta(minutes=5)
        task_id = await self.assistant.schedule_task_at_time(
            func=mock_func,
            schedule_time=future_time,
            task_id="time_task",
            priority=1,
            description="Time-based test task",
            task_type="test_time_task",
        )

        # Check task ID
        self.assertEqual(task_id, "scheduled_task_id")

        # Check that schedule_task was called with the correct arguments
        self.mock_schedule_task.assert_called_once()
        call_args = self.mock_schedule_task.call_args[1]
        self.assertEqual(call_args["func"], mock_func)
        self.assertEqual(call_args["task_id"], "time_task")
        self.assertEqual(call_args["schedule_time"], future_time)
        self.assertEqual(call_args["priority"], 1)
        self.assertEqual(call_args["description"], "Time-based test task")

        # Check that the task is tracked
        self.assertEqual(self.assistant.scheduled_tasks[task_id], "test_time_task")

    async def test_cancel_scheduled_task(self):
        """Test cancelling a scheduled task."""
        # Add a task to the tracking dict
        self.assistant.scheduled_tasks["task_to_cancel"] = "test_task"

        # Cancel the task
        cancelled = await self.assistant.cancel_scheduled_task("task_to_cancel")

        # Check result
        self.assertTrue(cancelled)

        # Check that cancel_scheduled_task was called
        self.mock_cancel_task.assert_called_once_with("task_to_cancel")

        # Check that the task was removed from tracking
        self.assertNotIn("task_to_cancel", self.assistant.scheduled_tasks)

    async def test_cancel_nonexistent_task(self):
        """Test cancelling a non-existent task."""
        # Set up the mock to return False
        self.mock_cancel_task.return_value = False

        # Try to cancel a non-existent task
        cancelled = await self.assistant.cancel_scheduled_task("nonexistent_task")

        # Check result
        self.assertFalse(cancelled)

        # Check that cancel_scheduled_task was called
        self.mock_cancel_task.assert_called_once_with("nonexistent_task")


class TestGetAsyncAssistant(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_async_assistant function with parallel execution."""

    async def test_get_async_assistant_with_parallel(self):
        """Test getting an async assistant with parallel execution."""
        # Mock the AsyncAssistant class
        with patch("dukat.core.async_assistant.AsyncAssistant") as mock_assistant_class:
            # Create a mock instance
            mock_assistant = MagicMock()
            mock_assistant_class.return_value = mock_assistant

            # Call get_async_assistant
            assistant = await get_async_assistant(
                model_name="test_model",
                ollama_host="http://localhost:11434",
                max_messages=100,
                conversation_id="test_conversation",
                max_parallel_tasks=5,
            )

            # Check that AsyncAssistant was called with the correct arguments
            mock_assistant_class.assert_called_once_with(
                model_name="test_model",
                ollama_host="http://localhost:11434",
                max_messages=100,
                conversation_id="test_conversation",
                max_parallel_tasks=5,
            )

            # Check that the returned assistant is the mock
            self.assertEqual(assistant, mock_assistant)


if __name__ == "__main__":
    unittest.main()
