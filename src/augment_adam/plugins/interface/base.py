"""
Base classes for plugins.

This module provides the base classes for plugins, including the Plugin class
and related metadata classes.
"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, ClassVar

from augment_adam.utils.tagging import tag, TagCategory


class PluginType(enum.Enum):
    """
    Type of plugin.
    
    This enum defines the possible types of plugins.
    """
    
    AGENT = "agent"           # Plugin that extends agent capabilities
    CONTEXT = "context"       # Plugin that extends context processing
    MEMORY = "memory"         # Plugin that extends memory operations
    TOOL = "tool"             # Plugin that provides a tool
    UTILITY = "utility"       # Plugin that provides utility functions
    INTEGRATION = "integration"  # Plugin that integrates with external systems
    OTHER = "other"           # Other type of plugin


class PluginCategory(enum.Enum):
    """
    Category of plugin.
    
    This enum defines the possible categories of plugins.
    """
    
    CORE = "core"             # Core plugin provided by the system
    EXTENSION = "extension"   # Extension plugin provided by the system
    THIRD_PARTY = "third_party"  # Third-party plugin
    USER = "user"             # User-created plugin


class PluginHook(enum.Enum):
    """
    Hook for plugin execution.
    
    This enum defines the possible hooks for plugin execution.
    """
    
    INIT = "init"             # Called when the plugin is initialized
    PRE_PROCESS = "pre_process"  # Called before processing
    PROCESS = "process"       # Called during processing
    POST_PROCESS = "post_process"  # Called after processing
    CLEANUP = "cleanup"       # Called when the plugin is cleaned up


@dataclass
class PluginMetadata:
    """
    Metadata for a plugin.
    
    This class represents the metadata for a plugin, including its name,
    description, version, and other attributes.
    
    Attributes:
        name: The name of the plugin.
        description: A description of the plugin.
        version: The version of the plugin.
        author: The author of the plugin.
        plugin_type: The type of the plugin.
        category: The category of the plugin.
        hooks: The hooks that the plugin implements.
        dependencies: The dependencies of the plugin.
        tags: Tags for the plugin.
        metadata: Additional metadata for the plugin.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    name: str
    description: str
    version: str = "0.1.0"
    author: str = "Unknown"
    plugin_type: PluginType = PluginType.OTHER
    category: PluginCategory = PluginCategory.THIRD_PARTY
    hooks: Set[PluginHook] = field(default_factory=lambda: {PluginHook.PROCESS})
    dependencies: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@tag("plugins")
class Plugin(ABC):
    """
    Base class for plugins.
    
    This class defines the interface for plugins, which can extend and customize
    the assistant with various functionalities.
    
    Attributes:
        metadata: The metadata for the plugin.
        config: The configuration for the plugin.
        is_initialized: Whether the plugin is initialized.
        is_enabled: Whether the plugin is enabled.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    metadata: ClassVar[PluginMetadata]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the plugin.
        
        Args:
            config: The configuration for the plugin.
        """
        self.config = config or {}
        self.is_initialized = False
        self.is_enabled = True
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        if not self.is_initialized:
            self._initialize()
            self.is_initialized = True
    
    def cleanup(self) -> None:
        """Clean up the plugin."""
        if self.is_initialized:
            self._cleanup()
            self.is_initialized = False
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.is_enabled = True
    
    def disable(self) -> None:
        """Disable the plugin."""
        self.is_enabled = False
    
    def execute(self, hook: PluginHook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The result of execution.
        """
        if not self.is_enabled:
            return context
        
        if not self.is_initialized:
            self.initialize()
        
        if hook not in self.metadata.hooks:
            return context
        
        return self._execute(hook, context)
    
    @abstractmethod
    def _initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method should be implemented by subclasses to perform
        plugin-specific initialization.
        """
        pass
    
    @abstractmethod
    def _cleanup(self) -> None:
        """
        Clean up the plugin.
        
        This method should be implemented by subclasses to perform
        plugin-specific cleanup.
        """
        pass
    
    @abstractmethod
    def _execute(self, hook: PluginHook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        This method should be implemented by subclasses to perform
        plugin-specific execution.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The result of execution.
        """
        pass
