"""
Unit tests for the Plugin interface.

This module contains tests for the Plugin interface, including plugin
registration, configuration, and execution.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.plugins.interface.base import Plugin, PluginResult, PluginConfig


class TestPlugin:
    """Tests for the Plugin interface."""

    def test_plugin_config_init(self):
        """Test initializing a PluginConfig."""
        config = PluginConfig(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            settings={"setting1": "value1"}
        )
        
        assert config.name == "test_plugin"
        assert config.version == "1.0.0"
        assert config.description == "Test plugin"
        assert config.settings == {"setting1": "value1"}
    
    def test_plugin_result_init(self):
        """Test initializing a PluginResult."""
        result = PluginResult(
            success=True,
            data={"key": "value"},
            message="Success"
        )
        
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.message == "Success"
    
    def test_plugin_result_to_dict(self):
        """Test converting a PluginResult to a dictionary."""
        result = PluginResult(
            success=True,
            data={"key": "value"},
            message="Success"
        )
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"] == {"key": "value"}
        assert result_dict["message"] == "Success"
    
    def test_plugin_init(self):
        """Test initializing a Plugin."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Test plugin"
        assert plugin.config is not None
    
    def test_plugin_init_with_config(self):
        """Test initializing a Plugin with a config."""
        config = PluginConfig(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            settings={"setting1": "value1"}
        )
        
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            config=config
        )
        
        assert plugin.config == config
        assert plugin.config.settings == {"setting1": "value1"}
    
    def test_plugin_get_config(self):
        """Test getting a Plugin's config."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        config = plugin.get_config()
        
        assert config.name == "test_plugin"
        assert config.version == "1.0.0"
        assert config.description == "Test plugin"
    
    def test_plugin_set_config(self):
        """Test setting a Plugin's config."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        new_config = PluginConfig(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            settings={"setting1": "value1"}
        )
        
        plugin.set_config(new_config)
        
        assert plugin.config == new_config
        assert plugin.config.settings == {"setting1": "value1"}
    
    def test_plugin_update_config(self):
        """Test updating a Plugin's config."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        plugin.update_config({"setting1": "value1"})
        
        assert plugin.config.settings == {"setting1": "value1"}
    
    def test_plugin_get_setting(self):
        """Test getting a Plugin's setting."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        plugin.update_config({"setting1": "value1"})
        
        assert plugin.get_setting("setting1") == "value1"
        assert plugin.get_setting("nonexistent") is None
        assert plugin.get_setting("nonexistent", "default") == "default"
    
    def test_plugin_set_setting(self):
        """Test setting a Plugin's setting."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        plugin.set_setting("setting1", "value1")
        
        assert plugin.config.settings["setting1"] == "value1"
    
    def test_plugin_execute(self):
        """Test executing a Plugin."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        # The base Plugin class doesn't implement execute
        with pytest.raises(NotImplementedError):
            plugin.execute()
    
    def test_plugin_validate(self):
        """Test validating a Plugin."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        # The base Plugin class doesn't implement validate
        with pytest.raises(NotImplementedError):
            plugin.validate()
    
    def test_plugin_get_info(self):
        """Test getting a Plugin's info."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        info = plugin.get_info()
        
        assert info["name"] == "test_plugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Test plugin"
        assert "config" in info
    
    def test_plugin_is_enabled(self):
        """Test checking if a Plugin is enabled."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        assert plugin.is_enabled() is True
        
        plugin.set_setting("enabled", False)
        
        assert plugin.is_enabled() is False
    
    def test_plugin_enable(self):
        """Test enabling a Plugin."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        plugin.set_setting("enabled", False)
        plugin.enable()
        
        assert plugin.is_enabled() is True
    
    def test_plugin_disable(self):
        """Test disabling a Plugin."""
        plugin = Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        plugin.disable()
        
        assert plugin.is_enabled() is False
