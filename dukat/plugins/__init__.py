"""Plugin system for the Dukat assistant.

This package contains the plugin system for the Dukat assistant,
allowing for extensibility through custom tools and capabilities.

Version: 0.1.0
Created: 2025-04-22
"""

import logging
from typing import Dict, Any, List, Optional

from dukat.plugins.base import Plugin, PluginRegistry, get_plugin_registry
from dukat.plugins.file_manager import FileManagerPlugin
from dukat.plugins.web_search import WebSearchPlugin
from dukat.plugins.system_info import SystemInfoPlugin

logger = logging.getLogger(__name__)


def initialize_plugins() -> PluginRegistry:
    """Initialize the default plugins.

    Returns:
        The plugin registry with default plugins registered.
    """
    # Get the plugin registry
    registry = get_plugin_registry()

    # Register default plugins
    registry.register(FileManagerPlugin())
    registry.register(WebSearchPlugin())
    registry.register(SystemInfoPlugin())

    logger.info(f"Initialized {len(registry.plugins)} default plugins")
    return registry


# Initialize plugins when the module is imported
default_registry = initialize_plugins()


def get_plugin(name: str) -> Optional[Plugin]:
    """Get a plugin by name.

    Args:
        name: The name of the plugin to get.

    Returns:
        The plugin, or None if not found.
    """
    return default_registry.get_plugin(name)


def list_plugins() -> List[Dict[str, Any]]:
    """List all registered plugins.

    Returns:
        A list of plugin signatures.
    """
    return default_registry.list_plugins()


def execute_plugin(name: str, **kwargs) -> Dict[str, Any]:
    """Execute a plugin.

    Args:
        name: The name of the plugin to execute.
        **kwargs: Arguments for the plugin.

    Returns:
        The result of the plugin execution.
    """
    return default_registry.execute_plugin(name, **kwargs)
