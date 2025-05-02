"""
Parallel Processing.

This module provides tools for executing tasks in parallel, with support for
thread-based, process-based, and asynchronous execution.

TODO(Issue #10): Add support for distributed processing
TODO(Issue #10): Implement adaptive resource allocation
TODO(Issue #10): Add monitoring and visualization
"""

from augment_adam.parallel.base import (
    Task,
    TaskStatus,
    TaskResult,
    TaskExecutor,
    ParallelExecutor,
)

from augment_adam.parallel.thread import (
    ThreadPoolExecutor,
    ThreadTask,
)

from augment_adam.parallel.process import (
    ProcessPoolExecutor,
    ProcessTask,
)

from augment_adam.parallel.async_module import (
    AsyncExecutor,
    AsyncTask,
)

from augment_adam.parallel.workflow import (
    Workflow,
    WorkflowExecutor,
    WorkflowTask,
    TaskDependency,
)

from augment_adam.parallel.utils import (
    ResourceMonitor,
    ResourceThrottler,
    ResultAggregator,
    ErrorHandler,
)

__all__ = [
    # Base
    "Task",
    "TaskStatus",
    "TaskResult",
    "TaskExecutor",
    "ParallelExecutor",

    # Thread
    "ThreadPoolExecutor",
    "ThreadTask",

    # Process
    "ProcessPoolExecutor",
    "ProcessTask",

    # Async
    "AsyncExecutor",
    "AsyncTask",

    # Workflow
    "Workflow",
    "WorkflowExecutor",
    "WorkflowTask",
    "TaskDependency",

    # Utils
    "ResourceMonitor",
    "ResourceThrottler",
    "ResultAggregator",
    "ErrorHandler",
]
