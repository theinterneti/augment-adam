"""
Workflow module for parallel processing.

This module provides tools for defining and executing workflows with task dependencies.
"""

from augment_adam.parallel.workflow.base import (
    Workflow,
    WorkflowExecutor,
    WorkflowTask,
    TaskDependency,
)

__all__ = [
    "Workflow",
    "WorkflowExecutor",
    "WorkflowTask",
    "TaskDependency",
]
