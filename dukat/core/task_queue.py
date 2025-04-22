"""Task queue system for async processing.

This module provides a task queue system for asynchronous processing
of tasks in the background.

Version: 0.1.0
Created: 2025-04-23
"""

import asyncio
import logging
import time
import uuid
import os
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """A task to be executed asynchronously."""

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
    ):
        """Initialize a task.

        Args:
            func: The function to execute.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            dependencies: List of task IDs that must complete before this task can run.
        """
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.task_id = task_id or str(uuid.uuid4())
        self.priority = priority
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.dependencies = dependencies or []

        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.retries_left = retry_count
        self.future = None  # Will be set when the task is scheduled

    def __lt__(self, other):
        """Compare tasks by priority for the priority queue."""
        if not isinstance(other, Task):
            return NotImplemented
        return self.priority > other.priority  # Higher priority first

    async def execute(self) -> Any:
        """Execute the task.

        Returns:
            The result of the task.

        Raises:
            Exception: If the task fails.
        """
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()

        try:
            # Check if the function is a coroutine function
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(*self.args, **self.kwargs)
            else:
                # Run synchronous functions in a thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: self.func(*self.args, **self.kwargs)
                )

            self.result = result
            self.status = TaskStatus.COMPLETED
            self.completed_at = time.time()
            return result

        except Exception as e:
            self.error = str(e)
            self.status = TaskStatus.FAILED
            self.completed_at = time.time()
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary.

        Returns:
            A dictionary representation of the task.
        """
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "priority": self.priority,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retries_left": self.retries_left,
            "dependencies": self.dependencies,
        }


class TaskQueue:
    """A queue for asynchronous task execution."""

    def __init__(
        self,
        max_workers: int = 5,
        max_queue_size: int = 100,
        enable_persistence: bool = True,
        persistence_dir: Optional[str] = None,
        auto_save_interval: float = 60.0,
    ):
        """Initialize the task queue.

        Args:
            max_workers: Maximum number of worker tasks to run concurrently.
            max_queue_size: Maximum number of tasks to queue.
            enable_persistence: Whether to enable task persistence.
            persistence_dir: Directory to store persistence files.
                If None, defaults to ~/.dukat/tasks
            auto_save_interval: Interval in seconds between auto-saves.
                Set to 0 to disable auto-saving.
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.enable_persistence = enable_persistence
        self.persistence_dir = persistence_dir
        self.auto_save_interval = auto_save_interval

        self.tasks: Dict[str, Task] = {}
        self.queue = asyncio.PriorityQueue()
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.loop = None
        self.persistence = None
        self.auto_save_task = None

    async def start(self):
        """Start the task queue."""
        if self.running:
            return

        self.running = True
        self.loop = asyncio.get_event_loop()

        # Initialize persistence if enabled
        if self.enable_persistence:
            from dukat.core.task_persistence import TaskPersistence
            self.persistence = TaskPersistence(
                persistence_dir=self.persistence_dir,
                auto_save_interval=self.auto_save_interval,
            )

            # Try to load persisted tasks
            if self.persistence:
                self.persistence.load_queue(self)

            # Start auto-save task if interval > 0
            if self.auto_save_interval > 0:
                self.auto_save_task = asyncio.create_task(self._auto_save())

        # Start worker tasks
        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._worker())
            self.workers.append(worker)

        logger.info(f"Task queue started with {self.max_workers} workers")

    async def stop(self):
        """Stop the task queue."""
        if not self.running:
            return

        self.running = False

        # Save task state before stopping
        if self.enable_persistence and self.persistence:
            self.persistence.save_queue(self)

        # Cancel auto-save task if running
        if self.auto_save_task and not self.auto_save_task.done():
            self.auto_save_task.cancel()
            try:
                await self.auto_save_task
            except asyncio.CancelledError:
                pass

        # Cancel all worker tasks
        for worker in self.workers:
            worker.cancel()

        # Wait for all worker tasks to complete
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)

        self.workers = []
        logger.info("Task queue stopped")

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
            dependencies: List of task IDs that must complete before this task can run.

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
        )

        # Check if a task with the same ID already exists
        if task.task_id in self.tasks:
            raise ValueError(f"Task with ID {task.task_id} already exists")

        # Add the task to the dictionary
        self.tasks[task.task_id] = task

        # Create a future for the task
        task.future = self.loop.create_future() if self.loop else asyncio.Future()

        # Add the task to the queue
        await self.queue.put(task)

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
        task = await self.get_task(task_id)
        if not task:
            return False

        if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            task.status = TaskStatus.CANCELLED

            # If the task has a future, cancel it
            if task.future and not task.future.done():
                task.future.cancel()

            logger.info(f"Cancelled task {task_id}")
            return True

        return False

    async def wait_for_task(
        self,
        task_id: str,
        timeout: Optional[float] = None,
    ) -> Optional[Any]:
        """Wait for a task to complete.

        Args:
            task_id: The ID of the task to wait for.
            timeout: Maximum time in seconds to wait for the task to complete.

        Returns:
            The result of the task, or None if the task was not found or timed out.
        """
        task = await self.get_task(task_id)
        if not task:
            return None

        if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            return task.result

        try:
            # Wait for the task to complete
            await asyncio.wait_for(task.future, timeout=timeout)
            return task.result
        except asyncio.TimeoutError:
            logger.warning(f"Timed out waiting for task {task_id}")
            return None
        except asyncio.CancelledError:
            logger.warning(f"Waiting for task {task_id} was cancelled")
            return None

    async def _worker(self):
        """Worker task that processes tasks from the queue."""
        while self.running:
            try:
                # Get a task from the queue
                task = await self.queue.get()

                # Check if all dependencies are completed
                dependencies_met = True
                for dep_id in task.dependencies:
                    dep_task = await self.get_task(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break

                if not dependencies_met:
                    # Put the task back in the queue
                    await self.queue.put(task)
                    # Sleep to avoid busy-waiting
                    await asyncio.sleep(0.1)
                    continue

                # Execute the task
                try:
                    if task.timeout:
                        # Execute with timeout
                        result = await asyncio.wait_for(
                            task.execute(), timeout=task.timeout
                        )
                    else:
                        # Execute without timeout
                        result = await task.execute()

                    # Set the result in the future
                    if not task.future.done():
                        task.future.set_result(result)

                    # Save task state after successful completion
                    if self.enable_persistence and self.persistence and task.status == TaskStatus.COMPLETED:
                        await asyncio.to_thread(self.persistence.save_queue, self)

                except asyncio.TimeoutError:
                    logger.warning(f"Task {task.task_id} timed out")
                    task.error = "Task timed out"
                    task.status = TaskStatus.FAILED

                    if not task.future.done():
                        task.future.set_exception(
                            asyncio.TimeoutError(
                                f"Task {task.task_id} timed out")
                        )

                except Exception as e:
                    logger.exception(
                        f"Error executing task {task.task_id}: {str(e)}")

                    # Check if we should retry
                    if task.retries_left > 0:
                        task.retries_left -= 1
                        task.status = TaskStatus.PENDING

                        # Wait before retrying
                        await asyncio.sleep(task.retry_delay)

                        # Put the task back in the queue
                        await self.queue.put(task)
                    else:
                        # No more retries, mark as failed
                        task.error = str(e)
                        task.status = TaskStatus.FAILED

                        if not task.future.done():
                            task.future.set_exception(e)

                finally:
                    # Mark the task as done in the queue
                    self.queue.task_done()

            except asyncio.CancelledError:
                # Worker was cancelled
                break

            except Exception as e:
                logger.exception(f"Unexpected error in worker: {str(e)}")

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the task queue.

        Returns:
            A dictionary with queue statistics.
        """
        pending_count = 0
        running_count = 0
        completed_count = 0
        failed_count = 0
        cancelled_count = 0

        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                pending_count += 1
            elif task.status == TaskStatus.RUNNING:
                running_count += 1
            elif task.status == TaskStatus.COMPLETED:
                completed_count += 1
            elif task.status == TaskStatus.FAILED:
                failed_count += 1
            elif task.status == TaskStatus.CANCELLED:
                cancelled_count += 1

        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "workers": len(self.workers),
            "max_workers": self.max_workers,
            "running": self.running,
            "tasks": {
                "total": len(self.tasks),
                "pending": pending_count,
                "running": running_count,
                "completed": completed_count,
                "failed": failed_count,
                "cancelled": cancelled_count,
            },
        }

    async def _auto_save(self):
        """Auto-save task queue state periodically."""
        try:
            while self.running:
                # Sleep for the auto-save interval
                await asyncio.sleep(self.auto_save_interval)

                # Save the task queue state
                if self.persistence:
                    await asyncio.to_thread(self.persistence.save_queue, self)

        except asyncio.CancelledError:
            # Auto-save task was cancelled
            logger.debug("Auto-save task cancelled")
            raise

        except Exception as e:
            logger.exception(f"Error in auto-save task: {str(e)}")


# Global task queue instance
_default_queue = None


def get_task_queue() -> TaskQueue:
    """Get the default task queue.

    Returns:
        The default task queue.
    """
    global _default_queue
    if _default_queue is None:
        _default_queue = TaskQueue()
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
        dependencies: List of task IDs that must complete before this task can run.

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
    )


async def get_task(task_id: str) -> Optional[Task]:
    """Get a task by ID from the default queue.

    Args:
        task_id: The ID of the task to get.

    Returns:
        The task, or None if not found.
    """
    queue = get_task_queue()
    return await queue.get_task(task_id)


async def cancel_task(task_id: str) -> bool:
    """Cancel a task in the default queue.

    Args:
        task_id: The ID of the task to cancel.

    Returns:
        True if the task was cancelled, False otherwise.
    """
    queue = get_task_queue()
    return await queue.cancel_task(task_id)


async def wait_for_task(
    task_id: str,
    timeout: Optional[float] = None,
) -> Optional[Any]:
    """Wait for a task to complete in the default queue.

    Args:
        task_id: The ID of the task to wait for.
        timeout: Maximum time in seconds to wait for the task to complete.

    Returns:
        The result of the task, or None if the task was not found or timed out.
    """
    queue = get_task_queue()
    return await queue.wait_for_task(task_id, timeout=timeout)


async def get_queue_stats() -> Dict[str, Any]:
    """Get statistics about the default task queue.

    Returns:
        A dictionary with queue statistics.
    """
    queue = get_task_queue()
    return await queue.get_queue_stats()
