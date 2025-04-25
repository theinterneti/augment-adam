"""
Error handling for parallel processing.

This module provides error handling for parallel processing, including
strategies for dealing with failures in parallel execution.
"""

from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic, Tuple

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.parallel.base import Task, TaskResult, TaskStatus


T = TypeVar('T')  # Type of task input
R = TypeVar('R')  # Type of task result


class ErrorStrategy(Enum):
    """
    Strategy for handling errors.
    
    This enum defines the possible strategies for handling errors in parallel execution.
    """
    
    FAIL_FAST = auto()      # Fail immediately on first error
    CONTINUE = auto()       # Continue execution despite errors
    RETRY = auto()          # Retry failed tasks
    IGNORE = auto()         # Ignore errors and continue


@tag("parallel.utils")
class ErrorHandler:
    """
    Handle errors in parallel execution.
    
    This class handles errors in parallel execution, applying different strategies
    for dealing with failures.
    
    Attributes:
        name: The name of the error handler.
        strategy: The error handling strategy.
        max_retries: The maximum number of retries for failed tasks.
        retry_delay: The delay between retries, in seconds.
        metadata: Additional metadata for the error handler.
    
    TODO(Issue #10): Add support for more error handling strategies
    TODO(Issue #10): Implement error analytics
    """
    
    def __init__(
        self,
        name: str,
        strategy: ErrorStrategy = ErrorStrategy.FAIL_FAST,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> None:
        """
        Initialize the error handler.
        
        Args:
            name: The name of the error handler.
            strategy: The error handling strategy.
            max_retries: The maximum number of retries for failed tasks.
            retry_delay: The delay between retries, in seconds.
        """
        self.name = name
        self.strategy = strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.metadata: Dict[str, Any] = {}
    
    def handle_error(self, task: Task[T, R], result: TaskResult[R]) -> bool:
        """
        Handle an error in a task.
        
        Args:
            task: The task that failed.
            result: The result of the task.
            
        Returns:
            True if execution should continue, False if it should stop.
        """
        if not result.is_failure():
            return True
        
        # Apply error handling strategy
        if self.strategy == ErrorStrategy.FAIL_FAST:
            return False
        elif self.strategy == ErrorStrategy.CONTINUE:
            return True
        elif self.strategy == ErrorStrategy.RETRY:
            # Check if the task has been retried too many times
            retries = task.get_metadata("retries", 0)
            if retries >= self.max_retries:
                return True
            
            # Increment retry count
            task.set_metadata("retries", retries + 1)
            
            # Reset task status
            task.status = TaskStatus.PENDING
            
            return True
        elif self.strategy == ErrorStrategy.IGNORE:
            # Mark the task as completed
            task.status = TaskStatus.COMPLETED
            task.result = TaskResult(status=TaskStatus.COMPLETED)
            
            return True
        else:
            return False
    
    def handle_errors(self, tasks: Dict[str, Task[T, R]], results: Dict[str, TaskResult[R]]) -> bool:
        """
        Handle errors in multiple tasks.
        
        Args:
            tasks: Dictionary mapping task IDs to tasks.
            results: Dictionary mapping task IDs to results.
            
        Returns:
            True if execution should continue, False if it should stop.
        """
        continue_execution = True
        
        for task_id, result in results.items():
            if result.is_failure():
                task = tasks.get(task_id)
                if task is not None:
                    if not self.handle_error(task, result):
                        continue_execution = False
        
        return continue_execution
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the error handler.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the error handler.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
