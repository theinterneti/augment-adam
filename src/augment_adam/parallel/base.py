"""
Base classes for parallel processing.

This module provides the base classes for parallel processing, including
the Task, TaskResult, TaskExecutor, and ParallelExecutor classes.
"""

import uuid
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic, Tuple
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory


T = TypeVar('T')  # Type of task input
R = TypeVar('R')  # Type of task result


class TaskStatus(Enum):
    """
    Status of a task.
    
    This enum defines the possible statuses of a task.
    """
    
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class TaskResult(Generic[R]):
    """
    Result of a task.
    
    This class represents the result of a task, including the result value,
    status, and error message if applicable.
    
    Attributes:
        value: The result value.
        status: The status of the task.
        error: Error message if the task failed.
        execution_time: The time it took to execute the task.
        metadata: Additional metadata for the result.
    
    TODO(Issue #10): Add support for result validation
    TODO(Issue #10): Implement result analytics
    """
    
    value: Optional[R] = None
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """
        Check if the task was successful.
        
        Returns:
            True if the task was successful, False otherwise.
        """
        return self.status == TaskStatus.COMPLETED
    
    def is_failure(self) -> bool:
        """
        Check if the task failed.
        
        Returns:
            True if the task failed, False otherwise.
        """
        return self.status == TaskStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """
        Check if the task was cancelled.
        
        Returns:
            True if the task was cancelled, False otherwise.
        """
        return self.status == TaskStatus.CANCELLED
    
    def is_done(self) -> bool:
        """
        Check if the task is done.
        
        Returns:
            True if the task is done, False otherwise.
        """
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the result.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the result.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@dataclass
class Task(Generic[T, R]):
    """
    Task for parallel processing.
    
    This class represents a task for parallel processing, including its input,
    function, status, and result.
    
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
    
    TODO(Issue #10): Add support for task dependencies
    TODO(Issue #10): Implement task validation
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    func: Callable[..., R] = field(default_factory=lambda: lambda: None)
    args: Tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: TaskResult[R] = field(default_factory=TaskResult)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self) -> TaskResult[R]:
        """
        Execute the task.
        
        Returns:
            The result of the task.
        """
        # Update task status
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()
        
        try:
            # Execute the function
            value = self.func(*self.args, **self.kwargs)
            
            # Update task status and result
            self.status = TaskStatus.COMPLETED
            self.completed_at = time.time()
            execution_time = self.completed_at - self.started_at
            
            self.result = TaskResult(
                value=value,
                status=TaskStatus.COMPLETED,
                execution_time=execution_time
            )
        except Exception as e:
            # Update task status and result
            self.status = TaskStatus.FAILED
            self.completed_at = time.time()
            execution_time = self.completed_at - self.started_at
            
            self.result = TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
        
        return self.result
    
    def cancel(self) -> bool:
        """
        Cancel the task.
        
        Returns:
            True if the task was cancelled, False otherwise.
        """
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.CANCELLED
            self.completed_at = time.time()
            self.result = TaskResult(status=TaskStatus.CANCELLED)
            return True
        return False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the task.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the task.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("parallel")
class TaskExecutor(Generic[T, R], ABC):
    """
    Base class for task executors.
    
    This class defines the interface for task executors, which execute tasks
    and return their results.
    
    Attributes:
        name: The name of the executor.
        metadata: Additional metadata for the executor.
    
    TODO(Issue #10): Add support for executor validation
    TODO(Issue #10): Implement executor analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the executor.
        
        Args:
            name: The name of the executor.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def submit(self, task: Task[T, R]) -> str:
        """
        Submit a task for execution.
        
        Args:
            task: The task to execute.
            
        Returns:
            The ID of the submitted task.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_result(self, task_id: str) -> Optional[TaskResult[R]]:
        """
        Get the result of a task.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            The result of the task, or None if the task doesn't exist.
        """
        pass
    
    @abstractmethod
    def wait_for_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult[R]]:
        """
        Wait for the result of a task.
        
        Args:
            task_id: The ID of the task.
            timeout: The maximum time to wait, in seconds. If None, wait indefinitely.
            
        Returns:
            The result of the task, or None if the task doesn't exist or the timeout expired.
        """
        pass
    
    @abstractmethod
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        pass
    
    @abstractmethod
    def shutdown(self, wait: bool = True) -> None:
        """
        Shut down the executor.
        
        Args:
            wait: Whether to wait for all tasks to complete before shutting down.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the executor.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the executor.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("parallel")
class ParallelExecutor(TaskExecutor[T, R], ABC):
    """
    Base class for parallel executors.
    
    This class defines the interface for parallel executors, which execute
    multiple tasks in parallel.
    
    Attributes:
        name: The name of the executor.
        metadata: Additional metadata for the executor.
        max_workers: The maximum number of workers.
    
    TODO(Issue #10): Add support for executor validation
    TODO(Issue #10): Implement executor analytics
    """
    
    def __init__(self, name: str, max_workers: Optional[int] = None) -> None:
        """
        Initialize the executor.
        
        Args:
            name: The name of the executor.
            max_workers: The maximum number of workers. If None, use the default.
        """
        super().__init__(name)
        self.max_workers = max_workers
        self.metadata["max_workers"] = max_workers
    
    @abstractmethod
    def map(self, func: Callable[[T], R], items: List[T]) -> List[TaskResult[R]]:
        """
        Apply a function to each item in a list, in parallel.
        
        Args:
            func: The function to apply.
            items: The items to apply the function to.
            
        Returns:
            The results of applying the function to each item.
        """
        pass
    
    @abstractmethod
    def submit_all(self, tasks: List[Task[T, R]]) -> List[str]:
        """
        Submit multiple tasks for execution.
        
        Args:
            tasks: The tasks to execute.
            
        Returns:
            The IDs of the submitted tasks.
        """
        pass
    
    @abstractmethod
    def wait_for_all(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, TaskResult[R]]:
        """
        Wait for the results of multiple tasks.
        
        Args:
            task_ids: The IDs of the tasks.
            timeout: The maximum time to wait, in seconds. If None, wait indefinitely.
            
        Returns:
            Dictionary mapping task IDs to results.
        """
        pass
