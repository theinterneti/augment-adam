"""
Base classes for workflow-based parallel processing.

This module provides the base classes for workflow-based parallel processing,
including the Workflow, WorkflowExecutor, WorkflowTask, and TaskDependency classes.
"""

import time
import threading
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic, Tuple
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.parallel.base import Task, TaskResult, TaskStatus, ParallelExecutor


T = TypeVar('T')  # Type of task input
R = TypeVar('R')  # Type of task result


class DependencyType(Enum):
    """
    Type of task dependency.
    
    This enum defines the possible types of task dependencies.
    """
    
    COMPLETION = auto()  # Task must complete (success or failure)
    SUCCESS = auto()     # Task must succeed
    FAILURE = auto()     # Task must fail


@dataclass
class TaskDependency:
    """
    Dependency between tasks.
    
    This class represents a dependency between tasks, specifying that one task
    depends on another.
    
    Attributes:
        task_id: The ID of the task that is depended on.
        type: The type of dependency.
        metadata: Additional metadata for the dependency.
    
    TODO(Issue #10): Add support for conditional dependencies
    TODO(Issue #10): Implement dependency validation
    """
    
    task_id: str
    type: DependencyType = DependencyType.SUCCESS
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_satisfied(self, task_status: TaskStatus) -> bool:
        """
        Check if the dependency is satisfied.
        
        Args:
            task_status: The status of the task that is depended on.
            
        Returns:
            True if the dependency is satisfied, False otherwise.
        """
        if self.type == DependencyType.COMPLETION:
            return task_status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
        elif self.type == DependencyType.SUCCESS:
            return task_status == TaskStatus.COMPLETED
        elif self.type == DependencyType.FAILURE:
            return task_status == TaskStatus.FAILED
        else:
            return False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the dependency.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the dependency.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("parallel.workflow")
class WorkflowTask(Task[T, R]):
    """
    Task in a workflow.
    
    This class represents a task in a workflow, extending the base Task class
    with workflow-specific functionality.
    
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
        dependencies: List of task dependencies.
    
    TODO(Issue #10): Add support for conditional execution
    TODO(Issue #10): Implement task validation
    """
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the workflow task."""
        super().__init__(*args, **kwargs)
        self.dependencies: List[TaskDependency] = []
    
    def add_dependency(self, task_id: str, dependency_type: DependencyType = DependencyType.SUCCESS) -> None:
        """
        Add a dependency on another task.
        
        Args:
            task_id: The ID of the task that this task depends on.
            dependency_type: The type of dependency.
        """
        self.dependencies.append(TaskDependency(task_id=task_id, type=dependency_type))
    
    def remove_dependency(self, task_id: str) -> bool:
        """
        Remove a dependency on another task.
        
        Args:
            task_id: The ID of the task that this task depends on.
            
        Returns:
            True if the dependency was removed, False otherwise.
        """
        for i, dependency in enumerate(self.dependencies):
            if dependency.task_id == task_id:
                self.dependencies.pop(i)
                return True
        return False
    
    def are_dependencies_satisfied(self, task_statuses: Dict[str, TaskStatus]) -> bool:
        """
        Check if all dependencies are satisfied.
        
        Args:
            task_statuses: Dictionary mapping task IDs to statuses.
            
        Returns:
            True if all dependencies are satisfied, False otherwise.
        """
        for dependency in self.dependencies:
            task_status = task_statuses.get(dependency.task_id)
            if task_status is None or not dependency.is_satisfied(task_status):
                return False
        return True


@tag("parallel.workflow")
class Workflow:
    """
    Workflow for parallel processing.
    
    This class represents a workflow for parallel processing, consisting of
    tasks with dependencies between them.
    
    Attributes:
        id: Unique identifier for the workflow.
        name: The name of the workflow.
        tasks: Dictionary of tasks, keyed by ID.
        metadata: Additional metadata for the workflow.
    
    TODO(Issue #10): Add support for workflow validation
    TODO(Issue #10): Implement workflow analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the workflow.
        
        Args:
            name: The name of the workflow.
        """
        self.id = str(time.time())
        self.name = name
        self.tasks: Dict[str, WorkflowTask[Any, Any]] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_task(self, task: WorkflowTask[Any, Any]) -> str:
        """
        Add a task to the workflow.
        
        Args:
            task: The task to add.
            
        Returns:
            The ID of the added task.
        """
        self.tasks[task.id] = task
        return task.id
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the workflow.
        
        Args:
            task_id: The ID of the task to remove.
            
        Returns:
            True if the task was removed, False otherwise.
        """
        if task_id in self.tasks:
            # Remove the task
            del self.tasks[task_id]
            
            # Remove dependencies on the task
            for task in self.tasks.values():
                task.remove_dependency(task_id)
            
            return True
        return False
    
    def add_dependency(self, dependent_task_id: str, dependency_task_id: str, dependency_type: DependencyType = DependencyType.SUCCESS) -> bool:
        """
        Add a dependency between tasks.
        
        Args:
            dependent_task_id: The ID of the task that depends on the other.
            dependency_task_id: The ID of the task that is depended on.
            dependency_type: The type of dependency.
            
        Returns:
            True if the dependency was added, False otherwise.
        """
        # Check if both tasks exist
        if dependent_task_id not in self.tasks or dependency_task_id not in self.tasks:
            return False
        
        # Add the dependency
        self.tasks[dependent_task_id].add_dependency(dependency_task_id, dependency_type)
        return True
    
    def remove_dependency(self, dependent_task_id: str, dependency_task_id: str) -> bool:
        """
        Remove a dependency between tasks.
        
        Args:
            dependent_task_id: The ID of the task that depends on the other.
            dependency_task_id: The ID of the task that is depended on.
            
        Returns:
            True if the dependency was removed, False otherwise.
        """
        # Check if the dependent task exists
        if dependent_task_id not in self.tasks:
            return False
        
        # Remove the dependency
        return self.tasks[dependent_task_id].remove_dependency(dependency_task_id)
    
    def get_ready_tasks(self, task_statuses: Dict[str, TaskStatus]) -> List[str]:
        """
        Get the IDs of tasks that are ready to execute.
        
        Args:
            task_statuses: Dictionary mapping task IDs to statuses.
            
        Returns:
            List of task IDs that are ready to execute.
        """
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            # Skip tasks that are not pending
            if task_statuses.get(task_id, TaskStatus.PENDING) != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are satisfied
            if task.are_dependencies_satisfied(task_statuses):
                ready_tasks.append(task_id)
        
        return ready_tasks
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the workflow.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the workflow.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("parallel.workflow")
class WorkflowExecutor:
    """
    Executor for workflows.
    
    This class executes workflows, respecting task dependencies and using
    a parallel executor to execute tasks.
    
    Attributes:
        name: The name of the executor.
        metadata: Additional metadata for the executor.
        executor: The parallel executor to use for executing tasks.
        workflows: Dictionary of workflows, keyed by ID.
        task_statuses: Dictionary mapping task IDs to statuses.
        running: Whether the executor is running.
    
    TODO(Issue #10): Add support for workflow executor validation
    TODO(Issue #10): Implement workflow executor analytics
    """
    
    def __init__(self, name: str, executor: ParallelExecutor[Any, Any]) -> None:
        """
        Initialize the workflow executor.
        
        Args:
            name: The name of the executor.
            executor: The parallel executor to use for executing tasks.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
        self.executor = executor
        self.workflows: Dict[str, Workflow] = {}
        self.task_statuses: Dict[str, TaskStatus] = {}
        self.running = True
        self.lock = threading.RLock()
    
    def add_workflow(self, workflow: Workflow) -> str:
        """
        Add a workflow to the executor.
        
        Args:
            workflow: The workflow to add.
            
        Returns:
            The ID of the added workflow.
        """
        with self.lock:
            self.workflows[workflow.id] = workflow
            
            # Initialize task statuses
            for task_id in workflow.tasks:
                self.task_statuses[task_id] = TaskStatus.PENDING
        
        return workflow.id
    
    def remove_workflow(self, workflow_id: str) -> bool:
        """
        Remove a workflow from the executor.
        
        Args:
            workflow_id: The ID of the workflow to remove.
            
        Returns:
            True if the workflow was removed, False otherwise.
        """
        with self.lock:
            if workflow_id in self.workflows:
                # Remove the workflow
                workflow = self.workflows.pop(workflow_id)
                
                # Remove task statuses
                for task_id in workflow.tasks:
                    self.task_statuses.pop(task_id, None)
                
                return True
        return False
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, TaskResult[Any]]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: The ID of the workflow to execute.
            
        Returns:
            Dictionary mapping task IDs to results.
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            if workflow is None:
                return {}
        
        # Execute the workflow
        return self._execute_workflow(workflow)
    
    def _execute_workflow(self, workflow: Workflow) -> Dict[str, TaskResult[Any]]:
        """
        Execute a workflow.
        
        Args:
            workflow: The workflow to execute.
            
        Returns:
            Dictionary mapping task IDs to results.
        """
        results: Dict[str, TaskResult[Any]] = {}
        
        # Initialize task statuses
        with self.lock:
            for task_id in workflow.tasks:
                self.task_statuses[task_id] = TaskStatus.PENDING
        
        # Execute tasks until all are done
        while True:
            # Get ready tasks
            with self.lock:
                ready_task_ids = workflow.get_ready_tasks(self.task_statuses)
            
            # If there are no ready tasks, check if all tasks are done
            if not ready_task_ids:
                with self.lock:
                    all_done = all(
                        status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
                        for task_id, status in self.task_statuses.items()
                        if task_id in workflow.tasks
                    )
                
                if all_done:
                    break
                
                # Wait a bit before checking again
                time.sleep(0.1)
                continue
            
            # Execute ready tasks
            for task_id in ready_task_ids:
                with self.lock:
                    task = workflow.tasks.get(task_id)
                    if task is None:
                        continue
                    
                    # Mark task as running
                    self.task_statuses[task_id] = TaskStatus.RUNNING
                
                # Submit task to executor
                self.executor.submit(task)
            
            # Wait for tasks to complete
            for task_id in ready_task_ids:
                # Wait for task to complete
                result = self.executor.wait_for_result(task_id)
                
                # Update task status and result
                with self.lock:
                    if result is not None:
                        self.task_statuses[task_id] = result.status
                        results[task_id] = result
                    else:
                        self.task_statuses[task_id] = TaskStatus.FAILED
                        results[task_id] = TaskResult(status=TaskStatus.FAILED, error="Task execution failed")
        
        return results
    
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
