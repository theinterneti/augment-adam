"""
Base classes for plugin execution.

This module provides the base classes for plugin execution, which handles
plugin execution and lifecycle management.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.plugins.interface import Plugin, PluginHook
from augment_adam.plugins.registry import PluginRegistry


@dataclass
class PluginContext:
    """
    Context for plugin execution.
    
    This class represents the context for plugin execution, including input data,
    output data, and metadata.
    
    Attributes:
        input_data: The input data for the plugin.
        output_data: The output data from the plugin.
        metadata: Additional metadata for the context.
    
    TODO(Issue #11): Add support for context validation
    TODO(Issue #11): Implement context analytics
    """
    
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the context.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the context.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@dataclass
class PluginResult:
    """
    Result of plugin execution.
    
    This class represents the result of plugin execution, including the output
    data, execution time, and metadata.
    
    Attributes:
        output_data: The output data from the plugin.
        execution_time: The time it took to execute the plugin.
        metadata: Additional metadata for the result.
    
    TODO(Issue #11): Add support for result validation
    TODO(Issue #11): Implement result analytics
    """
    
    output_data: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the result.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the result.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("plugins.execution")
class PluginExecutor:
    """
    Executor for plugins.
    
    This class handles plugin execution and lifecycle management, including
    initializing, executing, and cleaning up plugins.
    
    Attributes:
        registry: The plugin registry to get plugins from.
        plugins: Dictionary of plugin instances, keyed by name.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    def __init__(self, registry: Optional[PluginRegistry] = None) -> None:
        """
        Initialize the plugin executor.
        
        Args:
            registry: The plugin registry to get plugins from. If None, use the default registry.
        """
        self.registry = registry or PluginRegistry()
        self.plugins: Dict[str, Plugin] = {}
    
    def initialize_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize a plugin.
        
        Args:
            plugin_name: The name of the plugin to initialize.
            config: The configuration for the plugin.
            
        Returns:
            True if the plugin was initialized, False otherwise.
        """
        # Check if plugin is already initialized
        if plugin_name in self.plugins:
            return True
        
        # Get plugin class
        plugin_class = self.registry.get_plugin(plugin_name)
        if plugin_class is None:
            return False
        
        try:
            # Create plugin instance
            plugin = plugin_class(config)
            
            # Initialize plugin
            plugin.initialize()
            
            # Store plugin instance
            self.plugins[plugin_name] = plugin
            
            return True
        except Exception as e:
            print(f"Error initializing plugin {plugin_name}: {e}")
            return False
    
    def cleanup_plugin(self, plugin_name: str) -> bool:
        """
        Clean up a plugin.
        
        Args:
            plugin_name: The name of the plugin to clean up.
            
        Returns:
            True if the plugin was cleaned up, False otherwise.
        """
        # Check if plugin is initialized
        if plugin_name not in self.plugins:
            return False
        
        try:
            # Get plugin instance
            plugin = self.plugins[plugin_name]
            
            # Clean up plugin
            plugin.cleanup()
            
            # Remove plugin instance
            del self.plugins[plugin_name]
            
            return True
        except Exception as e:
            print(f"Error cleaning up plugin {plugin_name}: {e}")
            return False
    
    def execute_plugin(
        self,
        plugin_name: str,
        hook: PluginHook,
        context: Optional[PluginContext] = None
    ) -> PluginResult:
        """
        Execute a plugin.
        
        Args:
            plugin_name: The name of the plugin to execute.
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The result of execution.
        """
        # Create default context if none provided
        if context is None:
            context = PluginContext()
        
        # Initialize plugin if not already initialized
        if plugin_name not in self.plugins:
            plugin_class = self.registry.get_plugin(plugin_name)
            if plugin_class is None:
                return PluginResult(
                    output_data=context.output_data,
                    execution_time=0.0,
                    metadata={"error": f"Plugin '{plugin_name}' not found"}
                )
            
            if not self.initialize_plugin(plugin_name):
                return PluginResult(
                    output_data=context.output_data,
                    execution_time=0.0,
                    metadata={"error": f"Failed to initialize plugin '{plugin_name}'"}
                )
        
        # Get plugin instance
        plugin = self.plugins[plugin_name]
        
        try:
            # Execute plugin
            start_time = time.time()
            result = plugin.execute(hook, context.input_data)
            execution_time = time.time() - start_time
            
            # Create result
            return PluginResult(
                output_data=result,
                execution_time=execution_time
            )
        except Exception as e:
            return PluginResult(
                output_data=context.output_data,
                execution_time=0.0,
                metadata={"error": str(e)}
            )
    
    def execute_plugins(
        self,
        hook: PluginHook,
        context: Optional[PluginContext] = None
    ) -> Dict[str, PluginResult]:
        """
        Execute all plugins for a hook.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            Dictionary mapping plugin names to results.
        """
        # Create default context if none provided
        if context is None:
            context = PluginContext()
        
        # Get plugins for the hook
        plugin_classes = self.registry.get_plugins_by_hook(hook)
        
        # Execute plugins
        results = {}
        for plugin_class in plugin_classes:
            plugin_name = plugin_class.metadata.name
            results[plugin_name] = self.execute_plugin(plugin_name, hook, context)
        
        return results
    
    def execute_pipeline(
        self,
        hook: PluginHook,
        context: Optional[PluginContext] = None
    ) -> PluginResult:
        """
        Execute a pipeline of plugins for a hook.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The result of the pipeline.
        """
        # Create default context if none provided
        if context is None:
            context = PluginContext()
        
        # Get plugins for the hook
        plugin_classes = self.registry.get_plugins_by_hook(hook)
        
        # Execute plugins in a pipeline
        current_context = context
        total_execution_time = 0.0
        
        for plugin_class in plugin_classes:
            plugin_name = plugin_class.metadata.name
            
            # Execute plugin
            result = self.execute_plugin(plugin_name, hook, current_context)
            
            # Update context
            current_context = PluginContext(
                input_data=result.output_data,
                output_data=result.output_data,
                metadata=current_context.metadata
            )
            
            # Update execution time
            total_execution_time += result.execution_time
        
        # Create result
        return PluginResult(
            output_data=current_context.output_data,
            execution_time=total_execution_time
        )
    
    def cleanup_all_plugins(self) -> None:
        """Clean up all plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.cleanup_plugin(plugin_name)
