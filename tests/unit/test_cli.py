"""Unit tests for the CLI module.

This module contains tests for the command-line interface functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import sys
import os
import importlib.util

# Directly import the module from the file path
spec = importlib.util.spec_from_file_location("dukat.cli_module", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../dukat/cli.py')))
module = importlib.util.module_from_spec(spec)
sys.modules["dukat.cli_module"] = module
spec.loader.exec_module(module)

# Get the app from the module
app = module.app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_app_exists():
    """Test that the CLI app exists."""
    assert app is not None


@patch('dukat.cli_module.Assistant')
def test_main_command(mock_assistant, runner):
    """Test the main command."""
    # Mock the Assistant class
    mock_instance = MagicMock()
    mock_assistant.return_value = mock_instance
    mock_instance.generate_response.return_value = "Test response"

    # Run the command with a mock input to exit immediately
    result = runner.invoke(app, ["main"], input="exit\n")

    # Check the result
    assert result.exit_code == 0

    # Check that the welcome message was printed
    assert "Dukat" in result.stdout
    assert "v0.1.0" in result.stdout

    # Check that the model info was printed
    assert "Using model:" in result.stdout


@patch('dukat.cli_module.Assistant')
def test_main_command_with_model(mock_assistant, runner):
    """Test the main command with a custom model."""
    # Mock the Assistant class
    mock_instance = MagicMock()
    mock_assistant.return_value = mock_instance
    mock_instance.generate_response.return_value = "Test response"

    # Run the command with a custom model and mock input to exit immediately
    result = runner.invoke(
        app, ["main", "--model", "gpt-j:6b"], input="exit\n")

    # Check the result
    assert result.exit_code == 0

    # Check that the model info was printed with the custom model
    assert "gpt-j:6b" in result.stdout


@patch('dukat.cli_module.Assistant')
def test_main_command_with_verbose(mock_assistant, runner):
    """Test the main command with verbose mode."""
    # Mock the Assistant class
    mock_instance = MagicMock()
    mock_assistant.return_value = mock_instance
    mock_instance.generate_response.return_value = "Test response"

    # Run the command with verbose mode and mock input to exit immediately
    result = runner.invoke(app, ["main", "--verbose"], input="exit\n")

    # Check the result
    assert result.exit_code == 0

    # Check that the verbose message was printed
    assert "Verbose mode enabled" in result.stdout


@patch('dukat.cli_module.launch_web_interface')
def test_web_command(mock_launch_web, runner):
    """Test the web command."""
    # Mock the launch_web_interface function
    mock_launch_web.return_value = None

    # Run the command
    result = runner.invoke(app, ["web"])

    # Check the result
    assert result.exit_code == 0

    # Check that the welcome message was printed
    assert "Dukat Web Interface" in result.stdout
    assert "v0.1.0" in result.stdout

    # Check that the host and port info was printed
    assert "127.0.0.1:7860" in result.stdout


@patch('dukat.cli_module.launch_web_interface')
def test_web_command_with_custom_port(mock_launch_web, runner):
    """Test the web command with a custom port."""
    # Mock the launch_web_interface function
    mock_launch_web.return_value = None

    # Run the command with a custom port
    result = runner.invoke(app, ["web", "--port", "8080"])

    # Check the result
    assert result.exit_code == 0

    # Check that the host and port info was printed with the custom port
    assert "127.0.0.1:8080" in result.stdout


@patch('dukat.cli_module.launch_web_interface')
def test_web_command_with_custom_host(mock_launch_web, runner):
    """Test the web command with a custom host."""
    # Mock the launch_web_interface function
    mock_launch_web.return_value = None

    # Run the command with a custom host
    result = runner.invoke(app, ["web", "--host", "0.0.0.0"])

    # Check the result
    assert result.exit_code == 0

    # Check that the host and port info was printed with the custom host
    assert "0.0.0.0:7860" in result.stdout


def test_help_option(runner):
    """Test the help option."""
    # Run the command with --help
    result = runner.invoke(app, ["--help"])

    # Check the result
    assert result.exit_code == 0

    # Check that the help text was printed
    assert "Usage: " in result.stdout
    assert "An open-source AI assistant focused on personal automation." in result.stdout

    # Check that the commands are listed
    assert "main" in result.stdout
    assert "web" in result.stdout
