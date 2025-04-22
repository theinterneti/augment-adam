"""Web interface for the Dukat assistant.

This package provides a web interface for the Dukat assistant.

Version: 0.1.0
Created: 2025-04-23
"""

from dukat.web.interface import (
    WebInterface,
    create_web_interface,
    launch_web_interface,
)

from dukat.web.plugin_manager import (
    PluginManagerUI,
    create_plugin_tab,
)

__all__ = [
    "WebInterface",
    "create_web_interface",
    "launch_web_interface",
    "PluginManagerUI",
    "create_plugin_tab",
]
