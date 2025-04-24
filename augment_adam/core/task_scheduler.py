"""Task scheduling for Dukat.

This module provides a task scheduler that can schedule tasks to run
at specific times or at regular intervals.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import logging
import time
import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional, Union, Callable, Awaitable, Tuple

from dukat.core.task_queue import Task, TaskQueue, TaskStatus, add_task

logger = logging.getLogger(__name__)


class ScheduledTask:
    """A task scheduled to run at a specific time or interval."""
    
    def __init__(
        self,
        func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        schedule_time: Optional[float] = None,
        interval: Optional[float] = None,
        max_runs: Optional[int] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        description: str = "",
    ):
        """Initialize a scheduled task.
        
        Args:
            func: The function to execute.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            schedule_time: The time to run the task (Unix timestamp).
                If None, the task will run as soon as possible.
            interval: The interval in seconds between runs for periodic tasks.
                If None, the task will run only once.
            max_runs: Maximum number of times to run the task.
                If None, the task will run indefinitely (for periodic tasks).
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            description: Description of the task.
        """
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.task_id = task_id
        self.schedule_time = schedule_time or time.time()
        self.interval = interval
        self.max_runs = max_runs
        self.priority = priority
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.description = description
        
        self.runs = 0
        self.last_run_time = None
        self.next_run_time = self.schedule_time
        self.active = True
    
    def __lt__(self, other):
        """Compare tasks by next run time for the priority queue."""
        if not isinstance(other, ScheduledTask):
            return NotImplemented
        return self.next_run_time < other.next_run_time
    
    def update_next_run_time(self) -> bool:
        """Update the next run time for a periodic task.
        
        Returns:
            True if the task should run again, False otherwise.
        """
        if not self.interval:
            # One-time task
            return False
        
        if self.max_runs and self.runs >= self.max_runs:
            # Reached maximum number of runs
            return False
        
        # Update next run time
        self.next_run_time = time.time() + self.interval
        return True


class TaskScheduler:
    """Scheduler for running tasks at specific times or intervals."""
    
    def __init__(
        self,
        task_queue: Optional[TaskQueue] = None,
        check_interval: float = 1.0,
    ):
        """Initialize the task scheduler.
        
        Args:
            task_queue: The task queue to use. If None, the default queue will be used.
            check_interval: Interval in seconds to check for tasks to run.
        """
        self.task_queue = task_queue
        self.check_interval = check_interval
        
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.task_heap = []
        self.running = False
        self.scheduler_task = None
        self.lock = asyncio.Lock()
    
    async def start(self) -> None:
        """Start the task scheduler."""
        if self.running:
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Task scheduler started")
    
    async def stop(self) -> None:
        """Stop the task scheduler."""
        if not self.running:
            return
        
        self.running = False
        
        if self.scheduler_task and not self.scheduler_task.done():
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Task scheduler stopped")
    
    async def schedule_task(
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
    ) -> str:
        """Schedule a task to run at a specific time or interval.
        
        Args:
            func: The function to execute.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            schedule_time: The time to run the task.
                If None, the task will run as soon as possible.
            interval: The interval between runs for periodic tasks.
                If None, the task will run only once.
            max_runs: Maximum number of times to run the task.
                If None, the task will run indefinitely (for periodic tasks).
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            description: Description of the task.
            
        Returns:
            The ID of the scheduled task.
        """
        # Convert datetime to timestamp if needed
        if isinstance(schedule_time, datetime):
            schedule_time = schedule_time.timestamp()
        
        # Convert timedelta to seconds if needed
        if isinstance(interval, timedelta):
            interval = interval.total_seconds()
        
        # Create the scheduled task
        scheduled_task = ScheduledTask(
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
        
        # Add the task to the scheduler
        async with self.lock:
            self.scheduled_tasks[scheduled_task.task_id] = scheduled_task
            heapq.heappush(self.task_heap, scheduled_task)
        
        logger.info(f"Scheduled task {scheduled_task.task_id} to run at {scheduled_task.next_run_time}")
        return scheduled_task.task_id
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        async with self.lock:
            if task_id in self.scheduled_tasks:
                self.scheduled_tasks[task_id].active = False
                logger.info(f"Cancelled scheduled task {task_id}")
                return True
        
        return False
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a scheduled task.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            A dictionary with task information, or None if the task was not found.
        """
        if task_id not in self.scheduled_tasks:
            return None
        
        task = self.scheduled_tasks[task_id]
        return {
            "task_id": task.task_id,
            "schedule_time": task.schedule_time,
            "interval": task.interval,
            "max_runs": task.max_runs,
            "runs": task.runs,
            "last_run_time": task.last_run_time,
            "next_run_time": task.next_run_time,
            "active": task.active,
            "description": task.description,
        }
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get information about all scheduled tasks.
        
        Returns:
            A list of dictionaries with task information.
        """
        tasks = []
        for task_id in self.scheduled_tasks:
            task_info = await self.get_task(task_id)
            if task_info:
                tasks.append(task_info)
        
        return tasks
    
    async def _scheduler_loop(self) -> None:
        """Main loop for the task scheduler."""
        while self.running:
            try:
                await self._check_tasks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_tasks(self) -> None:
        """Check for tasks that need to be run."""
        now = time.time()
        tasks_to_run = []
        
        async with self.lock:
            # Check if there are tasks to run
            while self.task_heap and self.task_heap[0].next_run_time <= now:
                task = heapq.heappop(self.task_heap)
                
                # Skip inactive tasks
                if not task.active:
                    continue
                
                # Add the task to the list of tasks to run
                tasks_to_run.append(task)
        
        # Run the tasks
        for task in tasks_to_run:
            await self._run_task(task)
    
    async def _run_task(self, scheduled_task: ScheduledTask) -> None:
        """Run a scheduled task.
        
        Args:
            scheduled_task: The scheduled task to run.
        """
        try:
            # Update task state
            scheduled_task.runs += 1
            scheduled_task.last_run_time = time.time()
            
            # Create a task in the task queue
            task = await add_task(
                func=scheduled_task.func,
                args=scheduled_task.args,
                kwargs=scheduled_task.kwargs,
                task_id=f"{scheduled_task.task_id}_run_{scheduled_task.runs}",
                priority=scheduled_task.priority,
                timeout=scheduled_task.timeout,
                retry_count=scheduled_task.retry_count,
                retry_delay=scheduled_task.retry_delay,
                description=scheduled_task.description,
            )
            
            logger.info(f"Running scheduled task {scheduled_task.task_id} (run {scheduled_task.runs})")
            
            # Update the next run time for periodic tasks
            should_run_again = scheduled_task.update_next_run_time()
            
            async with self.lock:
                if should_run_again:
                    # Add the task back to the heap with the updated next run time
                    heapq.heappush(self.task_heap, scheduled_task)
                else:
                    # Remove the task from the scheduler
                    scheduled_task.active = False
                    logger.info(f"Scheduled task {scheduled_task.task_id} completed all runs")
            
        except Exception as e:
            logger.exception(f"Error running scheduled task {scheduled_task.task_id}: {str(e)}")


# Global task scheduler instance
_task_scheduler = None


async def get_task_scheduler(
    task_queue: Optional[TaskQueue] = None,
    check_interval: float = 1.0,
) -> TaskScheduler:
    """Get the global task scheduler instance.
    
    Args:
        task_queue: The task queue to use. If None, the default queue will be used.
        check_interval: Interval in seconds to check for tasks to run.
        
    Returns:
        The global task scheduler instance.
    """
    global _task_scheduler
    
    if _task_scheduler is None:
        _task_scheduler = TaskScheduler(
            task_queue=task_queue,
            check_interval=check_interval,
        )
        await _task_scheduler.start()
    
    return _task_scheduler


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
            If None, the task will run as soon as possible.
        interval: The interval between runs for periodic tasks.
            If None, the task will run only once.
        max_runs: Maximum number of times to run the task.
            If None, the task will run indefinitely (for periodic tasks).
        priority: The priority of the task. Higher values indicate higher priority.
        timeout: Maximum time in seconds to wait for the task to complete.
        retry_count: Number of times to retry the task if it fails.
        retry_delay: Delay in seconds between retries.
        description: Description of the task.
        
    Returns:
        The ID of the scheduled task.
    """
    scheduler = await get_task_scheduler()
    return await scheduler.schedule_task(
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


async def cancel_scheduled_task(task_id: str) -> bool:
    """Cancel a scheduled task.
    
    Args:
        task_id: The ID of the task to cancel.
        
    Returns:
        True if the task was cancelled, False otherwise.
    """
    scheduler = await get_task_scheduler()
    return await scheduler.cancel_task(task_id)


async def get_scheduled_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a scheduled task.
    
    Args:
        task_id: The ID of the task.
        
    Returns:
        A dictionary with task information, or None if the task was not found.
    """
    scheduler = await get_task_scheduler()
    return await scheduler.get_task(task_id)


async def get_all_scheduled_tasks() -> List[Dict[str, Any]]:
    """Get information about all scheduled tasks.
    
    Returns:
        A list of dictionaries with task information.
    """
    scheduler = await get_task_scheduler()
    return await scheduler.get_all_tasks()
