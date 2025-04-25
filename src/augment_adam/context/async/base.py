"""
Base classes for the async module.

This module provides the base classes for the async module, including
the AsyncContextBuilder, AsyncContextTask, and AsyncContextManager classes.
"""

import uuid
import time
import threading
import queue
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Tuple
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.context.core.base import Context, ContextType, ContextEngine


class TaskStatus(Enum):
    """
    Status of an async context task.
    
    This enum defines the possible statuses of an async context task.
    """
    
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class AsyncContextTask:
    """
    Task for asynchronous context building.
    
    This class represents a task for asynchronous context building, including
    its parameters, status, and results.
    
    Attributes:
        id: Unique identifier for the task.
        engine_name: The name of the context engine to use.
        builder_name: The name of the context builder to use.
        parameters: Parameters for the context builder.
        status: The status of the task.
        created_at: When the task was created.
        started_at: When the task was started.
        completed_at: When the task was completed.
        result_id: The ID of the resulting context.
        error: Error message if the task failed.
    
    TODO(Issue #7): Add support for task dependencies
    TODO(Issue #7): Implement task validation
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    engine_name: str = ""
    builder_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result_id: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary.
        
        Returns:
            Dictionary representation of the task.
        """
        return {
            "id": self.id,
            "engine_name": self.engine_name,
            "builder_name": self.builder_name,
            "parameters": self.parameters,
            "status": self.status.name,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result_id": self.result_id,
            "error": self.error,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AsyncContextTask':
        """
        Create a task from a dictionary.
        
        Args:
            data: Dictionary representation of the task.
            
        Returns:
            Task.
        """
        # Convert status from string to enum
        status_str = data.get("status", TaskStatus.PENDING.name)
        try:
            status = TaskStatus[status_str]
        except KeyError:
            status = TaskStatus.PENDING
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            engine_name=data.get("engine_name", ""),
            builder_name=data.get("builder_name", ""),
            parameters=data.get("parameters", {}),
            status=status,
            created_at=data.get("created_at", time.time()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            result_id=data.get("result_id"),
            error=data.get("error"),
        )


@tag("context.async")
class AsyncContextBuilder(ABC):
    """
    Base class for async context builders.
    
    This class defines the interface for async context builders, which
    build contexts asynchronously.
    
    Attributes:
        name: The name of the builder.
        metadata: Additional metadata for the builder.
    
    TODO(Issue #7): Add support for builder validation
    TODO(Issue #7): Implement builder analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the builder.
        
        Args:
            name: The name of the builder.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def build(self, engine: ContextEngine, parameters: Dict[str, Any]) -> Context:
        """
        Build a context.
        
        Args:
            engine: The context engine to use.
            parameters: Parameters for the builder.
            
        Returns:
            The built context.
            
        Raises:
            Exception: If the context could not be built.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the builder.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the builder.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("context.async")
class AsyncContextManager:
    """
    Manager for asynchronous context building.
    
    This class manages asynchronous context building, including task queuing,
    execution, and result retrieval.
    
    Attributes:
        engines: Dictionary of context engines, keyed by name.
        builders: Dictionary of context builders, keyed by name.
        tasks: Dictionary of tasks, keyed by ID.
        task_queue: Queue of tasks to execute.
        worker_thread: Thread for executing tasks.
        running: Whether the manager is running.
        metadata: Additional metadata for the manager.
    
    TODO(Issue #7): Add support for task priorities
    TODO(Issue #7): Implement task dependencies
    """
    
    def __init__(self) -> None:
        """Initialize the async context manager."""
        self.engines: Dict[str, ContextEngine] = {}
        self.builders: Dict[str, AsyncContextBuilder] = {}
        self.tasks: Dict[str, AsyncContextTask] = {}
        self.task_queue: queue.Queue[str] = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        self.metadata: Dict[str, Any] = {}
    
    def register_engine(self, engine: ContextEngine) -> None:
        """
        Register a context engine with the manager.
        
        Args:
            engine: The context engine to register.
        """
        self.engines[engine.name] = engine
    
    def unregister_engine(self, name: str) -> bool:
        """
        Unregister a context engine from the manager.
        
        Args:
            name: The name of the context engine to unregister.
            
        Returns:
            True if the context engine was unregistered, False otherwise.
        """
        if name in self.engines:
            del self.engines[name]
            return True
        return False
    
    def register_builder(self, builder: AsyncContextBuilder) -> None:
        """
        Register a context builder with the manager.
        
        Args:
            builder: The context builder to register.
        """
        self.builders[builder.name] = builder
    
    def unregister_builder(self, name: str) -> bool:
        """
        Unregister a context builder from the manager.
        
        Args:
            name: The name of the context builder to unregister.
            
        Returns:
            True if the context builder was unregistered, False otherwise.
        """
        if name in self.builders:
            del self.builders[name]
            return True
        return False
    
    def start(self) -> None:
        """Start the async context manager."""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def stop(self) -> None:
        """Stop the async context manager."""
        self.running = False
        if self.worker_thread is not None:
            self.worker_thread.join(timeout=1.0)
            self.worker_thread = None
    
    def submit_task(self, engine_name: str, builder_name: str, parameters: Dict[str, Any]) -> str:
        """
        Submit a task for asynchronous context building.
        
        Args:
            engine_name: The name of the context engine to use.
            builder_name: The name of the context builder to use.
            parameters: Parameters for the context builder.
            
        Returns:
            The ID of the submitted task.
            
        Raises:
            ValueError: If the engine or builder doesn't exist.
        """
        # Check if engine exists
        if engine_name not in self.engines:
            raise ValueError(f"Context engine '{engine_name}' not found")
        
        # Check if builder exists
        if builder_name not in self.builders:
            raise ValueError(f"Context builder '{builder_name}' not found")
        
        # Create task
        task = AsyncContextTask(
            engine_name=engine_name,
            builder_name=builder_name,
            parameters=parameters
        )
        
        # Add task to dictionary and queue
        self.tasks[task.id] = task
        self.task_queue.put(task.id)
        
        # Start the manager if it's not running
        if not self.running:
            self.start()
        
        return task.id
    
    def get_task(self, task_id: str) -> Optional[AsyncContextTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: The ID of the task to get.
            
        Returns:
            The task, or None if it doesn't exist.
        """
        return self.tasks.get(task_id)
    
    def get_result(self, task_id: str) -> Tuple[Optional[Context], Optional[str]]:
        """
        Get the result of a task.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            Tuple of (context, error). If the task is not completed, both will be None.
            If the task failed, context will be None and error will contain the error message.
            If the task completed successfully, context will contain the result and error will be None.
        """
        task = self.get_task(task_id)
        if task is None:
            return None, "Task not found"
        
        if task.status == TaskStatus.PENDING or task.status == TaskStatus.RUNNING:
            return None, None
        
        if task.status == TaskStatus.FAILED:
            return None, task.error
        
        if task.status == TaskStatus.CANCELLED:
            return None, "Task was cancelled"
        
        if task.result_id is None:
            return None, "Task completed but no result ID was set"
        
        # Get the context from the engine
        engine = self.engines.get(task.engine_name)
        if engine is None:
            return None, f"Context engine '{task.engine_name}' not found"
        
        context = engine.get_context(task.result_id)
        if context is None:
            return None, f"Context with ID '{task.result_id}' not found"
        
        return context, None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        task = self.get_task(task_id)
        if task is None:
            return False
        
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True
        
        return False
    
    def _worker_loop(self) -> None:
        """Worker loop for executing tasks."""
        while self.running:
            try:
                # Get a task from the queue
                try:
                    task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Get the task
                task = self.tasks.get(task_id)
                if task is None:
                    continue
                
                # Skip cancelled tasks
                if task.status == TaskStatus.CANCELLED:
                    self.task_queue.task_done()
                    continue
                
                # Execute the task
                self._execute_task(task)
                
                # Mark the task as done
                self.task_queue.task_done()
            except Exception as e:
                # Log the error
                print(f"Error in async context manager worker loop: {e}")
    
    def _execute_task(self, task: AsyncContextTask) -> None:
        """
        Execute a task.
        
        Args:
            task: The task to execute.
        """
        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        try:
            # Get the engine and builder
            engine = self.engines.get(task.engine_name)
            if engine is None:
                raise ValueError(f"Context engine '{task.engine_name}' not found")
            
            builder = self.builders.get(task.builder_name)
            if builder is None:
                raise ValueError(f"Context builder '{task.builder_name}' not found")
            
            # Build the context
            context = builder.build(engine, task.parameters)
            
            # Add the context to the engine
            context_id = engine.add_context(context)
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.result_id = context_id
        except Exception as e:
            # Update task status
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            task.error = str(e)


# Singleton instance
_async_context_manager: Optional[AsyncContextManager] = None

def get_async_context_manager() -> AsyncContextManager:
    """
    Get the singleton instance of the async context manager.
    
    Returns:
        The async context manager instance.
    """
    global _async_context_manager
    if _async_context_manager is None:
        _async_context_manager = AsyncContextManager()
        _async_context_manager.start()
    return _async_context_manager
