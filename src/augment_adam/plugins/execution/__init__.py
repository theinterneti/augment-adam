"""
Plugin execution.

This module provides the executor for plugins, which handles plugin execution
and lifecycle management.
"""

from augment_adam.plugins.execution.base import (
    PluginExecutor,
    PluginContext,
    PluginResult,
)

__all__ = [
    "PluginExecutor",
    "PluginContext",
    "PluginResult",
]
