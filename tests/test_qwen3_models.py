#!/usr/bin/env python3
"""
Test script for Qwen 3 models.

This script tests the Qwen 3 model integration with both HuggingFace and Ollama backends.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager
from src.models.model_registry import ModelRegistry, get_registry
from src.models.model_backend import ModelBackend
from src.models.huggingface_model import HuggingFaceModel
from src.models.ollama_model import OllamaModel


class TestQwen3Models(unittest.TestCase):
    """Test cases for Qwen 3 models."""

    def setUp(self):
        """Set up the test environment."""
        # Use a temporary cache directory
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_test")
        os.makedirs(self.cache_dir, exist_ok=True)

    def test_model_registry(self):
        """Test the model registry."""
        registry = ModelRegistry()
        
        # Register backends
        registry.register_backend("huggingface", HuggingFaceModel)
        registry.register_backend("ollama", OllamaModel)
        
        # Check registered backends
        self.assertIn("huggingface", registry.backends)
        self.assertIn("ollama", registry.backends)
        
        # Check backend classes
        self.assertEqual(registry.backends["huggingface"], HuggingFaceModel)
        self.assertEqual(registry.backends["ollama"], OllamaModel)

    @patch("src.models.huggingface_model.HuggingFaceModel")
    def test_huggingface_backend(self, mock_hf_model):
        """Test the HuggingFace backend."""
        # Mock the HuggingFace model
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        mock_instance.get_model_info.return_value = {
            "model_id": "Qwen/Qwen3-0.6B-Chat",
            "available": True,
            "backend": "huggingface"
        }
        mock_instance.generate.return_value = "This is a test response from Qwen 3."
        mock_hf_model.return_value = mock_instance
        
        # Create a registry with the mock backend
        registry = ModelRegistry()
        registry.register_backend("huggingface", mock_hf_model)
        
        # Create a model
        model = registry.create_model(
            backend_name="huggingface",
            model_id="Qwen/Qwen3-0.6B-Chat",
            cache_dir=self.cache_dir
        )
        
        # Check that the model was created
        self.assertIsNotNone(model)
        
        # Check that the model is available
        self.assertTrue(model.is_available())
        
        # Check model info
        model_info = model.get_model_info()
        self.assertEqual(model_info["model_id"], "Qwen/Qwen3-0.6B-Chat")
        self.assertEqual(model_info["backend"], "huggingface")
        
        # Test generation
        response = model.generate("Hello, world!")
        self.assertEqual(response, "This is a test response from Qwen 3.")

    @patch("src.models.ollama_model.OllamaModel")
    def test_ollama_backend(self, mock_ollama_model):
        """Test the Ollama backend."""
        # Mock the Ollama model
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        mock_instance.get_model_info.return_value = {
            "model_id": "qwen3:0.6b",
            "available": True,
            "backend": "ollama"
        }
        mock_instance.generate.return_value = "This is a test response from Qwen 3."
        mock_ollama_model.return_value = mock_instance
        
        # Create a registry with the mock backend
        registry = ModelRegistry()
        registry.register_backend("ollama", mock_ollama_model)
        
        # Create a model
        model = registry.create_model(
            backend_name="ollama",
            model_id="qwen3:0.6b",
            cache_dir=self.cache_dir
        )
        
        # Check that the model was created
        self.assertIsNotNone(model)
        
        # Check that the model is available
        self.assertTrue(model.is_available())
        
        # Check model info
        model_info = model.get_model_info()
        self.assertEqual(model_info["model_id"], "qwen3:0.6b")
        self.assertEqual(model_info["backend"], "ollama")
        
        # Test generation
        response = model.generate("Hello, world!")
        self.assertEqual(response, "This is a test response from Qwen 3.")

    @patch("src.models.model_manager.ModelManager._init_model")
    def test_model_manager(self, mock_init_model):
        """Test the model manager."""
        # Mock the model
        mock_model = MagicMock()
        mock_model.is_available.return_value = True
        mock_model.get_model_info.return_value = {
            "model_id": "qwen3:0.6b",
            "available": True,
            "backend": "ollama"
        }
        mock_model.generate.return_value = "This is a test response from Qwen 3."
        mock_init_model.return_value = mock_model
        
        # Create a model manager
        manager = ModelManager(
            model_type="ollama",
            model_size="qwen3_small",
            cache_dir=self.cache_dir
        )
        
        # Check that the model was initialized
        mock_init_model.assert_called_once()
        
        # Test generation
        response = manager.generate_response("Hello, world!")
        self.assertEqual(response, "This is a test response from Qwen 3.")
        
        # Check model info
        model_info = manager.get_model_info()
        self.assertEqual(model_info["model_id"], "qwen3:0.6b")
        self.assertEqual(model_info["backend"], "ollama")


if __name__ == "__main__":
    unittest.main()
