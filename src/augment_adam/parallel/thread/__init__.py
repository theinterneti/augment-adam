"""
Thread-based parallel processing.

This module provides tools for executing tasks in parallel using threads.
"""

from augment_adam.parallel.thread.base import (
    ThreadPoolExecutor,
    ThreadTask,
)

__all__ = [
    "ThreadPoolExecutor",
    "ThreadTask",
]
