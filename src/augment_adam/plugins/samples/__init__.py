"""
Sample plugins.

This module provides sample plugins to demonstrate how to use the plugin system.
"""

from augment_adam.plugins.samples.hello_world import HelloWorldPlugin
from augment_adam.plugins.samples.text_processor import TextProcessorPlugin
from augment_adam.plugins.samples.logger import LoggerPlugin

__all__ = [
    "HelloWorldPlugin",
    "TextProcessorPlugin",
    "LoggerPlugin",
]
