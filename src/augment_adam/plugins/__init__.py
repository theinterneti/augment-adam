"""
Plugin System.

This module provides a flexible plugin system that allows users to extend and
customize the assistant with plugins for various functionalities.

TODO(Issue #11): Add plugin marketplace
TODO(Issue #11): Implement plugin versioning
TODO(Issue #11): Add plugin analytics
"""

from augment_adam.plugins.interface import (
    Plugin,
    PluginMetadata,
    PluginType,
    PluginCategory,
    PluginHook,
)

from augment_adam.plugins.registry import (
    PluginRegistry,
)

from augment_adam.plugins.loader import (
    PluginLoader,
    PluginDiscovery,
    EntryPointDiscovery,
    DirectoryDiscovery,
)

from augment_adam.plugins.execution import (
    PluginExecutor,
    PluginContext,
    PluginResult,
)

from augment_adam.plugins.validation import (
    PluginValidator,
    SecurityValidator,
    CompatibilityValidator,
)

from augment_adam.plugins.config import (
    PluginConfig,
    PluginConfigSchema,
)

__all__ = [
    # Interface
    "Plugin",
    "PluginMetadata",
    "PluginType",
    "PluginCategory",
    "PluginHook",

    # Registry
    "PluginRegistry",

    # Loader
    "PluginLoader",
    "PluginDiscovery",
    "EntryPointDiscovery",
    "DirectoryDiscovery",

    # Execution
    "PluginExecutor",
    "PluginContext",
    "PluginResult",

    # Validation
    "PluginValidator",
    "SecurityValidator",
    "CompatibilityValidator",

    # Config
    "PluginConfig",
    "PluginConfigSchema",
]