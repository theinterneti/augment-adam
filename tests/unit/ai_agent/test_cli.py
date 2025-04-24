"""
Tests for the AI agent CLI.

These tests verify the functionality of the command-line interface.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from augment_adam.ai_agent.cli import app

# Create a CLI runner
runner = CliRunner()

class TestCLI:
    """Tests for the AI agent CLI."""
    
    def test_model_list_command(self):
        """Test the 'model list' command."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the list_available_models method
            mock_manager.list_available_models.return_value = [
                {
                    "id": "test/model1",
                    "name": "model1",
                    "description": "Test model 1",
                    "quantization": "4bit",
                    "is_loaded": True,
                    "is_default": True
                },
                {
                    "id": "test/model2",
                    "name": "model2",
                    "description": "Test model 2",
                    "quantization": "8bit",
                    "is_loaded": False,
                    "is_default": False
                }
            ]
            
            # Run the command
            result = runner.invoke(app, ["model", "list"])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output contains model information
            assert "model1" in result.stdout
            assert "model2" in result.stdout
            assert "Test model 1" in result.stdout
            assert "Test model 2" in result.stdout
            assert "4bit" in result.stdout
            assert "8bit" in result.stdout
            assert "Loaded" in result.stdout
            assert "Default" in result.stdout
    
    def test_model_download_command(self):
        """Test the 'model download' command."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the download_model method
            mock_manager.download_model.return_value = True
            
            # Run the command
            result = runner.invoke(app, ["model", "download", "test/model"])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output indicates success
            assert "downloaded successfully" in result.stdout
            
            # Check that the method was called with correct arguments
            mock_manager.download_model.assert_called_once_with("test/model", None, False)
    
    def test_model_download_command_failure(self):
        """Test the 'model download' command with failure."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the download_model method to return False (failure)
            mock_manager.download_model.return_value = False
            
            # Run the command
            result = runner.invoke(app, ["model", "download", "test/model"])
            
            # Check that the command failed
            assert result.exit_code == 1
            
            # Check that the output indicates failure
            assert "Failed to download" in result.stdout
    
    def test_model_load_command(self):
        """Test the 'model load' command."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the load_model method
            mock_manager.load_model.return_value = True
            
            # Run the command
            result = runner.invoke(app, ["model", "load", "test/model"])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output indicates success
            assert "loaded successfully" in result.stdout
            
            # Check that the method was called with correct arguments
            mock_manager.load_model.assert_called_once_with("test/model", None, False)
    
    def test_model_unload_command(self):
        """Test the 'model unload' command."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the unload_model method
            mock_manager.unload_model.return_value = True
            
            # Run the command
            result = runner.invoke(app, ["model", "unload", "test/model"])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output indicates success
            assert "unloaded successfully" in result.stdout
            
            # Check that the method was called with correct arguments
            mock_manager.unload_model.assert_called_once_with("test/model")
    
    def test_model_set_default_command(self):
        """Test the 'model set-default' command."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the set_default_model method
            mock_manager.set_default_model.return_value = True
            
            # Run the command
            result = runner.invoke(app, ["model", "set-default", "test/model"])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output indicates success
            assert "Default model set to" in result.stdout
            
            # Check that the method was called with correct arguments
            mock_manager.set_default_model.assert_called_once_with("test/model")
    
    def test_generate_command(self):
        """Test the 'generate' command."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the generate method
            mock_manager.generate.return_value = (
                "Generated text response",
                {
                    "model": "test/model",
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "parameters": {"temperature": 0.7}
                }
            )
            
            # Run the command
            result = runner.invoke(app, ["generate", "Test prompt"])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output contains the generated text
            assert "Generated Text:" in result.stdout
            assert "Generated text response" in result.stdout
            
            # Check that the output contains metadata
            assert "Metadata:" in result.stdout
            assert "test/model" in result.stdout
            assert "10" in result.stdout  # prompt tokens
            assert "20" in result.stdout  # completion tokens
    
    def test_generate_command_with_options(self):
        """Test the 'generate' command with options."""
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the generate method
            mock_manager.generate.return_value = (
                "Generated text response",
                {
                    "model": "custom/model",
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "parameters": {"temperature": 0.5}
                }
            )
            
            # Run the command with options
            result = runner.invoke(app, [
                "generate", 
                "Test prompt",
                "--model", "custom/model",
                "--system", "You are a helpful assistant",
                "--temperature", "0.5",
                "--max-tokens", "100"
            ])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the method was called with correct arguments
            mock_manager.generate.assert_called_once_with(
                prompt="Test prompt",
                model_id="custom/model",
                system_prompt="You are a helpful assistant",
                temperature=0.5,
                max_new_tokens=100
            )
    
    def test_docstring_command(self, tmp_path):
        """Test the 'docstring' command."""
        # Create a temporary Python file
        test_file = tmp_path / "test.py"
        with open(test_file, 'w') as f:
            f.write("def test_function():\n    pass\n")
        
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the generate method
            mock_manager.generate.return_value = (
                '"""Test function docstring."""',
                {"model": "test/model"}
            )
            
            # Run the command
            result = runner.invoke(app, ["docstring", str(test_file)])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output contains the generated docstring
            assert "Generated Docstring:" in result.stdout
            assert "Test function docstring" in result.stdout
            
            # Check that CodePromptTemplates.docstring_generation was used
            mock_manager.generate.assert_called_once()
            args, kwargs = mock_manager.generate.call_args
            assert "docstring" in kwargs.get("prompt", "").lower()
            assert kwargs.get("system_prompt", "").lower().startswith("you are an expert")
    
    def test_test_command(self, tmp_path):
        """Test the 'test' command."""
        # Create a temporary Python file
        test_file = tmp_path / "test.py"
        with open(test_file, 'w') as f:
            f.write("def test_function():\n    pass\n")
        
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the generate method
            mock_manager.generate.return_value = (
                "def test_test_function():\n    assert test_function() is None",
                {"model": "test/model"}
            )
            
            # Run the command
            result = runner.invoke(app, ["test", str(test_file)])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output contains the generated tests
            assert "Generated Tests:" in result.stdout
            assert "test_test_function" in result.stdout
            
            # Check that CodePromptTemplates.test_generation was used
            mock_manager.generate.assert_called_once()
            args, kwargs = mock_manager.generate.call_args
            assert "test" in kwargs.get("prompt", "").lower()
            assert kwargs.get("system_prompt", "").lower().startswith("you are an expert")
    
    def test_test_command_with_output(self, tmp_path):
        """Test the 'test' command with output file."""
        # Create a temporary Python file
        test_file = tmp_path / "test.py"
        with open(test_file, 'w') as f:
            f.write("def test_function():\n    pass\n")
        
        # Create output path
        output_file = tmp_path / "test_output.py"
        
        with patch('augment_adam.ai_agent.cli.model_manager') as mock_manager:
            # Mock the generate method
            mock_manager.generate.return_value = (
                "def test_test_function():\n    assert test_function() is None",
                {"model": "test/model"}
            )
            
            # Run the command with output file
            result = runner.invoke(app, [
                "test", 
                str(test_file),
                "--output", str(output_file)
            ])
            
            # Check that the command was successful
            assert result.exit_code == 0
            
            # Check that the output file was created
            assert output_file.exists()
            
            # Check the content of the output file
            with open(output_file, 'r') as f:
                content = f.read()
            
            assert "test_test_function" in content
            assert "assert test_function() is None" in content
