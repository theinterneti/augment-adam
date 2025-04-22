"""Unit tests for the task scheduler.

This module contains unit tests for the task scheduler.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from dukat.core.task_scheduler import (
    TaskScheduler,
    ScheduledTask,
)


class TestScheduledTask(unittest.TestCase):
    """Tests for the ScheduledTask class."""
    
    def test_init(self):
        """Test initializing a scheduled task."""
        # Create a one-time task
        task = ScheduledTask(
            func=lambda: None,
            task_id="task1",
            schedule_time=100.0,
        )
        
        self.assertEqual(task.task_id, "task1")
        self.assertEqual(task.schedule_time, 100.0)
        self.assertEqual(task.next_run_time, 100.0)
        self.assertIsNone(task.interval)
        self.assertIsNone(task.max_runs)
        self.assertEqual(task.runs, 0)
        self.assertIsNone(task.last_run_time)
        self.assertTrue(task.active)
        
        # Create a periodic task
        task = ScheduledTask(
            func=lambda: None,
            task_id="task2",
            schedule_time=100.0,
            interval=10.0,
            max_runs=5,
        )
        
        self.assertEqual(task.task_id, "task2")
        self.assertEqual(task.schedule_time, 100.0)
        self.assertEqual(task.next_run_time, 100.0)
        self.assertEqual(task.interval, 10.0)
        self.assertEqual(task.max_runs, 5)
    
    def test_update_next_run_time(self):
        """Test updating the next run time."""
        # One-time task
        task = ScheduledTask(
            func=lambda: None,
            task_id="task1",
            schedule_time=100.0,
        )
        
        # Should return False for one-time tasks
        self.assertFalse(task.update_next_run_time())
        
        # Periodic task
        task = ScheduledTask(
            func=lambda: None,
            task_id="task2",
            schedule_time=100.0,
            interval=10.0,
            max_runs=2,
        )
        
        # First run
        task.runs = 1
        task.last_run_time = 100.0
        
        # Should return True and update next_run_time
        self.assertTrue(task.update_next_run_time())
        self.assertAlmostEqual(task.next_run_time, time.time() + 10.0, delta=0.1)
        
        # Second run
        task.runs = 2
        task.last_run_time = 110.0
        
        # Should return False because max_runs is reached
        self.assertFalse(task.update_next_run_time())


class TestTaskScheduler(unittest.IsolatedAsyncioTestCase):
    """Tests for the TaskScheduler class."""
    
    async def test_schedule_task(self):
        """Test scheduling a task."""
        scheduler = TaskScheduler()
        
        # Mock the task queue
        scheduler.task_queue = MagicMock()
        
        # Schedule a one-time task
        task_id = await scheduler.schedule_task(
            func=lambda: "result",
            task_id="task1",
            schedule_time=time.time() + 10.0,
        )
        
        self.assertEqual(task_id, "task1")
        self.assertIn(task_id, scheduler.scheduled_tasks)
        
        # Schedule a periodic task
        task_id = await scheduler.schedule_task(
            func=lambda: "result",
            task_id="task2",
            schedule_time=time.time(),
            interval=5.0,
            max_runs=3,
        )
        
        self.assertEqual(task_id, "task2")
        self.assertIn(task_id, scheduler.scheduled_tasks)
    
    async def test_cancel_task(self):
        """Test cancelling a scheduled task."""
        scheduler = TaskScheduler()
        
        # Mock the task queue
        scheduler.task_queue = MagicMock()
        
        # Schedule a task
        task_id = await scheduler.schedule_task(
            func=lambda: "result",
            task_id="task1",
            schedule_time=time.time() + 10.0,
        )
        
        # Cancel the task
        cancelled = await scheduler.cancel_task(task_id)
        self.assertTrue(cancelled)
        self.assertFalse(scheduler.scheduled_tasks[task_id].active)
        
        # Try to cancel a non-existent task
        cancelled = await scheduler.cancel_task("non_existent")
        self.assertFalse(cancelled)
    
    async def test_get_task(self):
        """Test getting information about a scheduled task."""
        scheduler = TaskScheduler()
        
        # Mock the task queue
        scheduler.task_queue = MagicMock()
        
        # Schedule a task
        task_id = await scheduler.schedule_task(
            func=lambda: "result",
            task_id="task1",
            schedule_time=time.time() + 10.0,
            description="Test task",
        )
        
        # Get task information
        task_info = await scheduler.get_task(task_id)
        
        self.assertEqual(task_info["task_id"], task_id)
        self.assertEqual(task_info["description"], "Test task")
        self.assertTrue(task_info["active"])
        
        # Try to get a non-existent task
        task_info = await scheduler.get_task("non_existent")
        self.assertIsNone(task_info)
    
    async def test_get_all_tasks(self):
        """Test getting information about all scheduled tasks."""
        scheduler = TaskScheduler()
        
        # Mock the task queue
        scheduler.task_queue = MagicMock()
        
        # Schedule some tasks
        await scheduler.schedule_task(
            func=lambda: "result1",
            task_id="task1",
            schedule_time=time.time() + 10.0,
        )
        
        await scheduler.schedule_task(
            func=lambda: "result2",
            task_id="task2",
            schedule_time=time.time() + 20.0,
        )
        
        # Get all tasks
        tasks = await scheduler.get_all_tasks()
        
        self.assertEqual(len(tasks), 2)
        task_ids = [task["task_id"] for task in tasks]
        self.assertIn("task1", task_ids)
        self.assertIn("task2", task_ids)
    
    @patch("dukat.core.task_scheduler.add_task")
    async def test_run_task(self, mock_add_task):
        """Test running a scheduled task."""
        scheduler = TaskScheduler()
        
        # Mock the task queue
        scheduler.task_queue = MagicMock()
        
        # Mock add_task
        mock_add_task.return_value = MagicMock()
        
        # Create a scheduled task
        task = ScheduledTask(
            func=lambda: "result",
            task_id="task1",
            schedule_time=time.time(),
            description="Test task",
        )
        
        # Run the task
        await scheduler._run_task(task)
        
        # Check that add_task was called
        mock_add_task.assert_called_once()
        
        # Check that the task state was updated
        self.assertEqual(task.runs, 1)
        self.assertIsNotNone(task.last_run_time)
    
    @patch("dukat.core.task_scheduler.add_task")
    async def test_check_tasks(self, mock_add_task):
        """Test checking for tasks that need to be run."""
        scheduler = TaskScheduler()
        
        # Mock the task queue
        scheduler.task_queue = MagicMock()
        
        # Mock add_task
        mock_add_task.return_value = MagicMock()
        
        # Schedule a task that should run immediately
        now = time.time()
        task = ScheduledTask(
            func=lambda: "result",
            task_id="task1",
            schedule_time=now - 1.0,  # In the past
        )
        
        # Add the task to the scheduler
        scheduler.scheduled_tasks[task.task_id] = task
        scheduler.task_heap = [task]
        
        # Check tasks
        await scheduler._check_tasks()
        
        # Check that add_task was called
        mock_add_task.assert_called_once()


if __name__ == "__main__":
    unittest.main()
