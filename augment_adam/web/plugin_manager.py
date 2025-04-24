"""Plugin management for the Dukat web interface.

This module provides functionality for managing plugins in the Dukat web interface.

Version: 0.1.0
Created: 2025-04-25
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Callable

import gradio as gr

from augment_adam.plugins import list_plugins, get_plugin, execute_plugin
from augment_adam.plugins.base import Plugin, PluginRegistry, get_plugin_registry

logger = logging.getLogger(__name__)


class PluginManagerUI:
    """UI component for managing plugins in the web interface."""
    
    def __init__(self, registry: Optional[PluginRegistry] = None):
        """Initialize the plugin manager UI.
        
        Args:
            registry: The plugin registry to use. If None, the default registry will be used.
        """
        self.registry = registry or get_plugin_registry()
    
    def create_ui(self) -> Tuple[List[gr.Component], List[Callable]]:
        """Create the plugin manager UI components.
        
        Returns:
            A tuple of (components, event_handlers).
        """
        # Plugin list
        plugin_list = gr.Dropdown(
            label="Available Plugins",
            choices=self._get_plugin_names(),
            value=None,
            interactive=True,
        )
        
        # Plugin details
        plugin_details = gr.JSON(
            label="Plugin Details",
            value={},
        )
        
        # Plugin execution
        plugin_params = gr.JSON(
            label="Plugin Parameters",
            value={},
        )
        
        execute_button = gr.Button("Execute Plugin")
        
        execution_result = gr.JSON(
            label="Execution Result",
            value={},
        )
        
        # Plugin management
        refresh_button = gr.Button("Refresh Plugins")
        
        # Set up event handlers
        event_handlers = [
            plugin_list.change(
                fn=self._get_plugin_details,
                inputs=[plugin_list],
                outputs=[plugin_details, plugin_params],
            ),
            execute_button.click(
                fn=self._execute_plugin,
                inputs=[plugin_list, plugin_params],
                outputs=[execution_result],
            ),
            refresh_button.click(
                fn=lambda: gr.update(choices=self._get_plugin_names()),
                inputs=[],
                outputs=[plugin_list],
            ),
        ]
        
        components = [
            plugin_list,
            plugin_details,
            plugin_params,
            execute_button,
            execution_result,
            refresh_button,
        ]
        
        return components, event_handlers
    
    def _get_plugin_names(self) -> List[str]:
        """Get the names of all registered plugins.
        
        Returns:
            A list of plugin names.
        """
        try:
            plugins = list_plugins()
            return [plugin["name"] for plugin in plugins]
        except Exception as e:
            logger.exception(f"Error getting plugin names: {str(e)}")
            return []
    
    def _get_plugin_details(self, plugin_name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get details for a plugin.
        
        Args:
            plugin_name: The name of the plugin.
            
        Returns:
            A tuple of (plugin_details, default_params).
        """
        if not plugin_name:
            return {}, {}
        
        try:
            # Get the plugin
            plugin = get_plugin(plugin_name)
            
            if not plugin:
                return {"error": f"Plugin {plugin_name} not found"}, {}
            
            # Get the plugin signature
            signature = plugin.get_signature()
            
            # Create default parameters
            default_params = {}
            for param_name, param_info in signature.get("parameters", {}).items():
                default_params[param_name] = param_info.get("default")
            
            return signature, default_params
            
        except Exception as e:
            logger.exception(f"Error getting plugin details: {str(e)}")
            return {"error": str(e)}, {}
    
    def _execute_plugin(
        self,
        plugin_name: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a plugin.
        
        Args:
            plugin_name: The name of the plugin.
            params: The parameters for the plugin.
            
        Returns:
            The result of the plugin execution.
        """
        if not plugin_name:
            return {"error": "No plugin selected"}
        
        try:
            # Execute the plugin
            result = execute_plugin(plugin_name, **params)
            return result
            
        except Exception as e:
            logger.exception(f"Error executing plugin: {str(e)}")
            return {"error": str(e)}


def create_plugin_tab(registry: Optional[PluginRegistry] = None) -> Tuple[gr.Tab, List[Callable]]:
    """Create a plugin management tab for the web interface.
    
    Args:
        registry: The plugin registry to use. If None, the default registry will be used.
        
    Returns:
        A tuple of (tab, event_handlers).
    """
    plugin_manager = PluginManagerUI(registry)
    
    with gr.Tab("Plugins") as tab:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Plugin Management")
                gr.Markdown("Select a plugin to view details and execute it.")
                
                components, event_handlers = plugin_manager.create_ui()
    
    return tab, event_handlers
