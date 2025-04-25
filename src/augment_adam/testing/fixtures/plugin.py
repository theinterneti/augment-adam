"""
Plugin fixtures for testing.

This module provides fixtures for testing plugin components, including plugin registry,
plugin loading, and plugin execution.
"""

import os
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.fixtures.base import Fixture, MockFixture


@tag("testing.fixtures")
class PluginFixture(Fixture):
    """
    Fixture for plugin components.
    
    This class provides fixtures for testing plugin components, including plugin registry,
    plugin loading, and plugin execution.
    
    Attributes:
        name: The name of the fixture.
        plugin_type: The type of plugin component to create.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the plugin component.
    
    TODO(Issue #13): Add support for more plugin types
    TODO(Issue #13): Implement plugin validation
    """
    
    def __init__(
        self,
        name: str = "plugin",
        plugin_type: str = "mock",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the plugin fixture.
        
        Args:
            name: The name of the fixture.
            plugin_type: The type of plugin component to create.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the plugin component.
        """
        super().__init__(name, scope, metadata)
        self.plugin_type = plugin_type
        self.config = config or {}
        self._plugin = None
    
    def setup(self) -> Any:
        """
        Set up the plugin component.
        
        Returns:
            The plugin component.
        """
        # Create the plugin component
        if self.plugin_type == "registry":
            from augment_adam.plugins.registry import PluginRegistry
            
            self._plugin = PluginRegistry(
                **self.config
            )
        elif self.plugin_type == "loader":
            from augment_adam.plugins.loader import PluginLoader
            
            self._plugin = PluginLoader(
                **self.config
            )
        elif self.plugin_type == "executor":
            from augment_adam.plugins.execution import PluginExecutor
            
            self._plugin = PluginExecutor(
                **self.config
            )
        elif self.plugin_type == "mock":
            import unittest.mock as mock
            
            self._plugin = mock.MagicMock()
            
            # Configure the mock
            for key, value in self.config.items():
                setattr(self._plugin, key, value)
        else:
            raise ValueError(f"Unknown plugin type: {self.plugin_type}")
        
        return self._plugin
    
    def teardown(self) -> None:
        """Clean up the plugin component."""
        if self._plugin is not None:
            # Clean up the plugin component
            if hasattr(self._plugin, "cleanup") and callable(self._plugin.cleanup):
                self._plugin.cleanup()
            
            self._plugin = None


@tag("testing.fixtures")
class MockPluginFixture(PluginFixture):
    """
    Fixture for mock plugin components.
    
    This class provides a fixture for testing with a mock plugin component.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the mock plugin component.
        responses: Predefined responses for the mock plugin component.
    
    TODO(Issue #13): Add support for mock plugin validation
    TODO(Issue #13): Implement mock plugin analytics
    """
    
    def __init__(
        self,
        name: str = "mock_plugin",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        responses: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the mock plugin fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the mock plugin component.
            responses: Predefined responses for the mock plugin component.
        """
        super().__init__(name, "mock", scope, metadata, config)
        self.responses = responses or {}
    
    def setup(self) -> Any:
        """
        Set up the mock plugin component.
        
        Returns:
            The mock plugin component.
        """
        # Create the mock plugin component
        plugin = super().setup()
        
        # Configure the mock plugin component with predefined responses
        for method, response in self.responses.items():
            getattr(plugin, method).return_value = response
        
        return plugin
