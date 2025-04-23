"""
Tests for the ModelManager class.

These tests verify the functionality of the ModelManager class
in different environments.
"""

import os
import json
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from dukat.ai_agent.models.manager import ModelManager

# Disable logging during tests
logging.getLogger("dukat.ai_agent").setLevel(logging.ERROR)

class TestModelManager:
    """Tests for the ModelManager class."""
    
    def test_init(self, temp_model_dir, temp_config_file):
        """Test initialization of ModelManager."""
        # Initialize with custom paths
        manager = ModelManager(
            models_dir=str(temp_model_dir),
            config_path=str(temp_config_file)
        )
        
        # Check that directories were created
        assert temp_model_dir.exists()
        assert temp_config_file.exists()
        
        # Check that config was created with default values
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        assert "models" in config
        assert "default_model" in config
        
    def test_device_detection(self, env_info):
        """Test device detection based on environment."""
        with patch('torch.cuda.is_available', return_value=env_info["has_cuda"]):
            if hasattr(torch.backends, 'mps'):
                with patch('torch.backends.mps.is_available', return_value=env_info["has_mps"]):
                    manager = ModelManager()
                    if env_info["has_cuda"]:
                        assert manager.device_map == "auto"
                    elif env_info["has_mps"]:
                        assert manager.device_map == "mps"
                    else:
                        assert manager.device_map == "cpu"
            else:
                manager = ModelManager()
                if env_info["has_cuda"]:
                    assert manager.device_map == "auto"
                else:
                    assert manager.device_map == "cpu"
    
    @pytest.mark.parametrize("config_exists", [True, False])
    def test_load_config(self, temp_config_file, config_exists):
        """Test loading configuration."""
        if config_exists:
            # Create a custom config
            custom_config = {
                "models": {
                    "test/model": {
                        "description": "Test model",
                        "quantization": "4bit"
                    }
                },
                "default_model": "test/model"
            }
            with open(temp_config_file, 'w') as f:
                json.dump(custom_config, f)
        
        # Initialize manager with this config path
        manager = ModelManager(config_path=str(temp_config_file))
        
        if config_exists:
            # Check that our custom config was loaded
            assert "test/model" in manager.config["models"]
            assert manager.config["default_model"] == "test/model"
        else:
            # Check that default config was created
            assert "models" in manager.config
            assert "default_model" in manager.config
    
    def test_save_config(self, temp_config_file):
        """Test saving configuration."""
        # Initialize manager
        manager = ModelManager(config_path=str(temp_config_file))
        
        # Modify config
        manager.config["test_key"] = "test_value"
        
        # Save config
        manager._save_config()
        
        # Check that config was saved with our changes
        with open(temp_config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert "test_key" in saved_config
        assert saved_config["test_key"] == "test_value"
    
    @patch('dukat.ai_agent.models.manager.AutoTokenizer')
    @patch('dukat.ai_agent.models.manager.AutoModelForCausalLM')
    def test_download_model(self, mock_model_class, mock_tokenizer_class, temp_model_dir):
        """Test downloading a model."""
        # Mock the tokenizer and model
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        mock_config = MagicMock()
        mock_model_class.config_class.from_pretrained.return_value = mock_config
        
        # Initialize manager
        manager = ModelManager(models_dir=str(temp_model_dir))
        
        # Download a model
        result = manager.download_model("test/model")
        
        # Check that the download was successful
        assert result is True
        
        # Check that the tokenizer was saved
        mock_tokenizer.save_pretrained.assert_called_once()
        
        # Check that the model was added to config
        assert "test/model" in manager.config["models"]
    
    @patch('dukat.ai_agent.models.manager.AutoTokenizer')
    @patch('dukat.ai_agent.models.manager.AutoModelForCausalLM')
    @patch('dukat.ai_agent.models.manager.pipeline')
    def test_load_model(self, mock_pipeline, mock_model_class, mock_tokenizer_class, 
                        temp_model_dir, env_info):
        """Test loading a model."""
        # Mock the tokenizer and model
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        mock_model = MagicMock()
        mock_model_class.from_pretrained.return_value = mock_model
        
        mock_pipe = MagicMock()
        mock_pipeline.return_value = mock_pipe
        
        # Create model directory
        model_dir = temp_model_dir / "test-model"
        model_dir.mkdir()
        
        # Initialize manager
        manager = ModelManager(models_dir=str(temp_model_dir))
        
        # Add model to config
        manager.config["models"]["test/test-model"] = {
            "description": "Test model",
            "quantization": "4bit"
        }
        
        # Load the model
        result = manager.load_model("test/test-model")
        
        # Check that the load was successful
        assert result is True
        
        # Check that the model was loaded with correct parameters
        mock_model_class.from_pretrained.assert_called_once()
        mock_pipeline.assert_called_once()
        
        # Check that the model was added to loaded_models
        assert "test/test-model" in manager.loaded_models
        
    def test_list_available_models(self, temp_model_dir):
        """Test listing available models."""
        # Create some model directories
        (temp_model_dir / "model1").mkdir()
        (temp_model_dir / "model2").mkdir()
        
        # Initialize manager
        manager = ModelManager(models_dir=str(temp_model_dir))
        
        # Add models to config
        manager.config["models"]["org/model1"] = {
            "description": "Model 1",
            "quantization": "4bit"
        }
        manager.config["models"]["org/model2"] = {
            "description": "Model 2",
            "quantization": "8bit"
        }
        manager.config["default_model"] = "org/model1"
        
        # List available models
        models = manager.list_available_models()
        
        # Check that both models are listed
        assert len(models) == 2
        
        # Check model details
        model_names = [m["name"] for m in models]
        assert "model1" in model_names
        assert "model2" in model_names
        
        # Check default flag
        for model in models:
            if model["name"] == "model1":
                assert model["is_default"] is True
            else:
                assert model["is_default"] is False
    
    def test_set_default_model(self, temp_config_file):
        """Test setting the default model."""
        # Initialize manager
        manager = ModelManager(config_path=str(temp_config_file))
        
        # Add a model to config
        manager.config["models"]["test/model"] = {
            "description": "Test model",
            "quantization": "4bit"
        }
        
        # Set as default
        result = manager.set_default_model("test/model")
        
        # Check that the operation was successful
        assert result is True
        
        # Check that the default model was updated
        assert manager.config["default_model"] == "test/model"
        
        # Check that the config was saved
        with open(temp_config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config["default_model"] == "test/model"
    
    def test_set_default_model_invalid(self):
        """Test setting an invalid model as default."""
        # Initialize manager
        manager = ModelManager()
        
        # Try to set a non-existent model as default
        result = manager.set_default_model("nonexistent/model")
        
        # Check that the operation failed
        assert result is False
        
        # Check that the default model was not updated
        assert manager.config["default_model"] != "nonexistent/model"
