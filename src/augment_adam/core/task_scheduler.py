"""Task scheduler for Augment Adam.

This module provides functionality for scheduling tasks to run at specific times.
"""

import asyncio
import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from datetime import datetime, timedelta

from augment_adam.core.task_queue import add_task, Task

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Scheduled task class for Augment Adam.

    This class represents a task scheduled to run at a specific time or interval.
    """

    def __init__(
        self,
        func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        schedule_time: Optional[Union[float, datetime]] = None,
        interval: Optional[Union[float, timedelta]] = None,
        max_runs: Optional[int] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        description: str = "",
    ):
        """Initialize the scheduled task.

        Args:
            func: The function to execute.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            schedule_time: The time to run the task.
            interval: The interval between runs.
            max_runs: Maximum number of times to run the task.
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            description: Description of the task.
        """
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.task_id = task_id or f"scheduled_{uuid.uuid4().hex[:8]}"
        self.schedule_time = schedule_time
        self.interval = interval
        self.max_runs = max_runs
        self.priority = priority
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.description = description

        self.created_at = time.time()
        self.last_run_at = None
        self.next_run_at = None
        self.run_count = 0
        self.cancelled = False
        self.timer_handle = None

        # Calculate next run time
        self._calculate_next_run()

    def _calculate_next_run(self) -> None:
        """Calculate the next run time."""
        if self.cancelled:
            self.next_run_at = None
            return

        if self.schedule_time is not None and self.last_run_at is None:
            # One-time scheduled task
            if isinstance(self.schedule_time, datetime):
                self.next_run_at = self.schedule_time.timestamp()
            else:
                self.next_run_at = self.schedule_time
        elif self.interval is not None:
            # Periodic task
            if self.max_runs is not None and self.run_count >= self.max_runs:
                self.next_run_at = None
                return

            if self.last_run_at is None:
                # First run
                if isinstance(self.interval, timedelta):
                    self.next_run_at = time.time() + self.interval.total_seconds()
                else:
                    self.next_run_at = time.time() + self.interval
            else:
                # Subsequent runs
                if isinstance(self.interval, timedelta):
                    self.next_run_at = self.last_run_at + self.interval.total_seconds()
                else:
                    self.next_run_at = self.last_run_at + self.interval
        else:
            self.next_run_at = None


# Global dictionary of scheduled tasks
_scheduled_tasks: Dict[str, ScheduledTask] = {}


async def _run_scheduled_task(task: ScheduledTask) -> None:
    """Run a scheduled task.

    Args:
        task: The task to run.
    """
    # Update task state
    task.last_run_at = time.time()
    task.run_count += 1

    # Add the task to the queue
    await add_task(
        func=task.func,
        args=task.args,
        kwargs=task.kwargs,
        task_id=f"{task.task_id}_run_{task.run_count}",
        priority=task.priority,
        timeout=task.timeout,
        retry_count=task.retry_count,
        retry_delay=task.retry_delay,
        description=task.description,
    )

    # Calculate next run time
    task._calculate_next_run()

    # Schedule next run if needed
    if task.next_run_at is not None:
        delay = max(0, task.next_run_at - time.time())
        loop = asyncio.get_event_loop()
        task.timer_handle = loop.call_later(delay, lambda: asyncio.create_task(_run_scheduled_task(task)))


async def schedule_task(
    func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None,
    task_id: Optional[str] = None,
    schedule_time: Optional[Union[float, datetime]] = None,
    interval: Optional[Union[float, timedelta]] = None,
    max_runs: Optional[int] = None,
    priority: int = 0,
    timeout: Optional[float] = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    description: str = "",
) -> str:
    """Schedule a task to run at a specific time or interval.

    Args:
        func: The function to execute.
        args: Positional arguments to pass to the function.
        kwargs: Keyword arguments to pass to the function.
        task_id: A unique identifier for the task. If not provided, a UUID will be generated.
        schedule_time: The time to run the task.
        interval: The interval between runs.
        max_runs: Maximum number of times to run the task.
        priority: The priority of the task. Higher values indicate higher priority.
        timeout: Maximum time in seconds to wait for the task to complete.
        retry_count: Number of times to retry the task if it fails.
        retry_delay: Delay in seconds between retries.
        description: Description of the task.

    Returns:
        The ID of the scheduled task.

    Raises:
        ValueError: If neither schedule_time nor interval is provided.
    """
    if schedule_time is None and interval is None:
        raise ValueError("Either schedule_time or interval must be provided")

    # Create the task
    task = ScheduledTask(
        func=func,
        args=args,
        kwargs=kwargs,
        task_id=task_id,
        schedule_time=schedule_time,
        interval=interval,
        max_runs=max_runs,
        priority=priority,
        timeout=timeout,
        retry_count=retry_count,
        retry_delay=retry_delay,
        description=description,
    )

    # Add the task to the dictionary
    _scheduled_tasks[task.task_id] = task

    # Schedule the task
    if task.next_run_at is not None:
        delay = max(0, task.next_run_at - time.time())
        loop = asyncio.get_event_loop()
        task.timer_handle = loop.call_later(delay, lambda: asyncio.create_task(_run_scheduled_task(task)))

    logger.info(f"Scheduled task {task.task_id}")
    return task.task_id


async def cancel_scheduled_task(task_id: str) -> bool:
    """Cancel a scheduled task.

    Args:
        task_id: The ID of the task to cancel.

    Returns:
        True if the task was cancelled, False otherwise.
    """
    task = _scheduled_tasks.get(task_id)
    if not task:
        return False

    # Cancel the timer
    if task.timer_handle:
        task.timer_handle.cancel()

    # Update task state
    task.cancelled = True
    task.next_run_at = None

    # Remove the task from the dictionary
    del _scheduled_tasks[task_id]

    logger.info(f"Cancelled scheduled task {task_id}")
    return True


async def get_scheduled_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Get a scheduled task by ID.

    Args:
        task_id: The ID of the task to get.

    Returns:
        Information about the task, or None if not found.
    """
    task = _scheduled_tasks.get(task_id)
    if not task:
        return None

    return {
        "task_id": task.task_id,
        "created_at": task.created_at,
        "last_run_at": task.last_run_at,
        "next_run_at": task.next_run_at,
        "run_count": task.run_count,
        "cancelled": task.cancelled,
        "description": task.description,
    }


async def get_all_scheduled_tasks() -> Dict[str, Dict[str, Any]]:
    """Get all scheduled tasks.

    Returns:
        A dictionary mapping task IDs to task information.
    """
    result = {}
    for task_id, task in _scheduled_tasks.items():
        result[task_id] = {
            "task_id": task.task_id,
            "created_at": task.created_at,
            "last_run_at": task.last_run_at,
            "next_run_at": task.next_run_at,
            "run_count": task.run_count,
            "cancelled": task.cancelled,
            "description": task.description,
        }
    return result
