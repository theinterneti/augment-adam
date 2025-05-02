"""
Async-based parallel processing.

This module provides tools for executing tasks asynchronously.
"""

from augment_adam.parallel.async_module.base import (
    AsyncExecutor,
    AsyncTask,
)

__all__ = [
    "AsyncExecutor",
    "AsyncTask",
]
