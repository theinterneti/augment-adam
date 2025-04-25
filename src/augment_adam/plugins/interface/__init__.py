"""
Plugin interface.

This module provides the interface for plugins, including the base Plugin class
and related metadata classes.
"""

from augment_adam.plugins.interface.base import (
    Plugin,
    PluginMetadata,
    PluginType,
    PluginCategory,
    PluginHook,
)

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginType",
    "PluginCategory",
    "PluginHook",
]
