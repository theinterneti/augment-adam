"""
Plugin configuration.

This module provides configuration for plugins, allowing users to customize
plugin behavior.
"""

from augment_adam.plugins.config.base import (
    PluginConfig,
    PluginConfigSchema,
)

__all__ = [
    "PluginConfig",
    "PluginConfigSchema",
]
