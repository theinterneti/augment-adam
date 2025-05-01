#!/usr/bin/env python3
"""
Tests for the HuggingFaceModel class.

This module tests the HuggingFaceModel class and ensures that
it correctly implements the ModelBackend interface.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
import json

from src.models.huggingface_model import HuggingFaceModel, HUGGINGFACE_AVAILABLE


# Skip tests if HuggingFace is not available
@unittest.skipIf(not HUGGINGFACE_AVAILABLE, "HuggingFace is not available")
class TestHuggingFaceModel(unittest.TestCase):
    """Tests for the HuggingFaceModel class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the cache
        self.cache_dir = tempfile.mkdtemp()

        # Mock the transformers module
        self.transformers_patcher = patch('src.models.huggingface_model.transformers')
        self.mock_transformers = self.transformers_patcher.start()

        # Mock the torch module
        self.torch_patcher = patch('src.models.huggingface_model.torch')
        self.mock_torch = self.torch_patcher.start()
        self.mock_torch.cuda.is_available.return_value = True

        # Mock the AutoModelForCausalLM class
        self.model_patcher = patch('src.models.huggingface_model.AutoModelForCausalLM')
        self.mock_model_class = self.model_patcher.start()
        self.mock_model = MagicMock()
        self.mock_model_class.from_pretrained.return_value = self.mock_model

        # Mock the AutoTokenizer class
        self.tokenizer_patcher = patch('src.models.huggingface_model.AutoTokenizer')
        self.mock_tokenizer_class = self.tokenizer_patcher.start()
        self.mock_tokenizer = MagicMock()
        self.mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        self.mock_tokenizer_class.from_pretrained.return_value = self.mock_tokenizer

        # Mock the pipeline function
        self.pipeline_patcher = patch('src.models.huggingface_model.pipeline')
        self.mock_pipeline = self.pipeline_patcher.start()
        self.mock_pipe = MagicMock()
        self.mock_pipe.return_value = [{"generated_text": "This is a test response."}]
        self.mock_pipeline.return_value = self.mock_pipe

        # Mock the SentenceTransformer class
        self.sentence_transformer_patcher = patch('src.models.huggingface_model.SentenceTransformer')
        self.mock_sentence_transformer = self.sentence_transformer_patcher.start()
        self.mock_embedding_model = MagicMock()
        self.mock_embedding_model.encode.return_value = [0.1, 0.2, 0.3]
        self.mock_sentence_transformer.return_value = self.mock_embedding_model

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patchers
        self.transformers_patcher.stop()
        self.torch_patcher.stop()
        self.model_patcher.stop()
        self.tokenizer_patcher.stop()
        self.pipeline_patcher.stop()
        self.sentence_transformer_patcher.stop()

        # Remove the temporary directory
        shutil.rmtree(self.cache_dir)

    def test_init(self):
        """Test initialization."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Check that the model was initialized correctly
        self.assertEqual(model.model_id, "test/model")
        self.assertEqual(model.cache_dir, self.cache_dir)
        self.assertEqual(model.device, "cuda")

        # Check that the tokenizer was loaded
        self.mock_tokenizer_class.from_pretrained.assert_called_once_with(
            "test/model",
            cache_dir=self.cache_dir,
            trust_remote_code=True
        )

        # Check that the model was loaded
        self.mock_model_class.from_pretrained.assert_called_once()

        # Check that the pipeline was created
        self.mock_pipeline.assert_called_once_with(
            "text-generation",
            model=self.mock_model,
            tokenizer=self.mock_tokenizer,
            device_map="auto"
        )

        # Check that the embedding model was loaded
        self.mock_sentence_transformer.assert_called_once()

    def test_generate(self):
        """Test text generation."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Generate text
        response = model.generate(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )

        # Check that the response is correct
        self.assertEqual(response, "This is a test response.")

        # Check that the pipeline was called
        self.mock_pipe.assert_called_once()

    def test_generate_stream(self):
        """Test streaming text generation."""
        # Mock the TextStreamer class
        mock_streamer = MagicMock()
        self.mock_transformers.TextStreamer.return_value = mock_streamer

        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Generate streaming text
        chunks = list(model.generate_stream(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        ))

        # Check that the model.generate method was called
        self.mock_model.generate.assert_called_once()

    def test_get_token_count(self):
        """Test token counting."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Count tokens
        count = model.get_token_count("Hello, world!")

        # Check that the count is correct
        self.assertEqual(count, 5)

        # Check that the tokenizer was called
        self.mock_tokenizer.encode.assert_called_once_with("Hello, world!")

    def test_embed(self):
        """Test embedding generation."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Generate embeddings
        embedding = model.embed("Hello, world!")

        # Check that the embedding is correct
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

        # Check that the embedding model was called
        self.mock_embedding_model.encode.assert_called_once_with("Hello, world!")

    def test_batch_embed(self):
        """Test batch embedding generation."""
        # Mock the embedding model to return different embeddings for different texts
        self.mock_embedding_model.encode.side_effect = lambda texts, **kwargs: [
            [0.1, 0.2, 0.3] if i == 0 else [0.4, 0.5, 0.6]
            for i in range(len(texts))
        ]

        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Generate batch embeddings
        embeddings = model.batch_embed(["Hello, world!", "Goodbye, world!"])

        # Check that the embeddings are correct
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        # Check that the embedding model was called
        self.mock_embedding_model.encode.assert_called_once_with(["Hello, world!", "Goodbye, world!"])

    def test_get_model_info(self):
        """Test getting model information."""
        # Mock the model config
        self.mock_model.config.to_dict.return_value = {
            "model_type": "test",
            "vocab_size": 32000,
            "hidden_size": 768,
            "num_hidden_layers": 12,
            "num_attention_heads": 12,
            "max_position_embeddings": 2048
        }

        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Get model info
        info = model.get_model_info()

        # Check that the info is correct
        self.assertEqual(info["model_id"], "test/model")
        self.assertEqual(info["available"], True)
        self.assertEqual(info["device"], "cuda")
        self.assertEqual(info["backend"], "huggingface")
        self.assertEqual(info["model_type"], "test")
        self.assertEqual(info["vocab_size"], 32000)
        self.assertEqual(info["hidden_size"], 768)
        self.assertEqual(info["num_hidden_layers"], 12)
        self.assertEqual(info["num_attention_heads"], 12)
        self.assertEqual(info["max_position_embeddings"], 2048)
        self.assertEqual(info["embedding_model"], "sentence-transformers/all-MiniLM-L6-v2")

    def test_is_available(self):
        """Test checking if the model is available."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Check if the model is available
        available = model.is_available()

        # Check that the result is correct
        self.assertTrue(available)

    def test_format_prompt(self):
        """Test prompt formatting."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Format a prompt without system prompt
        formatted = model.format_prompt("Hello, world!")

        # Check that the formatting is correct
        self.assertEqual(formatted, "Hello, world!")

        # Format a prompt with system prompt
        formatted = model.format_prompt("Hello, world!", "You are a helpful assistant.")

        # Check that the formatting is correct
        self.assertIn("Hello, world!", formatted)
        self.assertIn("You are a helpful assistant.", formatted)

    def test_share_model(self):
        """Test model sharing."""
        # Initialize the model
        model = HuggingFaceModel(
            model_id="test/model",
            cache_dir=self.cache_dir
        )

        # Share the model
        result = model.share_model("ollama")

        # Check that the result is correct
        self.assertTrue(result)

        # Check that the metadata file was created
        model_name = "model"  # From test/model
        metadata_path = os.path.join(self.cache_dir, "shared_models", f"{model_name}.json")
        self.assertTrue(os.path.exists(metadata_path))

        # Check that the metadata is correct
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        self.assertEqual(metadata["model_id"], "test/model")
        self.assertEqual(metadata["model_name"], "model")
        self.assertEqual(metadata["device"], "cuda")
        self.assertEqual(metadata["backend"], "huggingface")
        self.assertEqual(metadata["target_backend"], "ollama")
        self.assertEqual(metadata["embedding_model"], "sentence-transformers/all-MiniLM-L6-v2")


if __name__ == "__main__":
    unittest.main()
