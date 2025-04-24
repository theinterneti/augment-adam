"""Unit tests for the plugin manager UI.

This module contains tests for the plugin manager UI.

Version: 0.1.0
Created: 2025-04-25
"""

import pytest
from unittest.mock import MagicMock, patch

import gradio as gr

from augment_adam.web.plugin_manager import PluginManagerUI, create_plugin_tab
from augment_adam.plugins.base import Plugin, PluginRegistry


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

    def execute(self, param1: str = "default", param2: int = 0):
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


@pytest.fixture
def mock_registry():
    """Create a mock plugin registry for testing."""
    registry = MagicMock(spec=PluginRegistry)

    # Set up the mock to return a list of plugins
    registry.list_plugins.return_value = [
        {"name": "test_plugin", "description": "Test plugin for testing"},
        {"name": "another_plugin", "description": "Another test plugin"},
    ]

    # Set up the mock to return a plugin
    test_plugin = TestPlugin()
    registry.get_plugin.return_value = test_plugin

    # Set up the mock to execute a plugin
    registry.execute_plugin.return_value = {"result": "success"}

    return registry


def test_plugin_manager_ui_init(mock_registry):
    """Test initializing the plugin manager UI."""
    # Create a plugin manager UI
    ui = PluginManagerUI(registry=mock_registry)

    # Check that the registry was set
    assert ui.registry is mock_registry


@patch("gradio.Dropdown")
@patch("gradio.JSON")
@patch("gradio.Button")
def test_plugin_manager_ui_create_ui(mock_button, mock_json, mock_dropdown, mock_registry):
    """Test creating the plugin manager UI."""
    # Set up the mocks
    mock_dropdown.return_value = MagicMock()
    mock_json.return_value = MagicMock()
    mock_button.return_value = MagicMock()

    # Create a plugin manager UI
    ui = PluginManagerUI(registry=mock_registry)

    # Create the UI
    components, event_handlers = ui.create_ui()

    # Check that the components were created
    assert len(components) == 6
    assert mock_dropdown.call_count == 1
    assert mock_json.call_count == 3
    assert mock_button.call_count == 2

    # Check that the event handlers were created
    assert len(event_handlers) == 3


def test_plugin_manager_ui_get_plugin_names(mock_registry):
    """Test getting plugin names."""
    # Create a plugin manager UI
    ui = PluginManagerUI(registry=mock_registry)

    # Mock the list_plugins function
    with patch('augment_adam.web.plugin_manager.list_plugins", return_value=[
        {"name": "test_plugin"},
        {"name": "another_plugin"},
    ]):
        # Get the plugin names
        names = ui._get_plugin_names()

        # Check that the names were returned
        assert len(names) == 2
        assert "test_plugin" in names
        assert "another_plugin" in names


def test_plugin_manager_ui_get_plugin_details(mock_registry):
    """Test getting plugin details."""
    # Create a plugin manager UI
    ui = PluginManagerUI(registry=mock_registry)

    # Create a test plugin
    test_plugin = TestPlugin()

    # Mock the get_plugin function
    with patch('augment_adam.web.plugin_manager.get_plugin", return_value=test_plugin):
        # Get the plugin details
        details, params = ui._get_plugin_details("test_plugin")

        # Check that the details were returned
        assert details["name"] == "test_plugin"
        assert details["description"] == "Test plugin for testing"
        assert "parameters" in details

        # Check that the default parameters were returned
        assert "param1" in params
        assert "param2" in params
        assert params["param1"] == "default"
        assert params["param2"] == 0


def test_plugin_manager_ui_execute_plugin(mock_registry):
    """Test executing a plugin."""
    # Create a plugin manager UI
    ui = PluginManagerUI(registry=mock_registry)

    # Mock the execute_plugin function
    with patch('augment_adam.web.plugin_manager.execute_plugin", return_value={"result": "success"}):
        # Execute the plugin
        result = ui._execute_plugin(
            "test_plugin", {"param1": "test", "param2": 42})

        # Check that the result was returned
        assert result == {"result": "success"}


def test_create_plugin_tab(mock_registry):
    """Test creating a plugin tab."""
    # Mock the necessary components
    mock_tab = MagicMock()
    mock_plugin_manager = MagicMock()
    mock_plugin_manager.create_ui.return_value = ([], [])

    # Patch the required functions
    with patch("gradio.Tab") as mock_tab_class, \
            patch('augment_adam.web.plugin_manager.PluginManagerUI", return_value=mock_plugin_manager) as mock_ui_class:

        # Set up the mock tab
        mock_tab_class.return_value.__enter__.return_value = mock_tab

        # Create a plugin tab
        tab, event_handlers = create_plugin_tab(registry=mock_registry)

        # Check that the tab was created
        assert tab is mock_tab

        # Check that the UI was created with the registry
        mock_ui_class.assert_called_once()
        assert mock_ui_class.call_args[0][0] is mock_registry

        # Check that create_ui was called
        mock_plugin_manager.create_ui.assert_called_once()
