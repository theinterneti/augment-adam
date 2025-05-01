#!/usr/bin/env python3
"""
Ollama Model Implementation for Augment Adam

This module provides an implementation of the ModelBackend for Ollama models.
"""

import os
import json
import logging
import subprocess
import time
import platform
from typing import Dict, List, Any, Optional, Generator, Union

import requests

from .model_backend import ModelBackend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaModel(ModelBackend):
    """Ollama Model implementation."""

    def __init__(
        self,
        model_id: str,
        model_config: Optional[Dict[str, Any]] = None,
        cache_dir: Optional[str] = None,
        ollama_host: str = "http://localhost:11434",
        embedding_model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Ollama Model.

        Args:
            model_id: The ID of the model in Ollama.
            model_config: Optional configuration for the model.
            cache_dir: Directory to cache models (shared with HuggingFace).
            ollama_host: The host URL for Ollama API.
            embedding_model_id: ID of the embedding model to use.
            **kwargs: Additional arguments for model initialization.
        """
        self.model_id = model_id
        self.model_config = model_config or {}
        self.ollama_host = ollama_host
        self.api_url = f"{ollama_host}/api"

        # Use a shared cache directory for both HuggingFace and Ollama
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_models")
        os.makedirs(self.cache_dir, exist_ok=True)

        # Set embedding model ID
        self.embedding_model_id = embedding_model_id or self.model_id

        # Ensure Ollama is running
        self._ensure_ollama_running()

        # Check if model exists in Ollama, if not, try to create it from shared models
        if not self._model_exists():
            self._create_model_from_shared()

    def _ensure_ollama_running(self):
        """Ensure Ollama is running, start it if not."""
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                logger.info("Ollama is running")
                return True
        except requests.exceptions.ConnectionError:
            logger.info("Ollama is not running, attempting to start it")

        try:
            # Check if ollama command is available
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Ollama is not installed")
                return False

            # Start Ollama in the background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

            # Wait for Ollama to start
            for _ in range(10):
                time.sleep(1)
                try:
                    response = requests.get(f"{self.api_url}/tags")
                    if response.status_code == 200:
                        logger.info("Ollama started successfully")
                        return True
                except requests.exceptions.ConnectionError:
                    pass

            logger.error("Failed to start Ollama")
            return False
        except Exception as e:
            logger.error(f"Error starting Ollama: {e}")
            return False

    def _model_exists(self) -> bool:
        """Check if the model exists in Ollama."""
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model.get("name") == self.model_id:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking if model exists: {e}")
            return False

    def _create_model_from_shared(self) -> bool:
        """
        Create an Ollama model from a shared model.

        This allows sharing models between HuggingFace and Ollama.
        """
        try:
            # Get model name without version tag
            model_name = self.model_id.split(":")[0] if ":" in self.model_id else self.model_id

            # Check if we have a shared model metadata file
            shared_paths_dir = os.path.join(self.cache_dir, "shared_models")
            metadata_path = os.path.join(shared_paths_dir, f"{model_name}.json")

            if not os.path.exists(metadata_path):
                logger.warning(f"No shared model metadata found for {model_name}")
                return False

            # Read the metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            model_path = metadata.get("model_path")
            modelfile_path = metadata.get("modelfile_path")

            if not model_path or not os.path.exists(model_path):
                logger.warning(f"Shared model path does not exist: {model_path}")
                return False

            # Create a Modelfile if it doesn't exist
            if not modelfile_path or not os.path.exists(modelfile_path):
                modelfile_content = f"""
FROM {model_name}
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
"""

                modelfile_path = os.path.join(shared_paths_dir, f"{model_name}.modelfile")
                with open(modelfile_path, "w") as f:
                    f.write(modelfile_content)

            # Create the model in Ollama
            subprocess.run(
                ["ollama", "create", model_name, "-f", modelfile_path, "--path", model_path],
                check=True
            )

            logger.info(f"Created Ollama model {model_name} from shared model at {model_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating Ollama model from shared model: {e}")
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on the prompt.

        Args:
            prompt: The prompt to generate from.
            system_prompt: Optional system prompt for context.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (higher = more random).
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling).
            stop: List of strings that stop generation when encountered.
            **kwargs: Additional arguments for generation.

        Returns:
            The generated text.
        """
        if not self.is_available():
            raise RuntimeError("Model is not available. Please check if Ollama is running and the model is loaded.")

        try:
            # Prepare the request payload
            payload = {
                "model": self.model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                    "stop": stop if stop else []
                }
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Add additional options from kwargs
            for key, value in kwargs.items():
                if key not in payload["options"]:
                    payload["options"][key] = value

            # Make the request to Ollama
            response = requests.post(f"{self.api_url}/generate", json=payload)
            response.raise_for_status()

            # Parse the response
            result = response.json()
            return result.get("response", "")

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error generating text: {str(e)}"

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate text based on a prompt, streaming the results.

        Args:
            prompt: The prompt to generate from.
            system_prompt: Optional system prompt for context.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (higher = more random).
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling).
            stop: List of strings that stop generation when encountered.
            **kwargs: Additional arguments for generation.

        Returns:
            A generator yielding chunks of generated text.
        """
        if not self.is_available():
            yield "Model is not available. Please check if Ollama is running and the model is loaded."
            return

        try:
            # Prepare the request payload
            payload = {
                "model": self.model_id,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                    "stop": stop if stop else []
                }
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Add additional options from kwargs
            for key, value in kwargs.items():
                if key not in payload["options"]:
                    payload["options"][key] = value

            # Make the streaming request to Ollama
            response = requests.post(f"{self.api_url}/generate", json=payload, stream=True)
            response.raise_for_status()

            # Stream the response
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            logger.error(f"Error streaming text: {e}")
            yield f"Error streaming text: {str(e)}"

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the text.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens.
        """
        if not self.is_available():
            raise RuntimeError("Model is not available. Please check if Ollama is running and the model is loaded.")

        try:
            # Use Ollama's tokenize endpoint
            payload = {
                "model": self.model_id,
                "prompt": text
            }

            response = requests.post(f"{self.api_url}/tokenize", json=payload)
            response.raise_for_status()

            result = response.json()
            return len(result.get("tokens", []))

        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to a rough estimate
            return len(text.split())

    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for the given text.

        Args:
            text: The text to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            The embedding vector.
        """
        if not self.is_available():
            raise RuntimeError("Model is not available. Please check if Ollama is running and the model is loaded.")

        try:
            # Use Ollama's embeddings endpoint
            payload = {
                "model": self.model_id,
                "prompt": text
            }

            response = requests.post(f"{self.api_url}/embeddings", json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("embedding", [])

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RuntimeError(f"Error generating embedding: {str(e)}")

    def batch_embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: The texts to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            A list of embedding vectors.
        """
        return [self.embed(text, **kwargs) for text in texts]

    def format_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Format the prompt according to the model's requirements.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.

        Returns:
            The formatted prompt.
        """
        # Ollama handles system prompts separately in the API call,
        # so we just return the user prompt
        return prompt

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing model information.
        """
        if not self.is_available():
            return {
                "model_id": self.model_id,
                "available": False,
                "error": "Model not available",
                "backend": "ollama"
            }

        try:
            # Get model information from Ollama
            response = requests.get(f"{self.api_url}/show", params={"name": self.model_id})
            response.raise_for_status()

            result = response.json()
            return {
                "model_id": self.model_id,
                "available": True,
                "backend": "ollama",
                "model_type": result.get("modelfile", {}).get("from", "unknown"),
                "parameters": result.get("parameters", {}),
                "template": result.get("template", ""),
                "license": result.get("license", ""),
                "size": result.get("size", 0),
                "embedding_model": self.embedding_model_id
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "model_id": self.model_id,
                "available": True,
                "backend": "ollama",
                "error": str(e)
            }

    def is_available(self) -> bool:
        """
        Check if the model is available for use.

        Returns:
            True if the model is available, False otherwise.
        """
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model.get("name") == self.model_id:
                        return True
            return False
        except Exception:
            return False

    def share_model(self, target_backend: str) -> bool:
        """
        Share this model with another backend.

        Args:
            target_backend: The backend to share the model with.

        Returns:
            True if successful, False otherwise.
        """
        # Ollama models are already in a format that can't be easily shared with other backends
        logger.warning(f"Sharing Ollama models with {target_backend} is not supported")
        return False
