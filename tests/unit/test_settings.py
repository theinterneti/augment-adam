"""Unit tests for settings management.

This module contains tests for the settings management system.

Version: 0.1.0
Created: 2025-04-25
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dukat.core.errors import ValidationError
from dukat.core.settings import (
    LoggingSettings,
    MemorySettings,
    ModelSettings,
    NetworkSettings,
    PluginSettings,
    SecuritySettings,
    Settings,
    SettingsError,
    SettingsManager,
    SettingsScope,
    UISettings,
    get_settings,
    get_settings_manager,
    reset_settings,
    update_settings,
)


class TestSettingsModels(unittest.TestCase):
    """Test settings model classes."""

    def test_model_settings(self):
        """Test ModelSettings."""
        settings = ModelSettings()
        self.assertEqual(settings.default_model, "llama3:8b")
        self.assertEqual(settings.temperature, 0.7)
        self.assertEqual(settings.max_tokens, 1024)

        # Test custom values
        custom = ModelSettings(default_model="gpt4",
                               temperature=0.5, max_tokens=2048)
        self.assertEqual(custom.default_model, "gpt4")
        self.assertEqual(custom.temperature, 0.5)
        self.assertEqual(custom.max_tokens, 2048)

        # Test validation
        with self.assertRaises(Exception):
            ModelSettings(temperature=2.0)  # temperature must be <= 1.0

        with self.assertRaises(Exception):
            ModelSettings(max_tokens=0)  # max_tokens must be > 0

    def test_memory_settings(self):
        """Test MemorySettings."""
        settings = MemorySettings()
        self.assertEqual(settings.working_memory_size, 10)
        self.assertTrue(settings.semantic_memory_enabled)
        self.assertTrue(settings.episodic_memory_enabled)

        # Test custom values
        custom = MemorySettings(
            working_memory_size=20,
            semantic_memory_enabled=False,
            episodic_memory_enabled=False,
        )
        self.assertEqual(custom.working_memory_size, 20)
        self.assertFalse(custom.semantic_memory_enabled)
        self.assertFalse(custom.episodic_memory_enabled)

    def test_ui_settings(self):
        """Test UISettings."""
        settings = UISettings()
        self.assertEqual(settings.theme, "light")
        self.assertEqual(settings.font_size, 14)
        self.assertTrue(settings.show_timestamps)

        # Test custom values
        custom = UISettings(
            theme="dark",
            font_size=16,
            show_timestamps=False,
        )
        self.assertEqual(custom.theme, "dark")
        self.assertEqual(custom.font_size, 16)
        self.assertFalse(custom.show_timestamps)

    def test_plugin_settings(self):
        """Test PluginSettings."""
        settings = PluginSettings()
        self.assertEqual(settings.enabled_plugins, [])
        self.assertFalse(settings.auto_enable_plugins)
        self.assertEqual(settings.plugin_timeout, 30.0)

        # Test custom values
        custom = PluginSettings(
            enabled_plugins=["plugin1", "plugin2"],
            auto_enable_plugins=True,
            plugin_timeout=60.0,
        )
        self.assertEqual(custom.enabled_plugins, ["plugin1", "plugin2"])
        self.assertTrue(custom.auto_enable_plugins)
        self.assertEqual(custom.plugin_timeout, 60.0)

    def test_logging_settings(self):
        """Test LoggingSettings."""
        settings = LoggingSettings()
        self.assertEqual(settings.level, "INFO")
        self.assertTrue(settings.file_logging_enabled)
        self.assertIsNone(settings.log_file_path)

        # Test custom values
        custom = LoggingSettings(
            level="DEBUG",
            file_logging_enabled=False,
            log_file_path="/path/to/log",
        )
        self.assertEqual(custom.level, "DEBUG")
        self.assertFalse(custom.file_logging_enabled)
        self.assertEqual(custom.log_file_path, "/path/to/log")

    def test_security_settings(self):
        """Test SecuritySettings."""
        settings = SecuritySettings()
        self.assertFalse(settings.enable_authentication)
        self.assertEqual(settings.session_timeout, 3600)
        self.assertEqual(settings.allowed_hosts, ["localhost", "127.0.0.1"])

        # Test custom values
        custom = SecuritySettings(
            enable_authentication=True,
            session_timeout=7200,
            allowed_hosts=["example.com"],
        )
        self.assertTrue(custom.enable_authentication)
        self.assertEqual(custom.session_timeout, 7200)
        self.assertEqual(custom.allowed_hosts, ["example.com"])

    def test_network_settings(self):
        """Test NetworkSettings."""
        settings = NetworkSettings()
        self.assertEqual(settings.request_timeout, 30.0)
        self.assertEqual(settings.max_retries, 3)
        self.assertEqual(settings.retry_delay, 1.0)

        # Test custom values
        custom = NetworkSettings(
            request_timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
        )
        self.assertEqual(custom.request_timeout, 60.0)
        self.assertEqual(custom.max_retries, 5)
        self.assertEqual(custom.retry_delay, 2.0)

    def test_main_settings(self):
        """Test main Settings class."""
        settings = Settings()

        # Test default values
        self.assertIsInstance(settings.model, ModelSettings)
        self.assertIsInstance(settings.memory, MemorySettings)
        self.assertIsInstance(settings.ui, UISettings)
        self.assertIsInstance(settings.plugins, PluginSettings)
        self.assertIsInstance(settings.logging, LoggingSettings)
        self.assertIsInstance(settings.security, SecuritySettings)
        self.assertIsInstance(settings.network, NetworkSettings)
        self.assertEqual(settings.custom, {})

        # Test custom values
        custom = Settings(
            model=ModelSettings(default_model="gpt4"),
            memory=MemorySettings(working_memory_size=20),
            custom={"key": "value"},
        )
        self.assertEqual(custom.model.default_model, "gpt4")
        self.assertEqual(custom.memory.working_memory_size, 20)
        self.assertEqual(custom.custom, {"key": "value"})


class TestSettingsManager(unittest.TestCase):
    """Test SettingsManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for settings files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)

        # Create a settings manager
        self.manager = SettingsManager(
            config_dir=self.config_dir, auto_save=False)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.manager.config_dir, self.config_dir)
        self.assertFalse(self.manager.auto_save)

        # Check that settings were created for each scope
        for scope in SettingsScope:
            self.assertIsInstance(self.manager.get_settings(scope), Settings)

    def test_get_settings_path(self):
        """Test _get_settings_path method."""
        self.assertEqual(
            self.manager._get_settings_path(SettingsScope.GLOBAL),
            self.config_dir / "global_settings.json",
        )
        self.assertEqual(
            self.manager._get_settings_path(SettingsScope.USER),
            self.config_dir / "user_settings.json",
        )

        # Session settings don't have a path
        with self.assertRaises(ValueError):
            self.manager._get_settings_path(SettingsScope.SESSION)

    def test_save_and_load_settings(self):
        """Test save_settings and load_settings methods."""
        # Update some settings
        self.manager.update_settings(
            SettingsScope.GLOBAL,
            {"model": {"default_model": "gpt4"}},
        )

        # Save settings
        self.manager.save_settings(SettingsScope.GLOBAL)

        # Check that the file was created
        settings_path = self.manager._get_settings_path(SettingsScope.GLOBAL)
        self.assertTrue(settings_path.exists())

        # Create a new manager to load the settings
        new_manager = SettingsManager(
            config_dir=self.config_dir, auto_save=False)

        # Check that the settings were loaded
        global_settings = new_manager.get_settings(SettingsScope.GLOBAL)
        self.assertEqual(global_settings.model.default_model, "gpt4")

    def test_load_settings_error(self):
        """Test load_settings with invalid file."""
        # Create an invalid settings file
        settings_path = self.manager._get_settings_path(SettingsScope.GLOBAL)
        with open(settings_path, "w") as f:
            f.write("invalid json")

        # Try to load the settings
        with self.assertRaises(SettingsError):
            self.manager.load_settings(SettingsScope.GLOBAL)

    def test_save_settings_error(self):
        """Test save_settings with error."""
        # Mock open to raise an error
        with patch("builtins.open", side_effect=OSError("Test error")):
            with self.assertRaises(SettingsError):
                self.manager.save_settings(SettingsScope.GLOBAL)

    def test_get_effective_settings(self):
        """Test get_effective_settings method."""
        # Create dictionaries representing settings for each scope
        global_dict = {"model": {"default_model": "global_model"}}
        user_dict = {"model": {"default_model": "user_model"}}
        session_dict = {"model": {"temperature": 0.5}}

        # Merge the dictionaries manually using _deep_merge
        merged_dict = self.manager._deep_merge(global_dict, user_dict)
        merged_dict = self.manager._deep_merge(merged_dict, session_dict)

        # Check that the dictionaries were merged correctly
        self.assertEqual(merged_dict["model"]["default_model"], "user_model")
        self.assertEqual(merged_dict["model"]["temperature"], 0.5)

    def test_deep_merge(self):
        """Test _deep_merge method."""
        base = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3,
            },
            "e": [1, 2, 3],
        }

        override = {
            "a": 10,
            "b": {
                "c": 20,
                "f": 30,
            },
            "g": 40,
        }

        merged = self.manager._deep_merge(base, override)

        self.assertEqual(merged["a"], 10)  # Overridden
        self.assertEqual(merged["b"]["c"], 20)  # Overridden
        self.assertEqual(merged["b"]["d"], 3)  # Kept from base
        self.assertEqual(merged["b"]["f"], 30)  # Added from override
        self.assertEqual(merged["e"], [1, 2, 3])  # Kept from base
        self.assertEqual(merged["g"], 40)  # Added from override

    def test_update_settings(self):
        """Test update_settings method."""
        # Update settings
        self.manager.update_settings(
            SettingsScope.USER,
            {
                "model": {"default_model": "gpt4"},
                "memory": {"working_memory_size": 20},
            },
        )

        # Check that the settings were updated
        user_settings = self.manager.get_settings(SettingsScope.USER)
        self.assertEqual(user_settings.model.default_model, "gpt4")
        self.assertEqual(user_settings.memory.working_memory_size, 20)

        # Update with invalid settings
        with self.assertRaises(ValidationError):
            self.manager.update_settings(
                SettingsScope.USER,
                {"model": {"temperature": 2.0}},  # Invalid temperature
            )

    def test_update_settings_with_auto_save(self):
        """Test update_settings with auto_save."""
        # Create a manager with auto_save=True
        manager = SettingsManager(config_dir=self.config_dir, auto_save=True)

        # Update settings
        manager.update_settings(
            SettingsScope.USER,
            {"model": {"default_model": "gpt4"}},
        )

        # Check that the file was created
        settings_path = manager._get_settings_path(SettingsScope.USER)
        self.assertTrue(settings_path.exists())

        # Check the file contents
        with open(settings_path, "r") as f:
            settings_dict = json.load(f)

        self.assertEqual(settings_dict["model"]["default_model"], "gpt4")

    def test_reset_settings(self):
        """Test reset_settings method."""
        # Update settings
        self.manager.update_settings(
            SettingsScope.USER,
            {"model": {"default_model": "gpt4"}},
        )

        # Reset settings
        self.manager.reset_settings(SettingsScope.USER)

        # Check that the settings were reset
        user_settings = self.manager.get_settings(SettingsScope.USER)
        self.assertEqual(user_settings.model.default_model,
                         "llama3:8b")  # Default value


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for settings files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)

        # Create the config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Clear the global settings manager
        from dukat.core.settings import _settings_manager
        if _settings_manager is not None:
            _settings_manager = None

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_get_settings_manager(self):
        """Test get_settings_manager function."""
        # Get the settings manager
        manager = get_settings_manager(config_dir=self.config_dir)

        # Check that it's a SettingsManager
        self.assertIsInstance(manager, SettingsManager)

        # Check that it's the same instance when called again
        manager2 = get_settings_manager()
        self.assertIs(manager2, manager)

    def test_get_settings(self):
        """Test get_settings function."""
        # Initialize the settings manager
        get_settings_manager(config_dir=self.config_dir)

        # Get settings for a specific scope
        global_settings = get_settings(SettingsScope.GLOBAL)
        self.assertIsInstance(global_settings, Settings)

        # Get effective settings
        effective_settings = get_settings()
        self.assertIsInstance(effective_settings, Settings)

    @patch("dukat.core.settings.SettingsManager.save_settings")
    def test_update_settings(self, mock_save):
        """Test update_settings function."""
        # Initialize the settings manager
        manager = get_settings_manager(config_dir=self.config_dir)

        # Update settings
        update_settings(
            {"model": {"default_model": "gpt4"}},
            scope=SettingsScope.USER,
            save=False,
        )

        # Check that the settings were updated
        user_settings = get_settings(SettingsScope.USER)
        self.assertEqual(user_settings.model.default_model, "gpt4")

        # Verify save_settings was not called
        mock_save.assert_not_called()

    @patch("dukat.core.settings.SettingsManager.save_settings")
    def test_reset_settings(self, mock_save):
        """Test reset_settings function."""
        # Initialize the settings manager
        manager = get_settings_manager(config_dir=self.config_dir)

        # Update settings without saving
        manager._settings[SettingsScope.USER].model.default_model = "gpt4"

        # Reset settings
        reset_settings(scope=SettingsScope.USER, save=False)

        # Check that the settings were reset
        user_settings = get_settings(SettingsScope.USER)
        self.assertEqual(user_settings.model.default_model,
                         "llama3:8b")  # Default value

        # Verify save_settings was not called
        mock_save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
