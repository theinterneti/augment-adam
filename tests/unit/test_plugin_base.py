"""Unit tests for the base plugin system.

This module contains tests for the base plugin system functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import pytest
import logging
from typing import Dict, Any

from augment_adam.plugins.base import Plugin, PluginRegistry, get_plugin_registry


class TestPlugin(Plugin):
    """Test plugin implementation for testing."""
    
    def __init__(
        self,
        name: str = "test_plugin",
        description: str = "Test plugin for testing",
        version: str = "0.1.0",
    ):
        """Initialize the test plugin."""
        super().__init__(name=name, description=description, version=version)
    
    def execute(self, param1: str = "default", param2: int = 0) -> Dict[str, Any]:
        """Execute the test plugin.
        
        Args:
            param1: A string parameter.
            param2: An integer parameter.
            
        Returns:
            A dictionary with the parameters.
        """
        return {
            "param1": param1,
            "param2": param2,
        }


class ErrorPlugin(Plugin):
    """Test plugin that raises an error when executed."""
    
    def __init__(
        self,
        name: str = "error_plugin",
        description: str = "Plugin that raises an error",
        version: str = "0.1.0",
    ):
        """Initialize the error plugin."""
        super().__init__(name=name, description=description, version=version)
    
    def execute(self) -> Dict[str, Any]:
        """Execute the error plugin.
        
        Raises:
            ValueError: Always raises this error.
            
        Returns:
            Never returns.
        """
        raise ValueError("This plugin always fails")


def test_plugin_init():
    """Test plugin initialization."""
    plugin = TestPlugin(name="test", description="Test description", version="1.0.0")
    
    assert plugin.name == "test"
    assert plugin.description == "Test description"
    assert plugin.version == "1.0.0"


def test_plugin_execute():
    """Test plugin execution."""
    plugin = TestPlugin()
    
    # Test with default parameters
    result = plugin.execute()
    assert result["param1"] == "default"
    assert result["param2"] == 0
    
    # Test with custom parameters
    result = plugin.execute(param1="custom", param2=42)
    assert result["param1"] == "custom"
    assert result["param2"] == 42


def test_plugin_get_signature():
    """Test getting plugin signature."""
    plugin = TestPlugin()
    
    signature = plugin.get_signature()
    
    assert signature["name"] == "test_plugin"
    assert signature["description"] == "Test plugin for testing"
    assert signature["version"] == "0.1.0"
    
    # Check parameters
    assert "param1" in signature["parameters"]
    assert "param2" in signature["parameters"]
    
    # Check parameter details
    assert signature["parameters"]["param1"]["name"] == "param1"
    assert signature["parameters"]["param1"]["required"] is False
    assert signature["parameters"]["param1"]["default"] == "default"
    
    assert signature["parameters"]["param2"]["name"] == "param2"
    assert signature["parameters"]["param2"]["required"] is False
    assert signature["parameters"]["param2"]["default"] == 0


def test_registry_init():
    """Test registry initialization."""
    registry = PluginRegistry()
    
    assert registry.plugins == {}


def test_registry_register():
    """Test registering a plugin."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    
    # Register the plugin
    result = registry.register(plugin)
    
    assert result is True
    assert "test_plugin" in registry.plugins
    assert registry.plugins["test_plugin"] is plugin


def test_registry_register_invalid():
    """Test registering an invalid plugin."""
    registry = PluginRegistry()
    
    # Try to register something that's not a plugin
    result = registry.register("not a plugin")
    
    assert result is False
    assert len(registry.plugins) == 0


def test_registry_register_duplicate():
    """Test registering a duplicate plugin."""
    registry = PluginRegistry()
    plugin1 = TestPlugin(name="duplicate")
    plugin2 = TestPlugin(name="duplicate", version="2.0.0")
    
    # Register the first plugin
    registry.register(plugin1)
    
    # Register the second plugin with the same name
    result = registry.register(plugin2)
    
    assert result is True
    assert "duplicate" in registry.plugins
    assert registry.plugins["duplicate"] is plugin2  # Should overwrite


def test_registry_unregister():
    """Test unregistering a plugin."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    
    # Register the plugin
    registry.register(plugin)
    
    # Unregister the plugin
    result = registry.unregister("test_plugin")
    
    assert result is True
    assert "test_plugin" not in registry.plugins


def test_registry_unregister_nonexistent():
    """Test unregistering a nonexistent plugin."""
    registry = PluginRegistry()
    
    # Try to unregister a plugin that doesn't exist
    result = registry.unregister("nonexistent")
    
    assert result is False


def test_registry_get_plugin():
    """Test getting a plugin."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    
    # Register the plugin
    registry.register(plugin)
    
    # Get the plugin
    result = registry.get_plugin("test_plugin")
    
    assert result is plugin


def test_registry_get_nonexistent_plugin():
    """Test getting a nonexistent plugin."""
    registry = PluginRegistry()
    
    # Try to get a plugin that doesn't exist
    result = registry.get_plugin("nonexistent")
    
    assert result is None


def test_registry_list_plugins():
    """Test listing plugins."""
    registry = PluginRegistry()
    plugin1 = TestPlugin(name="plugin1")
    plugin2 = TestPlugin(name="plugin2")
    
    # Register the plugins
    registry.register(plugin1)
    registry.register(plugin2)
    
    # List the plugins
    result = registry.list_plugins()
    
    assert len(result) == 2
    assert any(p["name"] == "plugin1" for p in result)
    assert any(p["name"] == "plugin2" for p in result)


def test_registry_execute_plugin():
    """Test executing a plugin."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    
    # Register the plugin
    registry.register(plugin)
    
    # Execute the plugin
    result = registry.execute_plugin("test_plugin", param1="executed", param2=99)
    
    assert result["param1"] == "executed"
    assert result["param2"] == 99


def test_registry_execute_nonexistent_plugin():
    """Test executing a nonexistent plugin."""
    registry = PluginRegistry()
    
    # Try to execute a plugin that doesn't exist
    result = registry.execute_plugin("nonexistent")
    
    assert "error" in result
    assert "not found" in result["error"]


def test_registry_execute_error_plugin():
    """Test executing a plugin that raises an error."""
    registry = PluginRegistry()
    plugin = ErrorPlugin()
    
    # Register the plugin
    registry.register(plugin)
    
    # Execute the plugin
    result = registry.execute_plugin("error_plugin")
    
    assert "error" in result
    assert "This plugin always fails" in result["error"]


def test_get_plugin_registry():
    """Test getting the default plugin registry."""
    # Reset the default registry
    import augment_adam.plugins.base
    augment_adam.plugins.base.default_registry = None
    
    # Get the registry
    registry1 = get_plugin_registry()
    
    assert isinstance(registry1, PluginRegistry)
    
    # Get the registry again
    registry2 = get_plugin_registry()
    
    assert registry2 is registry1  # Should be the same instance
