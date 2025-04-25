"""Settings management for the Augment Adam web interface.

This module provides functionality for managing settings in the Augment Adam web interface.

Version: 0.1.0
Created: 2025-04-25
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Callable, Union

import gradio as gr

from augment_adam.core.settings import (
    Settings,
    SettingsScope,
    get_settings,
    update_settings,
    reset_settings,
)

logger = logging.getLogger(__name__)


class SettingsManagerUI:
    """UI component for managing settings in the web interface."""
    
    def __init__(self):
        """Initialize the settings manager UI."""
        self.settings = get_settings()
    
    def create_ui(self) -> Tuple[List[gr.Component], List[Callable]]:
        """Create the settings manager UI components.
        
        Returns:
            A tuple of (components, event_handlers).
        """
        # Settings scope selector
        scope_selector = gr.Radio(
            label="Settings Scope",
            choices=[scope.value for scope in SettingsScope],
            value=SettingsScope.USER.value,
        )
        
        # Settings display
        settings_display = gr.JSON(
            label="Current Settings",
            value=self._get_settings_dict(SettingsScope.USER),
        )
        
        # Settings editor
        settings_editor = gr.JSON(
            label="Edit Settings",
            value={},
        )
        
        # Buttons
        update_button = gr.Button("Update Settings")
        reset_button = gr.Button("Reset to Defaults")
        refresh_button = gr.Button("Refresh Settings")
        
        # Status message
        status_message = gr.Textbox(
            label="Status",
            value="",
        )
        
        # Set up event handlers
        event_handlers = [
            scope_selector.change(
                fn=self._get_settings_dict,
                inputs=[scope_selector],
                outputs=[settings_display],
            ),
            update_button.click(
                fn=self._update_settings,
                inputs=[scope_selector, settings_editor],
                outputs=[settings_display, status_message],
            ),
            reset_button.click(
                fn=self._reset_settings,
                inputs=[scope_selector],
                outputs=[settings_display, status_message],
            ),
            refresh_button.click(
                fn=self._get_settings_dict,
                inputs=[scope_selector],
                outputs=[settings_display],
            ),
        ]
        
        components = [
            scope_selector,
            settings_display,
            settings_editor,
            update_button,
            reset_button,
            refresh_button,
            status_message,
        ]
        
        return components, event_handlers
    
    def _get_settings_dict(self, scope: str) -> Dict[str, Any]:
        """Get settings as a dictionary.
        
        Args:
            scope: The settings scope.
            
        Returns:
            The settings as a dictionary.
        """
        try:
            # Convert string scope to enum
            scope_enum = SettingsScope(scope)
            
            # Get settings for the scope
            settings = get_settings(scope_enum)
            
            # Convert to dictionary
            return settings.model_dump()
        except Exception as e:
            logger.exception(f"Error getting settings: {str(e)}")
            return {"error": str(e)}
    
    def _update_settings(
        self,
        scope: str,
        settings_dict: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], str]:
        """Update settings.
        
        Args:
            scope: The settings scope.
            settings_dict: The settings to update.
            
        Returns:
            A tuple of (updated_settings, status_message).
        """
        try:
            # Convert string scope to enum
            scope_enum = SettingsScope(scope)
            
            # Update settings
            update_settings(settings_dict, scope=scope_enum)
            
            # Get updated settings
            updated_settings = get_settings(scope_enum).model_dump()
            
            return updated_settings, f"Settings updated successfully for scope: {scope}"
        except Exception as e:
            logger.exception(f"Error updating settings: {str(e)}")
            return self._get_settings_dict(scope), f"Error updating settings: {str(e)}"
    
    def _reset_settings(self, scope: str) -> Tuple[Dict[str, Any], str]:
        """Reset settings to defaults.
        
        Args:
            scope: The settings scope.
            
        Returns:
            A tuple of (reset_settings, status_message).
        """
        try:
            # Convert string scope to enum
            scope_enum = SettingsScope(scope)
            
            # Reset settings
            reset_settings(scope=scope_enum)
            
            # Get reset settings
            reset_settings_dict = get_settings(scope_enum).model_dump()
            
            return reset_settings_dict, f"Settings reset to defaults for scope: {scope}"
        except Exception as e:
            logger.exception(f"Error resetting settings: {str(e)}")
            return self._get_settings_dict(scope), f"Error resetting settings: {str(e)}"


def create_settings_tab() -> Tuple[gr.Tab, List[Callable]]:
    """Create a settings management tab for the web interface.
    
    Returns:
        A tuple of (tab, event_handlers).
    """
    settings_manager = SettingsManagerUI()
    
    with gr.Tab("Settings") as tab:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Settings Management")
                gr.Markdown("Select a scope and update settings.")
                
                components, event_handlers = settings_manager.create_ui()
    
    return tab, event_handlers
