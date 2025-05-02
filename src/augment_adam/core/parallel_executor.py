"""Parallel task executor for Augment Adam.

This module provides functionality for executing tasks in parallel.
"""

import asyncio
import logging
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Set, Union, Callable, Awaitable

from augment_adam.core.task_queue import Task, TaskStatus
from augment_adam.core.circuit_breaker import CircuitBreaker, CircuitBreakerState

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Type of resource required by a task."""
    CPU = auto()
    MEMORY = auto()
    GPU = auto()
    NETWORK = auto()
    DISK = auto()
    API = auto()


class ResourceRequirement:
    """Resource requirement for a task."""

    def __init__(
        self,
        resource_type: ResourceType,
        amount: float = 1.0,
        exclusive: bool = False,
    ):
        """Initialize the resource requirement.

        Args:
            resource_type: The type of resource.
            amount: The amount of the resource required.
            exclusive: Whether the resource should be exclusively allocated.
        """
        self.resource_type = resource_type
        self.amount = amount
        self.exclusive = exclusive


class ParallelTaskExecutor:
    """Parallel task executor for Augment Adam.

    This class provides functionality for executing tasks in parallel.
    """

    def __init__(
        self,
        max_concurrency: int = 5,
    ):
        """Initialize the parallel task executor.

        Args:
            max_concurrency: Maximum number of tasks to execute concurrently.
        """
        self.max_concurrency = max_concurrency
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.resource_requirements: Dict[str, List[ResourceRequirement]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.circuit_breaker_names: Dict[str, str] = {}
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.cancelled_tasks: Set[str] = set()
        self.results: Dict[str, Any] = {}

    async def add_task(
        self,
        task: Task,
        dependencies: List[str] = None,
        resource_requirements: List[ResourceRequirement] = None,
        circuit_breaker_name: Optional[str] = None,
    ) -> None:
        """Add a task to the executor.

        Args:
            task: The task to add.
            dependencies: List of task IDs that must complete before this task can start.
            resource_requirements: List of resource requirements for the task.
            circuit_breaker_name: Name of the circuit breaker to use for the task.
        """
        self.tasks[task.task_id] = task
        self.dependencies[task.task_id] = dependencies or []
        self.resource_requirements[task.task_id] = resource_requirements or []
        if circuit_breaker_name:
            self.circuit_breaker_names[task.task_id] = circuit_breaker_name

    async def execute_all(self) -> Dict[str, Any]:
        """Execute all tasks.

        Returns:
            A dictionary mapping task IDs to results.
        """
        # Reset state
        self.running_tasks = set()
        self.completed_tasks = set()
        self.failed_tasks = set()
        self.cancelled_tasks = set()
        self.results = {}

        # Create a set of ready tasks
        ready_tasks = set()
        for task_id in self.tasks:
            if not self.dependencies[task_id]:
                ready_tasks.add(task_id)

        # Execute tasks until all are completed, failed, or cancelled
        while ready_tasks or self.running_tasks:
            # Start ready tasks up to max_concurrency
            while ready_tasks and len(self.running_tasks) < self.max_concurrency:
                task_id = ready_tasks.pop()
                self.running_tasks.add(task_id)
                asyncio.create_task(self._execute_task(task_id))

            # Wait for a task to complete
            await asyncio.sleep(0.1)

        return self.results

    async def _execute_task(self, task_id: str) -> None:
        """Execute a task.

        Args:
            task_id: The ID of the task to execute.
        """
        task = self.tasks[task_id]

        # Check if the circuit breaker is open
        circuit_breaker_name = self.circuit_breaker_names.get(task_id)
        if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[circuit_breaker_name]
            if circuit_breaker.state == CircuitBreakerState.OPEN:
                logger.warning(f"Circuit breaker {circuit_breaker_name} is open, skipping task {task_id}")
                self.running_tasks.remove(task_id)
                self.failed_tasks.add(task_id)
                self._update_ready_tasks()
                return

        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = asyncio.get_event_loop().time()

            # Execute the task
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)

            # Update task status
            task.status = TaskStatus.COMPLETED
            task.completed_at = asyncio.get_event_loop().time()
            task.result = result

            # Record success in the circuit breaker
            if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
                self.circuit_breakers[circuit_breaker_name].success()

            # Update state
            self.running_tasks.remove(task_id)
            self.completed_tasks.add(task_id)
            self.results[task_id] = result

            # Update ready tasks
            self._update_ready_tasks()

        except Exception as e:
            # Update task status
            task.status = TaskStatus.FAILED
            task.completed_at = asyncio.get_event_loop().time()
            task.error = str(e)

            # Record failure in the circuit breaker
            if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
                self.circuit_breakers[circuit_breaker_name].failure()

            # Update state
            self.running_tasks.remove(task_id)
            self.failed_tasks.add(task_id)

            # Update ready tasks
            self._update_ready_tasks()

            logger.error(f"Error executing task {task_id}: {str(e)}")

    def _update_ready_tasks(self) -> None:
        """Update the set of ready tasks."""
        for task_id, deps in self.dependencies.items():
            if task_id in self.completed_tasks or task_id in self.failed_tasks or task_id in self.cancelled_tasks or task_id in self.running_tasks:
                continue

            if all(dep in self.completed_tasks for dep in deps):
                self.running_tasks.add(task_id)
                asyncio.create_task(self._execute_task(task_id))


def create_parallel_executor(
    max_concurrency: int = 5,
) -> ParallelTaskExecutor:
    """Create a parallel task executor.

    Args:
        max_concurrency: Maximum number of tasks to execute concurrently.

    Returns:
        A ParallelTaskExecutor instance.
    """
    return ParallelTaskExecutor(max_concurrency=max_concurrency)
