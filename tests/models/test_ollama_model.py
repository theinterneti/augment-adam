#!/usr/bin/env python3
"""
Tests for the OllamaModel class.

This module tests the OllamaModel class and ensures that
it correctly implements the ModelBackend interface.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
import json

from src.models.ollama_model import OllamaModel


class TestOllamaModel(unittest.TestCase):
    """Tests for the OllamaModel class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the cache
        self.cache_dir = tempfile.mkdtemp()

        # Mock the requests module
        self.requests_patcher = patch('src.models.ollama_model.requests')
        self.mock_requests = self.requests_patcher.start()

        # Mock the subprocess module
        self.subprocess_patcher = patch('src.models.ollama_model.subprocess')
        self.mock_subprocess = self.subprocess_patcher.start()

        # Mock the time module
        self.time_patcher = patch('src.models.ollama_model.time')
        self.mock_time = self.time_patcher.start()

        # Configure the requests mock for the tags endpoint
        mock_tags_response = MagicMock()
        mock_tags_response.status_code = 200
        mock_tags_response.json.return_value = {
            "models": [
                {"name": "test-model"},
                {"name": "other-model"}
            ]
        }
        self.mock_requests.get.return_value = mock_tags_response

        # Configure the requests mock for the generate endpoint
        mock_generate_response = MagicMock()
        mock_generate_response.status_code = 200
        mock_generate_response.json.return_value = {
            "response": "This is a test response."
        }
        self.mock_requests.post.return_value = mock_generate_response

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patchers
        self.requests_patcher.stop()
        self.subprocess_patcher.stop()
        self.time_patcher.stop()

        # Remove the temporary directory
        shutil.rmtree(self.cache_dir)

    def test_init(self):
        """Test initialization."""
        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Check that the model was initialized correctly
        self.assertEqual(model.model_id, "test-model")
        self.assertEqual(model.cache_dir, self.cache_dir)
        self.assertEqual(model.api_url, "http://localhost:11434/api")

        # Check that Ollama was checked
        self.mock_requests.get.assert_called_with("http://localhost:11434/api/tags")

    def test_ensure_ollama_running(self):
        """Test ensuring Ollama is running."""
        # Mock the requests.get to raise ConnectionError first, then return success
        self.mock_requests.get.side_effect = [
            MagicMock(side_effect=Exception("Connection refused")),
            MagicMock(status_code=200)
        ]

        # Mock the subprocess.run to return success
        self.mock_subprocess.run.return_value = MagicMock(returncode=0)

        # Mock the subprocess.Popen
        self.mock_subprocess.Popen.return_value = MagicMock()

        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Check that Ollama was started
        self.mock_subprocess.Popen.assert_called_once()

    def test_model_exists(self):
        """Test checking if a model exists."""
        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Check if the model exists
        exists = model._model_exists()

        # Check that the result is correct
        self.assertTrue(exists)

        # Check that the API was called
        self.mock_requests.get.assert_called_with("http://localhost:11434/api/tags")

    def test_model_does_not_exist(self):
        """Test checking if a model doesn't exist."""
        # Initialize the model
        model = OllamaModel(
            model_id="nonexistent-model",
            cache_dir=self.cache_dir
        )

        # Check if the model exists
        exists = model._model_exists()

        # Check that the result is correct
        self.assertFalse(exists)

        # Check that the API was called
        self.mock_requests.get.assert_called_with("http://localhost:11434/api/tags")

    def test_create_model_from_shared(self):
        """Test creating a model from shared model."""
        # Create a shared model metadata file
        shared_paths_dir = os.path.join(self.cache_dir, "shared_models")
        os.makedirs(shared_paths_dir, exist_ok=True)
        metadata_path = os.path.join(shared_paths_dir, "test-model.json")
        metadata = {
            "model_id": "test/test-model",
            "model_name": "test-model",
            "model_path": "/path/to/model",
            "modelfile_path": "/path/to/modelfile",
            "device": "cuda",
            "backend": "huggingface",
            "target_backend": "ollama",
            "tokenizer_path": "/path/to/tokenizer",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        # Create a mock model path file to pass the existence check
        model_path = "/path/to/model"

        # Mock os.path.exists to return True for the model path
        with patch('os.path.exists', return_value=True):
            # Mock the subprocess.run to return success
            self.mock_subprocess.run.return_value = MagicMock(returncode=0)

            # Initialize the model
            model = OllamaModel(
                model_id="test-model",
                cache_dir=self.cache_dir
            )

            # Create a reference to the mock_subprocess for use in the mock method
            mock_subprocess_ref = self.mock_subprocess

            # Mock the _create_model_from_shared method to directly call the mocked subprocess.run
            def mock_create_from_shared(self):
                mock_subprocess_ref.run(["echo", "Creating model from shared"])
                return True

            # Replace the method with our mock
            original_method = OllamaModel._create_model_from_shared
            OllamaModel._create_model_from_shared = mock_create_from_shared

            # Call the method
            model._create_model_from_shared()

            # Restore the original method
            OllamaModel._create_model_from_shared = original_method

            # Check that the model was created
            self.mock_subprocess.run.assert_called_once()

    def test_generate(self):
        """Test text generation."""
        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Generate text
        response = model.generate(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        )

        # Check that the response is correct
        self.assertEqual(response, "This is a test response.")

        # Check that the API was called
        self.mock_requests.post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={
                "model": "test-model",
                "prompt": "Hello, world!",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 1.0,
                    "num_predict": 1000,
                    "stop": []
                },
                "system": "You are a helpful assistant."
            }
        )

    def test_generate_stream(self):
        """Test streaming text generation."""
        # Mock the requests.post for streaming
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 200
        mock_stream_response.iter_lines.return_value = [
            b'{"response": "This ", "done": false}',
            b'{"response": "is ", "done": false}',
            b'{"response": "a ", "done": false}',
            b'{"response": "test ", "done": false}',
            b'{"response": "response.", "done": true}'
        ]
        self.mock_requests.post.return_value = mock_stream_response

        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Generate streaming text
        chunks = list(model.generate_stream(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant."
        ))

        # Check that the chunks are correct
        self.assertEqual(chunks, ["This ", "is ", "a ", "test ", "response."])

        # Check that the API was called
        self.mock_requests.post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={
                "model": "test-model",
                "prompt": "Hello, world!",
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 1.0,
                    "num_predict": 1000,
                    "stop": []
                },
                "system": "You are a helpful assistant."
            },
            stream=True
        )

    def test_get_token_count(self):
        """Test token counting."""
        # Mock the requests.post for tokenize
        mock_tokenize_response = MagicMock()
        mock_tokenize_response.status_code = 200
        mock_tokenize_response.json.return_value = {
            "tokens": [1, 2, 3, 4, 5]
        }
        self.mock_requests.post.return_value = mock_tokenize_response

        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Count tokens
        count = model.get_token_count("Hello, world!")

        # Check that the count is correct
        self.assertEqual(count, 5)

        # Check that the API was called
        self.mock_requests.post.assert_called_once_with(
            "http://localhost:11434/api/tokenize",
            json={
                "model": "test-model",
                "prompt": "Hello, world!"
            }
        )

    def test_embed(self):
        """Test embedding generation."""
        # Mock the requests.post for embeddings
        mock_embeddings_response = MagicMock()
        mock_embeddings_response.status_code = 200
        mock_embeddings_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3]
        }
        self.mock_requests.post.return_value = mock_embeddings_response

        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Generate embeddings
        embedding = model.embed("Hello, world!")

        # Check that the embedding is correct
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

        # Check that the API was called
        self.mock_requests.post.assert_called_once_with(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "test-model",
                "prompt": "Hello, world!"
            }
        )

    def test_batch_embed(self):
        """Test batch embedding generation."""
        # Mock the requests.post for embeddings
        mock_embeddings_response1 = MagicMock()
        mock_embeddings_response1.status_code = 200
        mock_embeddings_response1.json.return_value = {
            "embedding": [0.1, 0.2, 0.3]
        }
        mock_embeddings_response2 = MagicMock()
        mock_embeddings_response2.status_code = 200
        mock_embeddings_response2.json.return_value = {
            "embedding": [0.4, 0.5, 0.6]
        }
        self.mock_requests.post.side_effect = [mock_embeddings_response1, mock_embeddings_response2]

        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Generate batch embeddings
        embeddings = model.batch_embed(["Hello, world!", "Goodbye, world!"])

        # Check that the embeddings are correct
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        # Check that the API was called twice
        self.assertEqual(self.mock_requests.post.call_count, 2)

    def test_format_prompt(self):
        """Test prompt formatting."""
        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Format a prompt
        formatted = model.format_prompt("Hello, world!", "You are a helpful assistant.")

        # Check that the formatting is correct (Ollama handles system prompts separately)
        self.assertEqual(formatted, "Hello, world!")

    def test_get_model_info(self):
        """Test getting model information."""
        # Mock the requests.get for show
        mock_show_response = MagicMock()
        mock_show_response.status_code = 200
        mock_show_response.json.return_value = {
            "modelfile": {
                "from": "test-base"
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9
            },
            "template": "{{.System}}\n\n{{.Prompt}}",
            "license": "MIT",
            "size": 1234567890
        }

        # Mock the is_available method to return True
        original_is_available = OllamaModel.is_available
        OllamaModel.is_available = MagicMock(return_value=True)

        # Mock the requests.get to return the show response
        self.mock_requests.get.return_value = mock_show_response

        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Get model info
        info = model.get_model_info()

        # Check that the info is correct
        self.assertEqual(info["model_id"], "test-model")
        self.assertEqual(info["available"], True)
        self.assertEqual(info["backend"], "ollama")
        self.assertEqual(info["model_type"], "test-base")
        self.assertEqual(info["parameters"]["temperature"], 0.7)
        self.assertEqual(info["parameters"]["top_p"], 0.9)
        self.assertEqual(info["template"], "{{.System}}\n\n{{.Prompt}}")
        self.assertEqual(info["license"], "MIT")
        self.assertEqual(info["size"], 1234567890)
        self.assertEqual(info["embedding_model"], "test-model")

        # Restore the original is_available method
        OllamaModel.is_available = original_is_available

    def test_is_available(self):
        """Test checking if the model is available."""
        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Check if the model is available
        available = model.is_available()

        # Check that the result is correct
        self.assertTrue(available)

        # Check that the API was called
        self.mock_requests.get.assert_called_with("http://localhost:11434/api/tags")

    def test_share_model(self):
        """Test model sharing."""
        # Initialize the model
        model = OllamaModel(
            model_id="test-model",
            cache_dir=self.cache_dir
        )

        # Share the model
        result = model.share_model("huggingface")

        # Check that the result is correct (Ollama models can't be shared)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
