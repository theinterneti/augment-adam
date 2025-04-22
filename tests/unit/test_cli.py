"""Unit tests for the CLI module.

This module contains tests for the command-line interface functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import pytest
from typer.testing import CliRunner

from dukat.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_app_exists():
    """Test that the CLI app exists."""
    assert app is not None


def test_main_command(runner):
    """Test the main command."""
    # Run the command
    result = runner.invoke(app, ["main"])

    # Check the result
    assert result.exit_code == 0

    # Check that the welcome message was printed
    assert "Dukat" in result.stdout
    assert "v0.1.0" in result.stdout

    # Check that the model info was printed
    assert "Using model:" in result.stdout


def test_main_command_with_model(runner):
    """Test the main command with a custom model."""
    # Run the command with a custom model
    result = runner.invoke(app, ["main", "--model", "gpt-j:6b"])

    # Check the result
    assert result.exit_code == 0

    # Check that the model info was printed with the custom model
    assert "gpt-j:6b" in result.stdout


def test_main_command_with_verbose(runner):
    """Test the main command with verbose mode."""
    # Run the command with verbose mode
    result = runner.invoke(app, ["main", "--verbose"])

    # Check the result
    assert result.exit_code == 0

    # Check that the verbose message was printed
    assert "Verbose mode enabled" in result.stdout


def test_web_command(runner):
    """Test the web command."""
    # Run the command
    result = runner.invoke(app, ["web"])

    # Check the result
    assert result.exit_code == 0

    # Check that the welcome message was printed
    assert "Dukat Web Interface" in result.stdout
    assert "v0.1.0" in result.stdout

    # Check that the host and port info was printed
    assert "127.0.0.1:7860" in result.stdout


def test_web_command_with_custom_port(runner):
    """Test the web command with a custom port."""
    # Run the command with a custom port
    result = runner.invoke(app, ["web", "--port", "8080"])

    # Check the result
    assert result.exit_code == 0

    # Check that the host and port info was printed with the custom port
    assert "127.0.0.1:8080" in result.stdout


def test_web_command_with_custom_host(runner):
    """Test the web command with a custom host."""
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
