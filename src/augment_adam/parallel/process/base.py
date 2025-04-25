"""
Base classes for process-based parallel processing.

This module provides the base classes for process-based parallel processing,
including the ProcessPoolExecutor and ProcessTask classes.
"""

import time
import threading
import multiprocessing
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic, Tuple
from concurrent.futures import ProcessPoolExecutor as ConcurrentProcessPoolExecutor

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.parallel.base import Task, TaskResult, TaskStatus, ParallelExecutor


T = TypeVar('T')  # Type of task input
R = TypeVar('R')  # Type of task result


@tag("parallel.process")
class ProcessTask(Task[T, R]):
    """
    Task for process-based parallel processing.
    
    This class represents a task for process-based parallel processing, extending
    the base Task class with process-specific functionality.
    
    Attributes:
        id: Unique identifier for the task.
        func: The function to execute.
        args: Positional arguments for the function.
        kwargs: Keyword arguments for the function.
        status: The status of the task.
        result: The result of the task.
        created_at: When the task was created.
        started_at: When the task was started.
        completed_at: When the task was completed.
        priority: The priority of the task (higher values have higher priority).
        metadata: Additional metadata for the task.
        event: Event for signaling task completion.
    
    TODO(Issue #10): Add support for process-specific task dependencies
    TODO(Issue #10): Implement process-specific task validation
    """
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the process task."""
        super().__init__(*args, **kwargs)
        self.event = threading.Event()
    
    def execute(self) -> TaskResult[R]:
        """
        Execute the task in the current process.
        
        Returns:
            The result of the task.
        """
        result = super().execute()
        self.event.set()
        return result
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for the task to complete.
        
        Args:
            timeout: The maximum time to wait, in seconds. If None, wait indefinitely.
            
        Returns:
            True if the task completed, False if the timeout expired.
        """
        return self.event.wait(timeout)


@tag("parallel.process")
class ProcessPoolExecutor(ParallelExecutor[T, R]):
    """
    Process pool executor for parallel processing.
    
    This class implements a process pool executor for parallel processing,
    using a pool of processes to execute tasks.
    
    Attributes:
        name: The name of the executor.
        metadata: Additional metadata for the executor.
        max_workers: The maximum number of worker processes.
        executor: The underlying concurrent.futures.ProcessPoolExecutor.
        tasks: Dictionary of tasks, keyed by ID.
        running: Whether the executor is running.
    
    TODO(Issue #10): Add support for process pool executor validation
    TODO(Issue #10): Implement process pool executor analytics
    """
    
    def __init__(self, name: str = "process_pool_executor", max_workers: Optional[int] = None) -> None:
        """
        Initialize the process pool executor.
        
        Args:
            name: The name of the executor.
            max_workers: The maximum number of worker processes. If None, use the default.
        """
        super().__init__(name, max_workers)
        
        self.executor = ConcurrentProcessPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, ProcessTask[T, R]] = {}
        self.running = True
        self.lock = threading.RLock()
    
    def submit(self, task: Task[T, R]) -> str:
        """
        Submit a task for execution.
        
        Args:
            task: The task to execute.
            
        Returns:
            The ID of the submitted task.
        """
        if not isinstance(task, ProcessTask):
            # Convert to ProcessTask
            process_task = ProcessTask(
                id=task.id,
                func=task.func,
                args=task.args,
                kwargs=task.kwargs,
                priority=task.priority,
                metadata=task.metadata
            )
        else:
            process_task = task
        
        with self.lock:
            # Add task to dictionary
            self.tasks[process_task.id] = process_task
            
            # Define a wrapper function to update the task status
            def wrapper():
                return process_task.execute()
            
            # Submit task to executor
            future = self.executor.submit(wrapper)
            
            # Add callback to update task when future completes
            def callback(future):
                try:
                    # Get result from future
                    result = future.result()
                    
                    # Update task result
                    process_task.result = result
                    process_task.status = result.status
                    process_task.completed_at = time.time()
                    
                    # Signal task completion
                    process_task.event.set()
                except Exception as e:
                    # Update task status and result
                    process_task.status = TaskStatus.FAILED
                    process_task.completed_at = time.time()
                    process_task.result = TaskResult(
                        status=TaskStatus.FAILED,
                        error=str(e),
                        execution_time=process_task.completed_at - (process_task.started_at or process_task.created_at)
                    )
                    
                    # Signal task completion
                    process_task.event.set()
            
            future.add_done_callback(callback)
            
            # Store future in task metadata
            process_task.set_metadata("future", future)
        
        return process_task.id
    
    def submit_function(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> str:
        """
        Submit a function for execution.
        
        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
            
        Returns:
            The ID of the submitted task.
        """
        task = ProcessTask(func=func, args=args, kwargs=kwargs)
        return self.submit(task)
    
    def get_result(self, task_id: str) -> Optional[TaskResult[R]]:
        """
        Get the result of a task.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            The result of the task, or None if the task doesn't exist.
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                return None
            
            return task.result
    
    def wait_for_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult[R]]:
        """
        Wait for the result of a task.
        
        Args:
            task_id: The ID of the task.
            timeout: The maximum time to wait, in seconds. If None, wait indefinitely.
            
        Returns:
            The result of the task, or None if the task doesn't exist or the timeout expired.
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                return None
        
        # Wait for task to complete
        if not task.wait(timeout):
            return None
        
        return task.result
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                return False
            
            # If the task is pending, cancel it
            if task.status == TaskStatus.PENDING:
                task.cancel()
                return True
            
            # If the task is running, try to cancel its future
            if task.status == TaskStatus.RUNNING:
                future = task.get_metadata("future")
                if future is not None:
                    return future.cancel()
            
            return False
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shut down the executor.
        
        Args:
            wait: Whether to wait for all tasks to complete before shutting down.
        """
        self.running = False
        self.executor.shutdown(wait=wait)
    
    def map(self, func: Callable[[T], R], items: List[T]) -> List[TaskResult[R]]:
        """
        Apply a function to each item in a list, in parallel.
        
        Args:
            func: The function to apply.
            items: The items to apply the function to.
            
        Returns:
            The results of applying the function to each item.
        """
        # Create tasks
        tasks = [ProcessTask(func=func, args=(item,)) for item in items]
        
        # Submit tasks
        task_ids = self.submit_all(tasks)
        
        # Wait for all tasks to complete
        results = self.wait_for_all(task_ids)
        
        # Return results in the same order as items
        return [results[task_id] for task_id in task_ids]
    
    def submit_all(self, tasks: List[Task[T, R]]) -> List[str]:
        """
        Submit multiple tasks for execution.
        
        Args:
            tasks: The tasks to execute.
            
        Returns:
            The IDs of the submitted tasks.
        """
        return [self.submit(task) for task in tasks]
    
    def wait_for_all(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, TaskResult[R]]:
        """
        Wait for the results of multiple tasks.
        
        Args:
            task_ids: The IDs of the tasks.
            timeout: The maximum time to wait, in seconds. If None, wait indefinitely.
            
        Returns:
            Dictionary mapping task IDs to results.
        """
        results: Dict[str, TaskResult[R]] = {}
        
        # Calculate deadline
        deadline = None if timeout is None else time.time() + timeout
        
        # Wait for each task
        for task_id in task_ids:
            # Calculate remaining time
            remaining = None if deadline is None else max(0, deadline - time.time())
            
            # Wait for task
            result = self.wait_for_result(task_id, remaining)
            
            # Store result
            results[task_id] = result if result is not None else TaskResult(status=TaskStatus.PENDING)
            
            # Check if deadline has passed
            if deadline is not None and time.time() >= deadline:
                break
        
        return results
