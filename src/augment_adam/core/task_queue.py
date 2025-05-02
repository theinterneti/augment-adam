"""Task queue for Augment Adam.

This module provides functionality for managing asynchronous tasks.
"""

import asyncio
import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from enum import Enum, auto

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class Task:
    """Task class for Augment Adam.

    This class represents an asynchronous task.
    """

    def __init__(
        self,
        func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        dependencies: List[str] = None,
        total_steps: Optional[int] = None,
        description: str = "",
    ):
        """Initialize the task.

        Args:
            func: The function to execute.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            dependencies: List of task IDs that must complete before this task can start.
            total_steps: Total number of steps in the task for progress tracking.
            description: Description of the task.
        """
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
        self.priority = priority
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.dependencies = dependencies or []
        self.total_steps = total_steps
        self.description = description

        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = None
        self.current_step = 0
        self.future = None


class TaskQueue:
    """Task queue class for Augment Adam.

    This class manages asynchronous tasks.
    """

    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        max_workers: int = 10,
        max_queue_size: int = 100,
    ):
        """Initialize the task queue.

        Args:
            loop: The event loop to use.
            max_workers: Maximum number of worker tasks.
            max_queue_size: Maximum size of the queue.
        """
        self.loop = loop or asyncio.get_event_loop()
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.queue = asyncio.PriorityQueue()
        self.tasks: Dict[str, Task] = {}
        self.workers: List[asyncio.Task] = []
        self.running = False

    async def start(self) -> None:
        """Start the task queue."""
        if self.running:
            return

        self.running = True
        logger.info("Starting task queue")

        # Start worker tasks
        for _ in range(self.max_workers):
            worker = self.loop.create_task(self._worker())
            self.workers.append(worker)

    async def stop(self) -> None:
        """Stop the task queue."""
        if not self.running:
            return

        self.running = False
        logger.info("Stopping task queue")

        # Cancel all worker tasks
        for worker in self.workers:
            worker.cancel()

        # Wait for all workers to complete
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []

    async def _worker(self) -> None:
        """Worker task that processes tasks from the queue."""
        while self.running:
            try:
                # Get a task from the queue
                _, task = await self.queue.get()

                # Process the task
                await self._process_task(task)

                # Mark the task as done
                self.queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker: {str(e)}")

    async def _process_task(self, task: Task) -> None:
        """Process a task.

        Args:
            task: The task to process.
        """
        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()

        try:
            # Execute the task
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)

            # Update task status
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.result = result

            # Set the future result
            if task.future and not task.future.done():
                task.future.set_result(result)

        except Exception as e:
            # Update task status
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            task.error = str(e)

            # Set the future exception
            if task.future and not task.future.done():
                task.future.set_exception(e)

            logger.error(f"Error processing task {task.task_id}: {str(e)}")

    async def add_task(
        self,
        func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        dependencies: List[str] = None,
        total_steps: Optional[int] = None,
        description: str = "",
    ) -> Task:
        """Add a task to the queue.

        Args:
            func: The function to execute.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            dependencies: List of task IDs that must complete before this task can start.
            total_steps: Total number of steps in the task for progress tracking.
            description: Description of the task.

        Returns:
            The created task.

        Raises:
            ValueError: If the queue is full or a task with the same ID already exists.
        """
        if self.queue.qsize() >= self.max_queue_size:
            raise ValueError("Task queue is full")

        # Create the task
        task = Task(
            func=func,
            args=args,
            kwargs=kwargs,
            task_id=task_id,
            priority=priority,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            dependencies=dependencies,
            total_steps=total_steps,
            description=description,
        )

        # Check if a task with the same ID already exists
        if task.task_id in self.tasks:
            raise ValueError(f"Task with ID {task.task_id} already exists")

        # Add the task to the dictionary
        self.tasks[task.task_id] = task

        # Create a future for the task
        task.future = self.loop.create_future() if self.loop else asyncio.Future()

        # Add the task to the queue
        await self.queue.put((-priority, task))

        logger.info(f"Added task {task.task_id} to the queue")
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to get.

        Returns:
            The task, or None if not found.
        """
        return self.tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.

        Args:
            task_id: The ID of the task to cancel.

        Returns:
            True if the task was cancelled, False otherwise.
        """
        task = self.tasks.get(task_id)
        if not task:
            return False

        # If the task is already completed or cancelled, return False
        if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            return False

        # Update task status
        task.status = TaskStatus.CANCELLED
        task.completed_at = time.time()

        # Cancel the future
        if task.future and not task.future.done():
            task.future.cancel()

        logger.info(f"Cancelled task {task_id}")
        return True

    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a task to complete.

        Args:
            task_id: The ID of the task to wait for.
            timeout: Maximum time in seconds to wait for the task to complete.

        Returns:
            The result of the task, or None if the task timed out or failed.
        """
        task = self.tasks.get(task_id)
        if not task:
            return None

        # If the task is already completed, return the result
        if task.status == TaskStatus.COMPLETED:
            return task.result

        # If the task is already failed or cancelled, return None
        if task.status in (TaskStatus.FAILED, TaskStatus.CANCELLED):
            return None

        # Wait for the future to complete
        try:
            if timeout:
                return await asyncio.wait_for(task.future, timeout)
            else:
                return await task.future
        except asyncio.TimeoutError:
            logger.warning(f"Task {task_id} timed out")
            return None
        except asyncio.CancelledError:
            logger.warning(f"Task {task_id} was cancelled")
            return None
        except Exception as e:
            logger.error(f"Error waiting for task {task_id}: {str(e)}")
            return None

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the task queue.

        Returns:
            A dictionary of queue statistics.
        """
        # Count tasks by status
        status_counts = {status: 0 for status in TaskStatus}
        for task in self.tasks.values():
            status_counts[task.status] += 1

        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "workers": len(self.workers),
            "max_workers": self.max_workers,
            "running": self.running,
            "tasks": {
                "total": len(self.tasks),
                "pending": status_counts[TaskStatus.PENDING],
                "running": status_counts[TaskStatus.RUNNING],
                "completed": status_counts[TaskStatus.COMPLETED],
                "failed": status_counts[TaskStatus.FAILED],
                "cancelled": status_counts[TaskStatus.CANCELLED],
            }
        }


# Global task queue instance
_default_queue = None


def get_task_queue() -> TaskQueue:
    """Get the default task queue.

    Returns:
        The default task queue.
    """
    global _default_queue
    if _default_queue is None:
        # Get the current event loop
        loop = asyncio.get_event_loop()
        _default_queue = TaskQueue(loop=loop)
    return _default_queue


async def add_task(
    func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None,
    task_id: Optional[str] = None,
    priority: int = 0,
    timeout: Optional[float] = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    dependencies: List[str] = None,
    total_steps: Optional[int] = None,
    description: str = "",
) -> Task:
    """Add a task to the default queue.

    Args:
        func: The function to execute.
        args: Positional arguments to pass to the function.
        kwargs: Keyword arguments to pass to the function.
        task_id: A unique identifier for the task. If not provided, a UUID will be generated.
        priority: The priority of the task. Higher values indicate higher priority.
        timeout: Maximum time in seconds to wait for the task to complete.
        retry_count: Number of times to retry the task if it fails.
        retry_delay: Delay in seconds between retries.
        dependencies: List of task IDs that must complete before this task can start.
        total_steps: Total number of steps in the task for progress tracking.
        description: Description of the task.

    Returns:
        The created task.
    """
    queue = get_task_queue()
    if not queue.running:
        await queue.start()

    return await queue.add_task(
        func=func,
        args=args,
        kwargs=kwargs,
        task_id=task_id,
        priority=priority,
        timeout=timeout,
        retry_count=retry_count,
        retry_delay=retry_delay,
        dependencies=dependencies,
        total_steps=total_steps,
        description=description,
    )


async def get_task(task_id: str) -> Optional[Task]:
    """Get a task by ID.

    Args:
        task_id: The ID of the task to get.

    Returns:
        The task, or None if not found.
    """
    queue = get_task_queue()
    return await queue.get_task(task_id)


async def cancel_task(task_id: str) -> bool:
    """Cancel a task.

    Args:
        task_id: The ID of the task to cancel.

    Returns:
        True if the task was cancelled, False otherwise.
    """
    queue = get_task_queue()
    return await queue.cancel_task(task_id)


async def wait_for_task(task_id: str, timeout: Optional[float] = None) -> Any:
    """Wait for a task to complete.

    Args:
        task_id: The ID of the task to wait for.
        timeout: Maximum time in seconds to wait for the task to complete.

    Returns:
        The result of the task, or None if the task timed out or failed.
    """
    queue = get_task_queue()
    return await queue.wait_for_task(task_id, timeout)


async def get_queue_stats() -> Dict[str, Any]:
    """Get statistics about the task queue.

    Returns:
        A dictionary of queue statistics.
    """
    queue = get_task_queue()
    return await queue.get_queue_stats()
