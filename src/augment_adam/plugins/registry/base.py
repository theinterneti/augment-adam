"""
Base classes for plugin registry.

This module provides the base classes for the plugin registry, which tracks
available plugins and their capabilities.
"""

import threading
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.plugins.interface import Plugin, PluginType, PluginCategory, PluginHook


@tag("plugins.registry")
class PluginRegistry:
    """
    Registry for plugins.
    
    This class tracks available plugins and their capabilities, providing
    methods for registering, unregistering, and querying plugins.
    
    Attributes:
        plugins: Dictionary of registered plugins, keyed by name.
        plugin_types: Dictionary of plugins by type.
        plugin_categories: Dictionary of plugins by category.
        plugin_hooks: Dictionary of plugins by hook.
        lock: Lock for thread safety.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a new instance of the registry, or return the existing one."""
        if cls._instance is None:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return
        
        self.plugins: Dict[str, Type[Plugin]] = {}
        self.plugin_types: Dict[PluginType, List[str]] = {
            plugin_type: [] for plugin_type in PluginType
        }
        self.plugin_categories: Dict[PluginCategory, List[str]] = {
            category: [] for category in PluginCategory
        }
        self.plugin_hooks: Dict[PluginHook, List[str]] = {
            hook: [] for hook in PluginHook
        }
        self.lock = threading.RLock()
        
        self._initialized = True
    
    def register(self, plugin_class: Type[Plugin]) -> None:
        """
        Register a plugin.
        
        Args:
            plugin_class: The plugin class to register.
            
        Raises:
            ValueError: If a plugin with the same name is already registered.
        """
        with self.lock:
            # Get plugin metadata
            metadata = plugin_class.metadata
            
            # Check if plugin is already registered
            if metadata.name in self.plugins:
                raise ValueError(f"Plugin '{metadata.name}' is already registered")
            
            # Register plugin
            self.plugins[metadata.name] = plugin_class
            
            # Update indices
            self.plugin_types[metadata.plugin_type].append(metadata.name)
            self.plugin_categories[metadata.category].append(metadata.name)
            
            for hook in metadata.hooks:
                self.plugin_hooks[hook].append(metadata.name)
    
    def unregister(self, plugin_name: str) -> None:
        """
        Unregister a plugin.
        
        Args:
            plugin_name: The name of the plugin to unregister.
            
        Raises:
            ValueError: If the plugin is not registered.
        """
        with self.lock:
            # Check if plugin is registered
            if plugin_name not in self.plugins:
                raise ValueError(f"Plugin '{plugin_name}' is not registered")
            
            # Get plugin metadata
            plugin_class = self.plugins[plugin_name]
            metadata = plugin_class.metadata
            
            # Unregister plugin
            del self.plugins[plugin_name]
            
            # Update indices
            self.plugin_types[metadata.plugin_type].remove(plugin_name)
            self.plugin_categories[metadata.category].remove(plugin_name)
            
            for hook in metadata.hooks:
                self.plugin_hooks[hook].remove(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[Type[Plugin]]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: The name of the plugin.
            
        Returns:
            The plugin class, or None if not found.
        """
        with self.lock:
            return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Type[Plugin]]:
        """
        Get plugins by type.
        
        Args:
            plugin_type: The type of plugins to get.
            
        Returns:
            List of plugin classes.
        """
        with self.lock:
            return [self.plugins[name] for name in self.plugin_types[plugin_type]]
    
    def get_plugins_by_category(self, category: PluginCategory) -> List[Type[Plugin]]:
        """
        Get plugins by category.
        
        Args:
            category: The category of plugins to get.
            
        Returns:
            List of plugin classes.
        """
        with self.lock:
            return [self.plugins[name] for name in self.plugin_categories[category]]
    
    def get_plugins_by_hook(self, hook: PluginHook) -> List[Type[Plugin]]:
        """
        Get plugins by hook.
        
        Args:
            hook: The hook to get plugins for.
            
        Returns:
            List of plugin classes.
        """
        with self.lock:
            return [self.plugins[name] for name in self.plugin_hooks[hook]]
    
    def get_all_plugins(self) -> List[Type[Plugin]]:
        """
        Get all registered plugins.
        
        Returns:
            List of all plugin classes.
        """
        with self.lock:
            return list(self.plugins.values())
    
    def clear(self) -> None:
        """Clear the registry."""
        with self.lock:
            self.plugins.clear()
            
            for plugin_type in PluginType:
                self.plugin_types[plugin_type].clear()
            
            for category in PluginCategory:
                self.plugin_categories[category].clear()
            
            for hook in PluginHook:
                self.plugin_hooks[hook].clear()
