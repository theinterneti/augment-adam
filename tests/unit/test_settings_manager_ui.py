"""Unit tests for the settings manager UI.

This module contains tests for the settings manager UI.

Version: 0.1.0
Created: 2025-04-25
"""

import unittest
from unittest.mock import MagicMock, patch

import gradio as gr
import pytest

from augment_adam.core.settings import Settings, SettingsScope
from augment_adam.web.settings_manager import SettingsManagerUI, create_settings_tab


class TestSettingsManagerUI(unittest.TestCase):
    """Test SettingsManagerUI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the settings functions
        self.mock_settings = Settings()
        
        # Create patches
        self.get_settings_patch = patch('augment_adam.web.settings_manager.get_settings")
        self.update_settings_patch = patch('augment_adam.web.settings_manager.update_settings")
        self.reset_settings_patch = patch('augment_adam.web.settings_manager.reset_settings")
        
        # Start patches
        self.mock_get_settings = self.get_settings_patch.start()
        self.mock_update_settings = self.update_settings_patch.start()
        self.mock_reset_settings = self.reset_settings_patch.start()
        
        # Set up mock return values
        self.mock_get_settings.return_value = self.mock_settings
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop patches
        self.get_settings_patch.stop()
        self.update_settings_patch.stop()
        self.reset_settings_patch.stop()
    
    def test_init(self):
        """Test initialization."""
        ui = SettingsManagerUI()
        self.assertEqual(ui.settings, self.mock_settings)
        self.mock_get_settings.assert_called_once()
    
    @patch("gradio.Radio")
    @patch("gradio.JSON")
    @patch("gradio.Button")
    @patch("gradio.Textbox")
    def test_create_ui(self, mock_textbox, mock_button, mock_json, mock_radio):
        """Test create_ui method."""
        # Set up mocks
        mock_radio.return_value = MagicMock()
        mock_json.return_value = MagicMock()
        mock_button.return_value = MagicMock()
        mock_textbox.return_value = MagicMock()
        
        # Create UI
        ui = SettingsManagerUI()
        components, event_handlers = ui.create_ui()
        
        # Check components
        self.assertEqual(len(components), 7)
        
        # Check event handlers
        self.assertEqual(len(event_handlers), 4)
    
    def test_get_settings_dict(self):
        """Test _get_settings_dict method."""
        ui = SettingsManagerUI()
        
        # Test with valid scope
        result = ui._get_settings_dict(SettingsScope.USER.value)
        self.assertEqual(result, self.mock_settings.model_dump())
        self.mock_get_settings.assert_called_with(SettingsScope.USER)
        
        # Test with exception
        self.mock_get_settings.side_effect = ValueError("Test error")
        result = ui._get_settings_dict(SettingsScope.USER.value)
        self.assertTrue("error" in result)
    
    def test_update_settings(self):
        """Test _update_settings method."""
        ui = SettingsManagerUI()
        
        # Test with valid settings
        settings_dict = {"model": {"default_model": "gpt4"}}
        result, status = ui._update_settings(SettingsScope.USER.value, settings_dict)
        
        self.assertEqual(result, self.mock_settings.model_dump())
        self.assertTrue("updated successfully" in status)
        self.mock_update_settings.assert_called_with(settings_dict, scope=SettingsScope.USER)
        
        # Test with exception
        self.mock_update_settings.side_effect = ValueError("Test error")
        result, status = ui._update_settings(SettingsScope.USER.value, settings_dict)
        
        self.assertTrue("error" in status.lower())
    
    def test_reset_settings(self):
        """Test _reset_settings method."""
        ui = SettingsManagerUI()
        
        # Test reset
        result, status = ui._reset_settings(SettingsScope.USER.value)
        
        self.assertEqual(result, self.mock_settings.model_dump())
        self.assertTrue("reset to defaults" in status)
        self.mock_reset_settings.assert_called_with(scope=SettingsScope.USER)
        
        # Test with exception
        self.mock_reset_settings.side_effect = ValueError("Test error")
        result, status = ui._reset_settings(SettingsScope.USER.value)
        
        self.assertTrue("error" in status.lower())


@patch('augment_adam.web.settings_manager.SettingsManagerUI")
@patch("gradio.Tab")
@patch("gradio.Row")
@patch("gradio.Column")
@patch("gradio.Markdown")
def test_create_settings_tab(
    mock_markdown,
    mock_column,
    mock_row,
    mock_tab,
    mock_ui,
):
    """Test create_settings_tab function."""
    # Set up mocks
    mock_tab.return_value.__enter__.return_value = MagicMock()
    mock_row.return_value.__enter__.return_value = MagicMock()
    mock_column.return_value.__enter__.return_value = MagicMock()
    mock_ui.return_value.create_ui.return_value = ([], [])
    
    # Create tab
    tab, event_handlers = create_settings_tab()
    
    # Check results
    assert tab is mock_tab.return_value.__enter__.return_value
    assert event_handlers == []
    
    # Check that UI was created
    mock_ui.assert_called_once()
    mock_ui.return_value.create_ui.assert_called_once()


if __name__ == "__main__":
    unittest.main()
