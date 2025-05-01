"""
Unit tests for the Plugin registry.

This module contains tests for the Plugin registry, including plugin
registration, retrieval, and management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.plugins.interface.base import Plugin, PluginConfig
from augment_adam.plugins.registry.base import PluginRegistry


class TestPluginRegistry:
    """Tests for the Plugin registry."""

    @pytest.fixture
    def registry(self):
        """Create a PluginRegistry for testing."""
        return PluginRegistry()
    
    @pytest.fixture
    def test_plugin(self):
        """Create a test Plugin for testing."""
        return Plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
    
    def test_registry_init(self, registry):
        """Test initializing a PluginRegistry."""
        assert registry.plugins == {}
    
    def test_register_plugin(self, registry, test_plugin):
        """Test registering a Plugin."""
        registry.register_plugin(test_plugin)
        
        assert "test_plugin" in registry.plugins
        assert registry.plugins["test_plugin"] == test_plugin
    
    def test_register_plugin_duplicate(self, registry, test_plugin):
        """Test registering a duplicate Plugin."""
        registry.register_plugin(test_plugin)
        
        # Should raise an exception
        with pytest.raises(ValueError):
            registry.register_plugin(test_plugin)
    
    def test_unregister_plugin(self, registry, test_plugin):
        """Test unregistering a Plugin."""
        registry.register_plugin(test_plugin)
        registry.unregister_plugin("test_plugin")
        
        assert "test_plugin" not in registry.plugins
    
    def test_unregister_plugin_nonexistent(self, registry):
        """Test unregistering a nonexistent Plugin."""
        # Should not raise an exception
        registry.unregister_plugin("nonexistent")
    
    def test_get_plugin(self, registry, test_plugin):
        """Test getting a Plugin."""
        registry.register_plugin(test_plugin)
        
        plugin = registry.get_plugin("test_plugin")
        
        assert plugin == test_plugin
    
    def test_get_plugin_nonexistent(self, registry):
        """Test getting a nonexistent Plugin."""
        plugin = registry.get_plugin("nonexistent")
        
        assert plugin is None
    
    def test_get_all_plugins(self, registry, test_plugin):
        """Test getting all Plugins."""
        registry.register_plugin(test_plugin)
        
        plugins = registry.get_all_plugins()
        
        assert len(plugins) == 1
        assert test_plugin in plugins
    
    def test_get_enabled_plugins(self, registry, test_plugin):
        """Test getting enabled Plugins."""
        registry.register_plugin(test_plugin)
        
        plugins = registry.get_enabled_plugins()
        
        assert len(plugins) == 1
        assert test_plugin in plugins
        
        # Disable the plugin
        test_plugin.disable()
        
        plugins = registry.get_enabled_plugins()
        
        assert len(plugins) == 0
    
    def test_get_disabled_plugins(self, registry, test_plugin):
        """Test getting disabled Plugins."""
        registry.register_plugin(test_plugin)
        
        plugins = registry.get_disabled_plugins()
        
        assert len(plugins) == 0
        
        # Disable the plugin
        test_plugin.disable()
        
        plugins = registry.get_disabled_plugins()
        
        assert len(plugins) == 1
        assert test_plugin in plugins
    
    def test_enable_plugin(self, registry, test_plugin):
        """Test enabling a Plugin."""
        registry.register_plugin(test_plugin)
        test_plugin.disable()
        
        registry.enable_plugin("test_plugin")
        
        assert test_plugin.is_enabled() is True
    
    def test_enable_plugin_nonexistent(self, registry):
        """Test enabling a nonexistent Plugin."""
        # Should raise an exception
        with pytest.raises(ValueError):
            registry.enable_plugin("nonexistent")
    
    def test_disable_plugin(self, registry, test_plugin):
        """Test disabling a Plugin."""
        registry.register_plugin(test_plugin)
        
        registry.disable_plugin("test_plugin")
        
        assert test_plugin.is_enabled() is False
    
    def test_disable_plugin_nonexistent(self, registry):
        """Test disabling a nonexistent Plugin."""
        # Should raise an exception
        with pytest.raises(ValueError):
            registry.disable_plugin("nonexistent")
    
    def test_get_plugin_info(self, registry, test_plugin):
        """Test getting Plugin info."""
        registry.register_plugin(test_plugin)
        
        info = registry.get_plugin_info("test_plugin")
        
        assert info["name"] == "test_plugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Test plugin"
    
    def test_get_plugin_info_nonexistent(self, registry):
        """Test getting info for a nonexistent Plugin."""
        # Should raise an exception
        with pytest.raises(ValueError):
            registry.get_plugin_info("nonexistent")
    
    def test_get_all_plugin_info(self, registry, test_plugin):
        """Test getting info for all Plugins."""
        registry.register_plugin(test_plugin)
        
        info = registry.get_all_plugin_info()
        
        assert len(info) == 1
        assert info[0]["name"] == "test_plugin"
        assert info[0]["version"] == "1.0.0"
        assert info[0]["description"] == "Test plugin"
    
    def test_has_plugin(self, registry, test_plugin):
        """Test checking if a Plugin exists."""
        registry.register_plugin(test_plugin)
        
        assert registry.has_plugin("test_plugin") is True
        assert registry.has_plugin("nonexistent") is False
    
    def test_count_plugins(self, registry, test_plugin):
        """Test counting Plugins."""
        assert registry.count_plugins() == 0
        
        registry.register_plugin(test_plugin)
        
        assert registry.count_plugins() == 1
    
    def test_clear_plugins(self, registry, test_plugin):
        """Test clearing all Plugins."""
        registry.register_plugin(test_plugin)
        
        registry.clear_plugins()
        
        assert registry.count_plugins() == 0
