"""
Process-based parallel processing.

This module provides tools for executing tasks in parallel using processes.
"""

from augment_adam.parallel.process.base import (
    ProcessPoolExecutor,
    ProcessTask,
)

__all__ = [
    "ProcessPoolExecutor",
    "ProcessTask",
]
