"""Plugins for Augment Adam.

This module provides plugins that extend the functionality of Augment Adam,
allowing it to interact with external systems and services.

Available plugins:
- File Manager: Interact with the file system
- System Info: Get information about the system
- Web Search: Search the web for information

Version: 0.1.0
Created: 2025-04-25
Updated: 2025-04-24
"""

from augment_adam.plugins.base import Plugin, PluginManager
from augment_adam.plugins.file_manager import FileManager
from augment_adam.plugins.system_info import SystemInfo
from augment_adam.plugins.web_search import WebSearch

__all__ = [
    "Plugin",
    "PluginManager",
    "FileManager",
    "SystemInfo",
    "WebSearch",
]