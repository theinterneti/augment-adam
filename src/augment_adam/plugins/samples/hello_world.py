"""
Hello World plugin.

This module provides a simple Hello World plugin to demonstrate the plugin system.
"""

from typing import Dict, Any

from augment_adam.plugins.interface import Plugin, PluginMetadata, PluginType, PluginCategory, PluginHook


class HelloWorldPlugin(Plugin):
    """
    Hello World plugin.
    
    This plugin simply adds a greeting message to the context.
    """
    
    metadata = PluginMetadata(
        name="hello_world",
        description="A simple Hello World plugin",
        version="0.1.0",
        author="Augment Adam",
        plugin_type=PluginType.UTILITY,
        category=PluginCategory.CORE,
        hooks={PluginHook.PROCESS},
        tags=["sample", "hello", "greeting"],
    )
    
    def _initialize(self) -> None:
        """Initialize the plugin."""
        # Get greeting from config, or use default
        self.greeting = self.config.get("greeting", "Hello, World!")
    
    def _cleanup(self) -> None:
        """Clean up the plugin."""
        pass
    
    def _execute(self, hook: PluginHook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The updated context.
        """
        # Add greeting to context
        context["greeting"] = self.greeting
        
        return context
