#!/usr/bin/env python3
"""
Tests for the ModelRegistry class.

This module tests the ModelRegistry class and ensures that
it correctly manages model backends.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.models.model_registry import ModelRegistry, get_registry
from src.models.model_backend import ModelBackend


class MockModelBackend(ModelBackend):
    """Mock implementation of ModelBackend for testing."""

    def __init__(self, model_id, model_config=None, cache_dir=None, **kwargs):
        self.model_id = model_id
        self.model_config = model_config or {}
        self.cache_dir = cache_dir
        self.kwargs = kwargs
        self.available = True

    def generate(self, prompt, system_prompt=None, max_tokens=1000, temperature=0.7, top_p=0.9, stop=None, **kwargs):
        return f"Generated text for {prompt}"

    def generate_stream(self, prompt, system_prompt=None, max_tokens=1000, temperature=0.7, top_p=0.9, stop=None, **kwargs):
        yield f"Generated text for {prompt}"

    def get_token_count(self, text):
        return len(text.split())

    def embed(self, text, **kwargs):
        return [0.1, 0.2, 0.3]

    def batch_embed(self, texts, **kwargs):
        return [[0.1, 0.2, 0.3] for _ in texts]

    def get_model_info(self):
        return {
            "model_id": self.model_id,
            "available": self.available,
            "backend": "mock"
        }

    def is_available(self):
        return self.available

    def format_prompt(self, prompt, system_prompt=None):
        if system_prompt:
            return f"{system_prompt}\n\n{prompt}"
        return prompt

    def share_model(self, target_backend):
        return True


class TestModelRegistry(unittest.TestCase):
    """Tests for the ModelRegistry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = ModelRegistry()
        self.registry.register_backend("mock", MockModelBackend)

    def test_register_backend(self):
        """Test registering a backend."""
        # Register a new backend
        self.registry.register_backend("test", MockModelBackend)

        # Check that the backend was registered
        self.assertIn("test", self.registry.backends)
        self.assertEqual(self.registry.backends["test"], MockModelBackend)

    def test_create_model(self):
        """Test creating a model."""
        # Create a model
        model = self.registry.create_model(
            backend_name="mock",
            model_id="test-model",
            model_config={"param": "value"},
            cache_dir="/tmp"
        )

        # Check that the model was created
        self.assertIsNotNone(model)
        self.assertIsInstance(model, MockModelBackend)
        self.assertEqual(model.model_id, "test-model")
        self.assertEqual(model.model_config, {"param": "value"})
        self.assertEqual(model.cache_dir, "/tmp")

        # Check that the model was registered
        self.assertIn("mock:test-model", self.registry.models)
        self.assertEqual(self.registry.models["mock:test-model"], model)

    def test_create_model_invalid_backend(self):
        """Test creating a model with an invalid backend."""
        # Try to create a model with an invalid backend
        model = self.registry.create_model(
            backend_name="invalid",
            model_id="test-model"
        )

        # Check that the model was not created
        self.assertIsNone(model)

    def test_get_model(self):
        """Test getting a model."""
        # Create a model
        model = self.registry.create_model(
            backend_name="mock",
            model_id="test-model"
        )

        # Get the model
        retrieved_model = self.registry.get_model("mock", "test-model")

        # Check that the model was retrieved
        self.assertEqual(retrieved_model, model)

    def test_get_model_not_found(self):
        """Test getting a model that doesn't exist."""
        # Try to get a model that doesn't exist
        model = self.registry.get_model("mock", "nonexistent-model")

        # Check that the model was not found
        self.assertIsNone(model)

    def test_list_models(self):
        """Test listing models."""
        # Create some models
        model1 = self.registry.create_model(
            backend_name="mock",
            model_id="model1"
        )
        model2 = self.registry.create_model(
            backend_name="mock",
            model_id="model2"
        )

        # List the models
        models = self.registry.list_models()

        # Check that the models were listed
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["backend"], "mock")
        self.assertEqual(models[0]["model_id"], "model1")
        self.assertEqual(models[1]["backend"], "mock")
        self.assertEqual(models[1]["model_id"], "model2")

    def test_list_backends(self):
        """Test listing backends."""
        # Register some backends
        self.registry.register_backend("test1", MockModelBackend)
        self.registry.register_backend("test2", MockModelBackend)

        # List the backends
        backends = self.registry.list_backends()

        # Check that the backends were listed
        self.assertIn("mock", backends)
        self.assertIn("test1", backends)
        self.assertIn("test2", backends)

    def test_share_model(self):
        """Test sharing a model."""
        # Create a mock model that will be returned by create_model
        mock_model = MagicMock()
        mock_model.share_model.return_value = True

        # Register the target backend
        self.registry.register_backend("target", MagicMock())

        # Directly add the mock model to the registry's models dictionary
        self.registry.models["mock:test-model"] = mock_model

        # Share the model
        result = self.registry.share_model("mock", "test-model", "target")

        # Check that the model was shared
        self.assertTrue(result)

    def test_share_model_not_found(self):
        """Test sharing a model that doesn't exist."""
        # Try to share a model that doesn't exist
        result = self.registry.share_model("mock", "nonexistent-model", "target")

        # Check that the model was not shared
        self.assertFalse(result)

    def test_share_model_invalid_target(self):
        """Test sharing a model with an invalid target."""
        # Create a model
        model = self.registry.create_model(
            backend_name="mock",
            model_id="test-model"
        )

        # Try to share the model with an invalid target
        result = self.registry.share_model("mock", "test-model", "invalid")

        # Check that the model was not shared
        self.assertFalse(result)

    def test_get_registry_singleton(self):
        """Test the get_registry function."""
        # Get the registry
        registry1 = get_registry()
        registry2 = get_registry()

        # Check that the same registry was returned
        self.assertIs(registry1, registry2)


if __name__ == "__main__":
    unittest.main()
