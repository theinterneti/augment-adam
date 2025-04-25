"""
Base classes for plugin validation.

This module provides the base classes for plugin validation, ensuring plugins
meet security and compatibility requirements.
"""

import os
import inspect
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.plugins.interface import Plugin


@tag("plugins.validation")
class PluginValidator(ABC):
    """
    Base class for plugin validators.
    
    This class defines the interface for plugin validators, which ensure plugins
    meet certain requirements.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement validator analytics
    """
    
    @abstractmethod
    def validate(self, plugin_class: Type[Plugin]) -> bool:
        """
        Validate a plugin.
        
        Args:
            plugin_class: The plugin class to validate.
            
        Returns:
            True if the plugin is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_validation_errors(self, plugin_class: Type[Plugin]) -> List[str]:
        """
        Get validation errors for a plugin.
        
        Args:
            plugin_class: The plugin class to validate.
            
        Returns:
            List of validation error messages.
        """
        pass


@tag("plugins.validation")
class SecurityValidator(PluginValidator):
    """
    Validator for plugin security.
    
    This class validates plugins for security, ensuring they don't use
    dangerous functions or modules.
    
    Attributes:
        forbidden_modules: Set of forbidden module names.
        forbidden_functions: Set of forbidden function names.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement validator analytics
    """
    
    def __init__(
        self,
        forbidden_modules: Optional[Set[str]] = None,
        forbidden_functions: Optional[Set[str]] = None
    ) -> None:
        """
        Initialize the security validator.
        
        Args:
            forbidden_modules: Set of forbidden module names.
            forbidden_functions: Set of forbidden function names.
        """
        self.forbidden_modules = forbidden_modules or {
            "os.system",
            "subprocess",
            "eval",
            "exec",
            "compile",
        }
        
        self.forbidden_functions = forbidden_functions or {
            "os.system",
            "os.popen",
            "os.spawn",
            "os.exec",
            "subprocess.run",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
            "subprocess.Popen",
            "eval",
            "exec",
            "compile",
        }
    
    def validate(self, plugin_class: Type[Plugin]) -> bool:
        """
        Validate a plugin for security.
        
        Args:
            plugin_class: The plugin class to validate.
            
        Returns:
            True if the plugin is secure, False otherwise.
        """
        return len(self.get_validation_errors(plugin_class)) == 0
    
    def get_validation_errors(self, plugin_class: Type[Plugin]) -> List[str]:
        """
        Get security validation errors for a plugin.
        
        Args:
            plugin_class: The plugin class to validate.
            
        Returns:
            List of security validation error messages.
        """
        errors = []
        
        # Get source code
        try:
            source = inspect.getsource(plugin_class)
        except Exception:
            errors.append("Could not get source code for plugin")
            return errors
        
        # Check for forbidden modules
        for module in self.forbidden_modules:
            if f"import {module}" in source or f"from {module}" in source:
                errors.append(f"Plugin uses forbidden module: {module}")
        
        # Check for forbidden functions
        for function in self.forbidden_functions:
            if function in source:
                errors.append(f"Plugin uses forbidden function: {function}")
        
        return errors


@tag("plugins.validation")
class CompatibilityValidator(PluginValidator):
    """
    Validator for plugin compatibility.
    
    This class validates plugins for compatibility, ensuring they implement
    the required interface and have the required metadata.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement validator analytics
    """
    
    def validate(self, plugin_class: Type[Plugin]) -> bool:
        """
        Validate a plugin for compatibility.
        
        Args:
            plugin_class: The plugin class to validate.
            
        Returns:
            True if the plugin is compatible, False otherwise.
        """
        return len(self.get_validation_errors(plugin_class)) == 0
    
    def get_validation_errors(self, plugin_class: Type[Plugin]) -> List[str]:
        """
        Get compatibility validation errors for a plugin.
        
        Args:
            plugin_class: The plugin class to validate.
            
        Returns:
            List of compatibility validation error messages.
        """
        errors = []
        
        # Check if plugin is a subclass of Plugin
        if not issubclass(plugin_class, Plugin):
            errors.append("Plugin class must be a subclass of Plugin")
            return errors
        
        # Check if plugin has metadata
        if not hasattr(plugin_class, "metadata"):
            errors.append("Plugin class must have metadata")
            return errors
        
        # Check if plugin has required metadata attributes
        metadata = plugin_class.metadata
        
        if not hasattr(metadata, "name") or not metadata.name:
            errors.append("Plugin metadata must have a name")
        
        if not hasattr(metadata, "description") or not metadata.description:
            errors.append("Plugin metadata must have a description")
        
        if not hasattr(metadata, "version") or not metadata.version:
            errors.append("Plugin metadata must have a version")
        
        if not hasattr(metadata, "hooks") or not metadata.hooks:
            errors.append("Plugin metadata must have at least one hook")
        
        # Check if plugin implements required methods
        if not hasattr(plugin_class, "_initialize") or not callable(getattr(plugin_class, "_initialize")):
            errors.append("Plugin class must implement _initialize method")
        
        if not hasattr(plugin_class, "_cleanup") or not callable(getattr(plugin_class, "_cleanup")):
            errors.append("Plugin class must implement _cleanup method")
        
        if not hasattr(plugin_class, "_execute") or not callable(getattr(plugin_class, "_execute")):
            errors.append("Plugin class must implement _execute method")
        
        return errors
