"""
Integration tests for the AI agent model management.

These tests verify that the model manager can download and use models
in a real environment.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
import torch

from augment_adam.ai_agent.models import ModelManager

# Skip all tests if no GPU is available
pytestmark = pytest.mark.skipif(
    not torch.cuda.is_available(),
    reason="Integration tests require GPU"
)

# Use a small model for testing
# Changed from TinyLlama to a more compatible model
TEST_MODEL = "facebook/opt-125m"

class TestModelManagerIntegration:
    """Integration tests for the ModelManager class."""

    @pytest.fixture
    def model_manager(self):
        """Create a model manager with a temporary directory."""
        # Create temporary directories
        temp_dir = tempfile.mkdtemp(prefix="augment_adam_test_models_")
        temp_config = tempfile.mktemp(prefix="augment_adam_test_config_", suffix=".json")

        # Create model manager
        manager = ModelManager(
            models_dir=temp_dir,
            config_path=temp_config,
            default_model=TEST_MODEL
        )

        yield manager

        # Clean up
        if os.path.exists(temp_config):
            os.unlink(temp_config)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.mark.slow
    def test_download_model(self, model_manager):
        """Test downloading a model."""
        # Download the model
        result = model_manager.download_model(TEST_MODEL)

        # Check that the download was successful
        assert result is True

        # Check that the model directory was created
        model_name = TEST_MODEL.split('/')[-1]
        model_dir = Path(model_manager.models_dir) / model_name
        assert model_dir.exists()

        # Check that the model was added to config
        assert TEST_MODEL in model_manager.config["models"]

    @pytest.mark.slow
    def test_load_model(self, model_manager):
        """Test loading a model."""
        # Download the model first
        model_manager.download_model(TEST_MODEL)

        # Load the model
        result = model_manager.load_model(TEST_MODEL, quantization="4bit")

        # Check that the load was successful
        assert result is True

        # Check that the model was added to loaded_models
        assert TEST_MODEL in model_manager.loaded_models

        # Check that the model components are available
        assert "model" in model_manager.loaded_models[TEST_MODEL]
        assert "tokenizer" in model_manager.loaded_models[TEST_MODEL]
        assert "pipeline" in model_manager.loaded_models[TEST_MODEL]

    @pytest.mark.slow
    def test_generate_text(self, model_manager):
        """Test generating text with a model."""
        # Download and load the model first
        model_manager.download_model(TEST_MODEL)
        model_manager.load_model(TEST_MODEL, quantization="4bit")

        # Generate text
        prompt = "Write a function to calculate the factorial of a number."
        response, metadata = model_manager.generate(
            prompt=prompt,
            model_id=TEST_MODEL,
            temperature=0.7,
            max_new_tokens=100
        )

        # Check that the response is not empty
        assert response
        assert len(response) > 0

        # Check that the metadata is correct
        assert metadata["model"] == TEST_MODEL
        assert metadata["prompt_tokens"] > 0
        assert metadata["completion_tokens"] > 0

        # Check that the response contains relevant content
        assert "def" in response or "function" in response or "factorial" in response

    @pytest.mark.slow
    def test_unload_model(self, model_manager):
        """Test unloading a model."""
        # Download and load the model first
        model_manager.download_model(TEST_MODEL)
        model_manager.load_model(TEST_MODEL)

        # Unload the model
        result = model_manager.unload_model(TEST_MODEL)

        # Check that the unload was successful
        assert result is True

        # Check that the model was removed from loaded_models
        assert TEST_MODEL not in model_manager.loaded_models
