"""
Logger plugin.

This module provides a Logger plugin to demonstrate the plugin system.
"""

import os
import time
from typing import Dict, Any, Optional, TextIO

from augment_adam.plugins.interface import Plugin, PluginMetadata, PluginType, PluginCategory, PluginHook


class LoggerPlugin(Plugin):
    """
    Logger plugin.
    
    This plugin logs context data to a file.
    """
    
    metadata = PluginMetadata(
        name="logger",
        description="A plugin for logging context data",
        version="0.1.0",
        author="Augment Adam",
        plugin_type=PluginType.UTILITY,
        category=PluginCategory.CORE,
        hooks={PluginHook.INIT, PluginHook.PRE_PROCESS, PluginHook.PROCESS, PluginHook.POST_PROCESS, PluginHook.CLEANUP},
        tags=["sample", "logger", "utility"],
    )
    
    def _initialize(self) -> None:
        """Initialize the plugin."""
        # Get configuration options, or use defaults
        self.log_file = self.config.get("log_file", "plugin_log.txt")
        self.log_level = self.config.get("log_level", "INFO")
        self.log_format = self.config.get("log_format", "[{timestamp}] [{level}] {message}")
        
        # Create log file directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.log_file)), exist_ok=True)
        
        # Open log file
        self.file: Optional[TextIO] = open(self.log_file, "a")
        
        # Log initialization
        self._log("INIT", "Logger plugin initialized")
    
    def _cleanup(self) -> None:
        """Clean up the plugin."""
        # Log cleanup
        self._log("CLEANUP", "Logger plugin cleaned up")
        
        # Close log file
        if self.file is not None:
            self.file.close()
            self.file = None
    
    def _execute(self, hook: PluginHook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The updated context.
        """
        # Log hook execution
        self._log(hook.value.upper(), f"Executing hook: {hook.value}")
        
        # Log context data
        for key, value in context.items():
            self._log(hook.value.upper(), f"Context[{key}] = {value}")
        
        return context
    
    def _log(self, level: str, message: str) -> None:
        """
        Log a message.
        
        Args:
            level: The log level.
            message: The message to log.
        """
        # Check if log level is enabled
        if self._is_level_enabled(level):
            # Format log message
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_message = self.log_format.format(
                timestamp=timestamp,
                level=level,
                message=message
            )
            
            # Write to log file
            if self.file is not None:
                self.file.write(log_message + "\n")
                self.file.flush()
    
    def _is_level_enabled(self, level: str) -> bool:
        """
        Check if a log level is enabled.
        
        Args:
            level: The log level to check.
            
        Returns:
            True if the log level is enabled, False otherwise.
        """
        # Define log level priorities
        level_priorities = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }
        
        # Get priority of current level
        current_priority = level_priorities.get(self.log_level, 0)
        
        # Get priority of level to check
        level_priority = level_priorities.get(level, 0)
        
        # Check if level is enabled
        return level_priority >= current_priority
