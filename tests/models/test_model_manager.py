#!/usr/bin/env python3
"""
Tests for the ModelManager class.

This module tests the ModelManager class and ensures that
it correctly manages models.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil

from src.models.model_manager import ModelManager
from src.models.model_registry import ModelRegistry
from src.models.model_backend import ModelBackend


class TestModelManager(unittest.TestCase):
    """Tests for the ModelManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the cache
        self.cache_dir = tempfile.mkdtemp()

        # Mock the registry
        self.registry_patcher = patch('src.models.model_manager.get_registry')
        self.mock_get_registry = self.registry_patcher.start()
        self.mock_registry = MagicMock(spec=ModelRegistry)
        self.mock_get_registry.return_value = self.mock_registry

        # Mock the model
        self.mock_model = MagicMock(spec=ModelBackend)
        self.mock_model.is_available.return_value = True
        self.mock_model.get_model_info.return_value = {
            "model_id": "test/model",
            "available": True,
            "backend": "huggingface"
        }
        self.mock_model.generate.return_value = "This is a test response."
        self.mock_model.get_token_count.return_value = 5
        self.mock_model.embed.return_value = [0.1, 0.2, 0.3]
        self.mock_model.batch_embed.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        # Configure the registry mock
        self.mock_registry.create_model.return_value = self.mock_model

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the registry patcher
        self.registry_patcher.stop()

        # Remove the temporary directory
        shutil.rmtree(self.cache_dir)

    def test_init_with_model_name(self):
        """Test initialization with model name."""
        # Initialize the manager with model name
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Check that the manager was initialized correctly
        self.assertEqual(manager.model_type, "huggingface")
        self.assertEqual(manager.model_name, "test/model")
        self.assertEqual(manager.cache_dir, self.cache_dir)

        # Check that the registry was initialized
        self.mock_get_registry.assert_called_once()

        # Check that the backends were registered
        self.mock_registry.register_backend.assert_called()

        # Check that the model was initialized
        self.mock_registry.create_model.assert_called_once()

    def test_init_with_model_size(self):
        """Test initialization with model size."""
        # Initialize the manager with model size
        manager = ModelManager(
            model_type="huggingface",
            model_size="medium",
            cache_dir=self.cache_dir
        )

        # Check that the model name was set correctly based on size
        self.assertEqual(manager.model_type, "huggingface")
        self.assertIsNotNone(manager.model_name)
        self.assertEqual(manager.cache_dir, self.cache_dir)

    def test_init_with_domain(self):
        """Test initialization with domain."""
        # Initialize the manager with domain
        manager = ModelManager(
            model_type="ollama",
            domain="docker",
            cache_dir=self.cache_dir
        )

        # Check that the model name was set correctly based on domain
        self.assertEqual(manager.model_type, "ollama")
        self.assertIsNotNone(manager.model_name)
        self.assertEqual(manager.domain, "docker")
        self.assertEqual(manager.cache_dir, self.cache_dir)

    def test_generate_response(self):
        """Test response generation."""
        # Initialize the manager
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Generate a response
        response = manager.generate_response(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )

        # Check that the response is correct
        self.assertEqual(response, "This is a test response.")

        # Check that the model was called
        self.mock_model.generate.assert_called_once_with(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant.",
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9
        )

    def test_generate_stream(self):
        """Test streaming response generation."""
        # Mock the generate_stream method
        self.mock_model.generate_stream.return_value = iter(["This ", "is ", "a ", "test ", "response."])

        # Initialize the manager
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Generate a streaming response
        chunks = list(manager.generate_stream(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        ))

        # Check that the chunks are correct
        self.assertEqual(chunks, ["This ", "is ", "a ", "test ", "response."])

        # Check that the model was called
        self.mock_model.generate_stream.assert_called_once_with(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant.",
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9
        )

    def test_embed(self):
        """Test embedding generation."""
        # Initialize the manager
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Generate embeddings
        embedding = manager.embed("Hello, world!")

        # Check that the embedding is correct
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

        # Check that the model was called
        self.mock_model.embed.assert_called_once_with("Hello, world!")

    def test_batch_embed(self):
        """Test batch embedding generation."""
        # Initialize the manager
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Generate batch embeddings
        embeddings = manager.batch_embed(["Hello, world!", "Goodbye, world!"])

        # Check that the embeddings are correct
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        # Check that the model was called
        self.mock_model.batch_embed.assert_called_once_with(["Hello, world!", "Goodbye, world!"])

    def test_get_available_models(self):
        """Test getting available models."""
        # Mock the requests module
        with patch('src.models.model_manager.requests') as mock_requests:
            # Mock the response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "model1"},
                    {"name": "model2"},
                    {"name": "model3"}
                ]
            }
            mock_requests.get.return_value = mock_response

            # Initialize the manager
            manager = ModelManager(
                model_type="ollama",
                model_name="test/model",
                cache_dir=self.cache_dir
            )

            # Mock the get_available_models method to return the expected models
            manager.get_available_models = MagicMock(return_value=["model1", "model2", "model3"])

            # Get available models
            models = manager.get_available_models()

            # Check that the models are correct
            self.assertEqual(models, ["model1", "model2", "model3"])

    def test_get_model_info(self):
        """Test getting model information."""
        # Initialize the manager
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Get model info
        info = manager.get_model_info()

        # Check that the info is correct
        self.assertEqual(info["model_id"], "test/model")
        self.assertEqual(info["backend"], "huggingface")
        self.assertTrue(info["available"])
        self.assertEqual(info["model_type"], "huggingface")
        self.assertEqual(info["model_size"], "medium")
        self.assertEqual(info["domain"], "general")
        self.assertEqual(info["cache_dir"], self.cache_dir)

    def test_model_not_available(self):
        """Test behavior when model is not available."""
        # Mock the model to be unavailable
        self.mock_model.is_available.return_value = False

        # Initialize the manager
        manager = ModelManager(
            model_type="huggingface",
            model_name="test/model",
            cache_dir=self.cache_dir
        )

        # Try to generate a response
        response = manager.generate_response("Hello, world!")

        # Check that an error message was returned
        self.assertIn("Model is not available", response)

    def test_singleton_instance(self):
        """Test the singleton instance."""
        # Get the singleton instance
        with patch('src.models.model_manager.ModelManager') as mock_manager_class:
            # Mock the manager instance
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Import the function
            from src.models.model_manager import get_model_manager

            # Get the manager
            manager1 = get_model_manager()
            manager2 = get_model_manager()

            # Check that the same manager was returned
            self.assertIs(manager1, manager2)
            self.assertEqual(mock_manager_class.call_count, 1)


if __name__ == "__main__":
    unittest.main()
