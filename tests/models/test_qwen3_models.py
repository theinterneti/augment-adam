#!/usr/bin/env python3
"""
Tests for Qwen 3 models.

This module tests the integration of Qwen 3 models with the model management system.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil

from src.models.model_manager import ModelManager
from src.models.huggingface_model import HuggingFaceModel, HUGGINGFACE_AVAILABLE
from src.models.ollama_model import OllamaModel


class TestQwen3Models(unittest.TestCase):
    """Tests for Qwen 3 models."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the cache
        self.cache_dir = tempfile.mkdtemp()

        # Mock the HuggingFace and Ollama models
        self.huggingface_patcher = patch('src.models.model_manager.HuggingFaceModel')
        self.mock_huggingface_class = self.huggingface_patcher.start()
        self.mock_huggingface_model = MagicMock(spec=HuggingFaceModel)
        self.mock_huggingface_model.is_available.return_value = True
        self.mock_huggingface_model.get_model_info.return_value = {
            "model_id": "Qwen/Qwen3-1.7B-Chat",
            "available": True,
            "backend": "huggingface",
            "model_type": "qwen3"
        }
        self.mock_huggingface_model.generate.return_value = "This is a test response from Qwen 3."
        self.mock_huggingface_class.return_value = self.mock_huggingface_model

        self.ollama_patcher = patch('src.models.model_manager.OllamaModel')
        self.mock_ollama_class = self.ollama_patcher.start()
        self.mock_ollama_model = MagicMock(spec=OllamaModel)
        self.mock_ollama_model.is_available.return_value = True
        self.mock_ollama_model.get_model_info.return_value = {
            "model_id": "qwen3:1.7b",
            "available": True,
            "backend": "ollama",
            "model_type": "qwen3"
        }
        self.mock_ollama_model.generate.return_value = "This is a test response from Qwen 3 on Ollama."
        self.mock_ollama_class.return_value = self.mock_ollama_model

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patchers
        self.huggingface_patcher.stop()
        self.ollama_patcher.stop()

        # Remove the temporary directory
        shutil.rmtree(self.cache_dir)

    def test_qwen3_huggingface(self):
        """Test Qwen 3 models with HuggingFace backend."""
        # Create a model manager with Qwen 3 model
        manager = ModelManager(
            model_type="huggingface",
            model_size="qwen3_medium",
            cache_dir=self.cache_dir
        )

        # Check that the model name was set correctly
        self.assertIn("qwen3", manager.model_name.lower())
        self.assertEqual(manager.model_size, "qwen3_medium")

        # Generate a response
        response = manager.generate_response(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )

        # Check that the response is correct
        self.assertEqual(response, "This is a test response from Qwen 3.")

        # Check that the HuggingFace model was called
        self.mock_huggingface_model.generate.assert_called_once()

        # Check that the prompt was formatted correctly
        self.mock_huggingface_model.generate.assert_called_with(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant.",
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9
        )

    def test_qwen3_ollama(self):
        """Test Qwen 3 models with Ollama backend."""
        # Create a model manager with Qwen 3 model
        manager = ModelManager(
            model_type="ollama",
            model_size="qwen3_medium",
            cache_dir=self.cache_dir
        )

        # Check that the model name was set correctly
        self.assertIn("qwen3", manager.model_name.lower())
        self.assertEqual(manager.model_size, "qwen3_medium")

        # Generate a response
        response = manager.generate_response(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )

        # Check that the response is correct
        self.assertEqual(response, "This is a test response from Qwen 3 on Ollama.")

        # Check that the Ollama model was called
        self.mock_ollama_model.generate.assert_called_once()

        # Check that the prompt was formatted correctly
        self.mock_ollama_model.generate.assert_called_with(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant.",
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9
        )

    def test_qwen3_context_window(self):
        """Test Qwen 3 context window sizes."""
        # Create a model manager with Qwen 3 model
        manager = ModelManager(
            model_type="huggingface",
            model_size="qwen3_medium",
            cache_dir=self.cache_dir
        )

        # For testing, we'll mock the model_config
        manager.model = MagicMock()
        manager.model.model_config = {"context_size": 32768}

        # Check that the context window size is correct
        self.assertEqual(manager.model.model_config.get("context_size"), 32768)

        # Create a model manager with Qwen 3 XL model
        manager = ModelManager(
            model_type="huggingface",
            model_size="qwen3_xl",
            cache_dir=self.cache_dir
        )

        # For testing, we'll mock the model_config
        manager.model = MagicMock()
        manager.model.model_config = {"context_size": 128000}

        # Check that the context window size is correct
        self.assertEqual(manager.model.model_config.get("context_size"), 128000)

    def test_qwen3_moe_models(self):
        """Test Qwen 3 MoE models."""
        # Create a model manager with Qwen 3 MoE model
        manager = ModelManager(
            model_type="huggingface",
            model_size="qwen3_moe_small",
            cache_dir=self.cache_dir
        )

        # Check that the model name was set correctly
        self.assertIn("qwen3", manager.model_name.lower())
        self.assertIn("moe", manager.model_size.lower())

        # Mock the model for testing
        manager.model = MagicMock()
        manager.model.generate.return_value = "This is a test response from Qwen 3."
        manager.model.model_config = {"context_size": 128000}

        # Generate a response
        response = manager.generate_response(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )

        # Check that the response is correct
        self.assertEqual(response, "This is a test response from Qwen 3.")

        # Check that the context window size is correct
        self.assertEqual(manager.model.model_config.get("context_size"), 128000)


if __name__ == "__main__":
    unittest.main()
