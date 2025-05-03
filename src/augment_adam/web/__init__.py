"""Web interface for Augment Adam.

This module provides web-based interfaces for interacting with Augment Adam,
including a chat interface, visualization tools, and management interfaces.

Version: 0.1.0
Created: 2023-05-01
"""

from augment_adam.web.interface import WebInterface, create_web_interface, launch_web_interface

__all__ = [
    "WebInterface",
    "create_web_interface",
    "launch_web_interface",
]