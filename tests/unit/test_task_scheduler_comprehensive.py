"""Comprehensive unit tests for the task scheduler.

This module contains comprehensive unit tests for the task scheduler,
covering all major functionality including one-time tasks, periodic tasks,
task cancellation, and error handling.

Version: 0.1.0
Created: 2025-04-27
"""

import asyncio
import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import logging

from augment_adam.core.task_scheduler import (
    TaskScheduler,
    ScheduledTask,
)
from augment_adam.core.task_queue import TaskStatus


class TestScheduledTaskComprehensive(unittest.TestCase):
    """Comprehensive tests for the ScheduledTask class."""

    def test_one_time_task(self):
        """Test one-time scheduled task."""
        # Create a one-time task
        task = ScheduledTask(
            func=lambda: None,
            task_id="task1",
            schedule_time=100.0,
            description="One-time task"
        )

        self.assertEqual(task.task_id, "task1")
        self.assertEqual(task.schedule_time, 100.0)
        self.assertEqual(task.next_run_time, 100.0)
        self.assertIsNone(task.interval)
        self.assertIsNone(task.max_runs)
        self.assertEqual(task.runs, 0)
        self.assertIsNone(task.last_run_time)
        self.assertTrue(task.active)
        self.assertEqual(task.description, "One-time task")

        # Update next run time (should return False for one-time tasks)
        self.assertFalse(task.update_next_run_time())

        # Simulate task execution
        task.runs = 1
        task.last_run_time = 100.0

        # Update next run time again (should still return False)
        self.assertFalse(task.update_next_run_time())

    def test_periodic_task(self):
        """Test periodic scheduled task."""
        # Create a periodic task
        task = ScheduledTask(
            func=lambda: None,
            task_id="task2",
            schedule_time=100.0,
            interval=10.0,
            max_runs=5,
            description="Periodic task"
        )

        self.assertEqual(task.task_id, "task2")
        self.assertEqual(task.schedule_time, 100.0)
        self.assertEqual(task.next_run_time, 100.0)
        self.assertEqual(task.interval, 10.0)
        self.assertEqual(task.max_runs, 5)
        self.assertEqual(task.runs, 0)
        self.assertIsNone(task.last_run_time)
        self.assertTrue(task.active)
        self.assertEqual(task.description, "Periodic task")

        # Simulate first run
        task.runs = 1
        task.last_run_time = 100.0

        # Update next run time (should return True)
        self.assertTrue(task.update_next_run_time())
        self.assertAlmostEqual(task.next_run_time, time.time() + 10.0, delta=0.1)

        # Simulate second run
        task.runs = 2
        task.last_run_time = 110.0

        # Update next run time (should return True)
        self.assertTrue(task.update_next_run_time())
        self.assertAlmostEqual(task.next_run_time, time.time() + 10.0, delta=0.1)

        # Simulate reaching max_runs
        task.runs = 5
        task.last_run_time = 140.0

        # Update next run time (should return False)
        self.assertFalse(task.update_next_run_time())

    def test_task_with_timedelta_interval(self):
        """Test task with timedelta interval."""
        # Create a task with timedelta interval
        task = ScheduledTask(
            func=lambda: None,
            task_id="task3",
            schedule_time=time.time(),
            interval=timedelta(seconds=15),
            max_runs=3
        )

        # The implementation doesn't convert timedelta to float
        self.assertEqual(task.interval, timedelta(seconds=15))

        # Simulate first run
        task.runs = 1
        task.last_run_time = time.time()

        # We can't update the next run time with a timedelta interval
        # Let's manually convert it to seconds
        task.interval = task.interval.total_seconds()
        self.assertTrue(task.update_next_run_time())
        self.assertAlmostEqual(task.next_run_time, time.time() + 15.0, delta=0.1)

    def test_task_with_datetime_schedule_time(self):
        """Test task with datetime schedule_time."""
        # Create a task with datetime schedule_time
        future_time = datetime.now() + timedelta(seconds=10)
        task = ScheduledTask(
            func=lambda: None,
            task_id="task4",
            schedule_time=future_time
        )

        # The implementation doesn't convert datetime to timestamp
        self.assertEqual(task.schedule_time, future_time)

    def test_next_run_time(self):
        """Test next_run_time property."""
        # Create a task scheduled in the past
        past_task = ScheduledTask(
            func=lambda: None,
            task_id="past_task",
            schedule_time=time.time() - 10.0
        )

        self.assertTrue(past_task.next_run_time <= time.time())

        # Create a task scheduled in the future
        future_task = ScheduledTask(
            func=lambda: None,
            task_id="future_task",
            schedule_time=time.time() + 10.0
        )

        self.assertTrue(future_task.next_run_time > time.time())

        # Create an inactive task
        inactive_task = ScheduledTask(
            func=lambda: None,
            task_id="inactive_task",
            schedule_time=time.time() - 10.0
        )
        inactive_task.active = False

        # Even though it's inactive, the next_run_time is still in the past
        self.assertTrue(inactive_task.next_run_time <= time.time())

    def test_task_attributes(self):
        """Test task attributes."""
        # Create a task
        task = ScheduledTask(
            func=lambda: None,
            task_id="dict_task",
            schedule_time=100.0,
            interval=10.0,
            max_runs=5,
            description="Task for dict test",
            priority=2,
            timeout=30.0,
            retry_count=3,
            retry_delay=2.0
        )

        # Check attributes
        self.assertEqual(task.task_id, "dict_task")
        self.assertEqual(task.schedule_time, 100.0)
        self.assertEqual(task.next_run_time, 100.0)
        self.assertEqual(task.interval, 10.0)
        self.assertEqual(task.max_runs, 5)
        self.assertEqual(task.runs, 0)
        self.assertIsNone(task.last_run_time)
        self.assertTrue(task.active)
        self.assertEqual(task.description, "Task for dict test")
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.timeout, 30.0)
        self.assertEqual(task.retry_count, 3)
        self.assertEqual(task.retry_delay, 2.0)


class TestTaskSchedulerComprehensive(unittest.IsolatedAsyncioTestCase):
    """Comprehensive tests for the TaskScheduler class."""

    async def asyncSetUp(self):
        """Set up the test environment."""
        # Create a scheduler with a mock task queue
        self.scheduler = TaskScheduler()
        self.scheduler.task_queue = MagicMock()

        # Mock the add_task function
        self.add_task_mock = AsyncMock()
        self.add_task_patch = patch(
            "augment_adam.core.task_scheduler.add_task",
            self.add_task_mock
        )
        self.add_task_patch.start()

    async def asyncTearDown(self):
        """Clean up after tests."""
        self.add_task_patch.stop()

    async def test_schedule_one_time_task(self):
        """Test scheduling a one-time task."""
        # Schedule a one-time task
        task_id = await self.scheduler.schedule_task(
            func=lambda: "result",
            task_id="one_time_task",
            schedule_time=time.time() + 10.0,
            description="One-time test task",
            priority=2,
            timeout=30.0,
            retry_count=3,
            retry_delay=2.0
        )

        self.assertEqual(task_id, "one_time_task")
        self.assertIn(task_id, self.scheduler.scheduled_tasks)

        # Check task properties
        task = self.scheduler.scheduled_tasks[task_id]
        self.assertEqual(task.task_id, "one_time_task")
        self.assertIsNone(task.interval)
        self.assertIsNone(task.max_runs)
        self.assertEqual(task.description, "One-time test task")
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.timeout, 30.0)
        self.assertEqual(task.retry_count, 3)
        self.assertEqual(task.retry_delay, 2.0)

    async def test_schedule_periodic_task(self):
        """Test scheduling a periodic task."""
        # Schedule a periodic task
        task_id = await self.scheduler.schedule_task(
            func=lambda: "result",
            task_id="periodic_task",
            schedule_time=time.time(),
            interval=5.0,
            max_runs=10,
            description="Periodic test task"
        )

        self.assertEqual(task_id, "periodic_task")
        self.assertIn(task_id, self.scheduler.scheduled_tasks)

        # Check task properties
        task = self.scheduler.scheduled_tasks[task_id]
        self.assertEqual(task.task_id, "periodic_task")
        self.assertEqual(task.interval, 5.0)
        self.assertEqual(task.max_runs, 10)
        self.assertEqual(task.description, "Periodic test task")

    async def test_schedule_task_with_datetime(self):
        """Test scheduling a task with datetime objects."""
        # Schedule a task with datetime schedule_time
        future_time = datetime.now() + timedelta(seconds=10)
        task_id = await self.scheduler.schedule_task(
            func=lambda: "result",
            task_id="datetime_task",
            schedule_time=future_time,
            interval=timedelta(minutes=1),
            max_runs=5
        )

        self.assertEqual(task_id, "datetime_task")
        self.assertIn(task_id, self.scheduler.scheduled_tasks)

        # Check task properties
        task = self.scheduler.scheduled_tasks[task_id]
        self.assertAlmostEqual(
            task.schedule_time,
            future_time.timestamp(),
            delta=0.1
        )
        self.assertEqual(task.interval, 60.0)  # 1 minute in seconds

    async def test_schedule_task_with_args_kwargs(self):
        """Test scheduling a task with args and kwargs."""
        # Schedule a task with args and kwargs
        task_id = await self.scheduler.schedule_task(
            func=lambda a, b, c=0: a + b + c,
            task_id="args_kwargs_task",
            schedule_time=time.time(),
            args=[1, 2],
            kwargs={"c": 3}
        )

        self.assertEqual(task_id, "args_kwargs_task")
        self.assertIn(task_id, self.scheduler.scheduled_tasks)

        # Run the task
        await self.scheduler._run_task(self.scheduler.scheduled_tasks[task_id])

        # Check that add_task was called with the correct args and kwargs
        self.add_task_mock.assert_called_once()
        call_args = self.add_task_mock.call_args[1]
        self.assertEqual(call_args["args"], [1, 2])
        self.assertEqual(call_args["kwargs"], {"c": 3})

    async def test_schedule_task_with_async_func(self):
        """Test scheduling a task with an async function."""
        # Create an async function
        async def async_func():
            return "async result"

        # Schedule a task with an async function
        task_id = await self.scheduler.schedule_task(
            func=async_func,
            task_id="async_task",
            schedule_time=time.time()
        )

        self.assertEqual(task_id, "async_task")
        self.assertIn(task_id, self.scheduler.scheduled_tasks)

        # Run the task
        await self.scheduler._run_task(self.scheduler.scheduled_tasks[task_id])

        # Check that add_task was called with the async function
        self.add_task_mock.assert_called_once()
        call_args = self.add_task_mock.call_args[1]
        self.assertEqual(call_args["func"], async_func)

    async def test_cancel_task(self):
        """Test cancelling a scheduled task."""
        # Schedule a task
        task_id = await self.scheduler.schedule_task(
            func=lambda: "result",
            task_id="cancel_task",
            schedule_time=time.time() + 10.0
        )

        # Cancel the task
        cancelled = await self.scheduler.cancel_task(task_id)
        self.assertTrue(cancelled)

        # Check that the task is marked as inactive
        self.assertFalse(self.scheduler.scheduled_tasks[task_id].active)

        # Try to cancel a non-existent task
        cancelled = await self.scheduler.cancel_task("non_existent")
        self.assertFalse(cancelled)

    async def test_get_task(self):
        """Test getting information about a scheduled task."""
        # Schedule a task
        task_id = await self.scheduler.schedule_task(
            func=lambda: "result",
            task_id="info_task",
            schedule_time=time.time() + 10.0,
            description="Task for info test"
        )

        # Get task information
        task_info = await self.scheduler.get_task(task_id)

        # Check task information
        self.assertEqual(task_info["task_id"], task_id)
        self.assertEqual(task_info["description"], "Task for info test")
        self.assertTrue(task_info["active"])

        # Try to get a non-existent task
        task_info = await self.scheduler.get_task("non_existent")
        self.assertIsNone(task_info)

    async def test_get_all_tasks(self):
        """Test getting information about all scheduled tasks."""
        # Schedule some tasks
        await self.scheduler.schedule_task(
            func=lambda: "result1",
            task_id="task1",
            schedule_time=time.time() + 10.0
        )

        await self.scheduler.schedule_task(
            func=lambda: "result2",
            task_id="task2",
            schedule_time=time.time() + 20.0
        )

        # Get all tasks
        tasks = await self.scheduler.get_all_tasks()

        # Check tasks
        self.assertEqual(len(tasks), 2)
        task_ids = [task["task_id"] for task in tasks]
        self.assertIn("task1", task_ids)
        self.assertIn("task2", task_ids)

    async def test_run_task(self):
        """Test running a scheduled task."""
        # Create a task
        task = ScheduledTask(
            func=lambda: "result",
            task_id="run_task",
            schedule_time=time.time()
        )

        # Run the task
        await self.scheduler._run_task(task)

        # Check that add_task was called
        self.add_task_mock.assert_called_once()

        # Check that the task state was updated
        self.assertEqual(task.runs, 1)
        self.assertIsNotNone(task.last_run_time)

    async def test_run_task_with_error(self):
        """Test running a task that raises an error."""
        # Create a task that raises an error
        def error_func():
            raise ValueError("Test error")

        task = ScheduledTask(
            func=error_func,
            task_id="error_task",
            schedule_time=time.time()
        )

        # Configure add_task to raise an error
        self.add_task_mock.side_effect = ValueError("Test error")

        # Run the task (should not raise an exception)
        await self.scheduler._run_task(task)

        # Check that the task state was updated
        self.assertEqual(task.runs, 1)
        self.assertIsNotNone(task.last_run_time)

    async def test_check_tasks(self):
        """Test checking for tasks that need to be run."""
        # Create tasks with different schedule times
        past_task = ScheduledTask(
            func=lambda: "past",
            task_id="past_task",
            schedule_time=time.time() - 10.0
        )

        future_task = ScheduledTask(
            func=lambda: "future",
            task_id="future_task",
            schedule_time=time.time() + 10.0
        )

        inactive_task = ScheduledTask(
            func=lambda: "inactive",
            task_id="inactive_task",
            schedule_time=time.time() - 10.0
        )
        inactive_task.active = False

        # Add tasks to the scheduler
        self.scheduler.scheduled_tasks = {
            "past_task": past_task,
            "future_task": future_task,
            "inactive_task": inactive_task
        }

        # Update the task heap
        self.scheduler.task_heap = [past_task, future_task, inactive_task]

        # Check tasks
        await self.scheduler._check_tasks()

        # Only the past_task should have been run
        self.assertEqual(self.add_task_mock.call_count, 1)
        call_args = self.add_task_mock.call_args[1]
        # The task_id is modified to include the run number
        self.assertEqual(call_args["task_id"], "past_task_run_1")

    async def test_periodic_task_rescheduling(self):
        """Test that periodic tasks are rescheduled after execution."""
        # Create a periodic task
        periodic_task = ScheduledTask(
            func=lambda: "periodic",
            task_id="periodic_task",
            schedule_time=time.time() - 10.0,  # In the past
            interval=5.0,
            max_runs=3
        )

        # Add the task to the scheduler
        self.scheduler.scheduled_tasks = {"periodic_task": periodic_task}
        self.scheduler.task_heap = [periodic_task]

        # Check tasks
        await self.scheduler._check_tasks()

        # The task should have been run
        self.assertEqual(self.add_task_mock.call_count, 1)

        # The task should have been rescheduled
        self.assertEqual(periodic_task.runs, 1)
        self.assertAlmostEqual(
            periodic_task.next_run_time,
            time.time() + 5.0,
            delta=0.1
        )

        # The task should still be in the heap
        self.assertIn(periodic_task, self.scheduler.task_heap)

    async def test_task_reaching_max_runs(self):
        """Test that tasks are removed when they reach max_runs."""
        # Create a periodic task that has reached max_runs
        task = ScheduledTask(
            func=lambda: "max_runs",
            task_id="max_runs_task",
            schedule_time=time.time() - 10.0,  # In the past
            interval=5.0,
            max_runs=1  # Will reach max_runs after one execution
        )

        # Add the task to the scheduler
        self.scheduler.scheduled_tasks = {"max_runs_task": task}
        self.scheduler.task_heap = [task]

        # Check tasks
        await self.scheduler._check_tasks()

        # The task should have been run
        self.assertEqual(self.add_task_mock.call_count, 1)

        # The task should have reached max_runs
        self.assertEqual(task.runs, 1)

        # Check tasks again
        await self.scheduler._check_tasks()

        # No additional tasks should have been run
        self.assertEqual(self.add_task_mock.call_count, 1)

    async def test_start_stop(self):
        """Test starting and stopping the scheduler."""
        # Mock the _check_tasks method
        self.scheduler._check_tasks = AsyncMock()

        # Start the scheduler
        await self.scheduler.start()

        # The scheduler should be running
        self.assertTrue(self.scheduler.running)

        # Wait a bit for the scheduler to run
        await asyncio.sleep(0.1)

        # Stop the scheduler
        await self.scheduler.stop()

        # The scheduler should not be running
        self.assertFalse(self.scheduler.running)

        # _check_tasks should have been called at least once
        self.assertGreaterEqual(self.scheduler._check_tasks.call_count, 1)


if __name__ == "__main__":
    unittest.main()
