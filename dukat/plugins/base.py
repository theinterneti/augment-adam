"""Base plugin system for the Dukat assistant.

This module provides the base classes and interfaces for
creating plugins for the Dukat assistant.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Callable, Type
import logging
import inspect
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Base class for all Dukat plugins.
    
    This abstract class defines the interface that all plugins must implement.
    
    Attributes:
        name: The name of the plugin.
        description: A description of the plugin.
        version: The version of the plugin.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "0.1.0",
    ):
        """Initialize the plugin.
        
        Args:
            name: The name of the plugin.
            description: A description of the plugin.
            version: The version of the plugin.
        """
        self.name = name
        self.description = description
        self.version = version
        
        logger.info(f"Initialized plugin: {name} v{version}")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the plugin with the given arguments.
        
        Args:
            **kwargs: Arguments for the plugin.
            
        Returns:
            The result of the plugin execution.
        """
        pass
    
    def get_signature(self) -> Dict[str, Any]:
        """Get the signature of the plugin.
        
        Returns:
            A dictionary describing the plugin's signature.
        """
        # Get the signature of the execute method
        sig = inspect.signature(self.execute)
        
        # Extract parameter information
        parameters = {}
        for name, param in sig.parameters.items():
            if name != "self":
                parameters[name] = {
                    "name": name,
                    "required": param.default == inspect.Parameter.empty,
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": None if param.default == inspect.Parameter.empty else param.default,
                }
        
        # Return the signature
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": parameters,
        }


class PluginRegistry:
    """Registry for Dukat plugins.
    
    This class manages the registration and discovery of plugins.
    
    Attributes:
        plugins: Dictionary of registered plugins.
    """
    
    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, Plugin] = {}
        logger.info("Initialized plugin registry")
    
    def register(self, plugin: Plugin) -> bool:
        """Register a plugin.
        
        Args:
            plugin: The plugin to register.
            
        Returns:
            True if successful, False otherwise.
        """
        if not isinstance(plugin, Plugin):
            logger.error(f"Cannot register {plugin}: not a Plugin instance")
            return False
        
        if plugin.name in self.plugins:
            logger.warning(f"Plugin {plugin.name} already registered, overwriting")
        
        self.plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
        return True
    
    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin.
        
        Args:
            plugin_name: The name of the plugin to unregister.
            
        Returns:
            True if successful, False otherwise.
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} not registered")
            return False
        
        del self.plugins[plugin_name]
        logger.info(f"Unregistered plugin: {plugin_name}")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            plugin_name: The name of the plugin to get.
            
        Returns:
            The plugin, or None if not found.
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins.
        
        Returns:
            A list of plugin signatures.
        """
        return [plugin.get_signature() for plugin in self.plugins.values()]
    
    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a plugin.
        
        Args:
            plugin_name: The name of the plugin to execute.
            **kwargs: Arguments for the plugin.
            
        Returns:
            The result of the plugin execution.
        """
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            logger.error(f"Plugin {plugin_name} not found")
            return {"error": f"Plugin {plugin_name} not found"}
        
        try:
            result = plugin.execute(**kwargs)
            return result
        
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}: {str(e)}")
            return {"error": f"Error executing plugin {plugin_name}: {str(e)}"}


# Singleton instance for easy access
default_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get or create the default plugin registry.
    
    Returns:
        The default plugin registry.
    """
    global default_registry
    
    if default_registry is None:
        default_registry = PluginRegistry()
    
    return default_registry
