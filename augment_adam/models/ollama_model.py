"""Ollama Model implementation.

This module provides an implementation of the ModelInterface for Ollama models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
import requests

from augment_adam.core.errors import (
    ResourceError, NetworkError, wrap_error, log_error, ErrorCategory
)
from augment_adam.models.model_interface import ModelInterface

logger = logging.getLogger(__name__)


class OllamaModel(ModelInterface):
    """Ollama Model implementation.

    This class provides an implementation of the ModelInterface for Ollama models.

    Attributes:
        model_name: The name of the Ollama model to use
        base_url: The base URL for the Ollama API
    """

    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        """Initialize the Ollama Model.

        Args:
            model_name: The name of the Ollama model to use
            base_url: The base URL for the Ollama API
            **kwargs: Additional parameters for the Ollama API
        """
        try:
            self.model_name = model_name
            self.base_url = base_url

            # Check if the model is available
            self._check_model_availability()

            logger.info(f"Initialized Ollama Model: {model_name}")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to initialize Ollama Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": model_name}
            )
            log_error(error, logger=logger)
            raise error

    def _check_model_availability(self) -> None:
        """Check if the model is available.

        Raises:
            ResourceError: If the model is not available
        """
        try:
            # Get list of models
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()

            # Check if the model is in the list
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]

            if self.model_name not in model_names:
                logger.warning(f"Model {self.model_name} not found in Ollama. Available models: {model_names}")
                # We won't raise an error here, as the model might be pulled later
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to check model availability",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Generate text based on a prompt.

        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling)
            stop: List of strings that stop generation when encountered
            **kwargs: Additional model-specific parameters

        Returns:
            The generated text
        """
        try:
            # Prepare request data
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stop": stop or []
                }
            }

            # Add additional options
            for key, value in kwargs.items():
                if key not in data["options"]:
                    data["options"][key] = value

            # Generate completion
            response = requests.post(f"{self.base_url}/api/generate", json=data)
            response.raise_for_status()

            # Extract generated text
            result = response.json()
            generated_text = result.get("response", "")

            logger.info(f"Generated {len(generated_text)} characters with {self.model_name}")
            return generated_text
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate text with Ollama Model",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            return f"Error generating text: {str(error)}"

    def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Generate text based on a prompt, streaming the results.

        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling)
            stop: List of strings that stop generation when encountered
            **kwargs: Additional model-specific parameters

        Returns:
            A generator yielding chunks of generated text
        """
        try:
            # Prepare request data
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stop": stop or []
                }
            }

            # Add additional options
            for key, value in kwargs.items():
                if key not in data["options"]:
                    data["options"][key] = value

            # Generate streaming completion
            response = requests.post(f"{self.base_url}/api/generate", json=data, stream=True)
            response.raise_for_status()

            # Yield chunks of generated text
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode JSON: {line}")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to stream text with Ollama Model",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            yield f"Error generating text: {str(error)}"

    def get_token_count(self, text: str) -> int:
        """Get the number of tokens in a text.

        Args:
            text: The text to count tokens for

        Returns:
            The number of tokens
        """
        try:
            # Prepare request data
            data = {
                "model": self.model_name,
                "prompt": text
            }

            # Get token count
            response = requests.post(f"{self.base_url}/api/tokenize", json=data)
            response.raise_for_status()

            # Extract token count
            result = response.json()
            tokens = result.get("tokens", [])

            return len(tokens)
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to count tokens with Ollama Model",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)

            # Fall back to a simple approximation
            return len(text.split()) * 4 // 3  # Rough approximation

    def get_embedding(self, text: str) -> List[float]:
        """Get the embedding for a text.

        Args:
            text: The text to get an embedding for

        Returns:
            The embedding as a list of floats
        """
        try:
            # Prepare request data
            data = {
                "model": self.model_name,
                "prompt": text
            }

            # Get embedding
            response = requests.post(f"{self.base_url}/api/embeddings", json=data)
            response.raise_for_status()

            # Extract embedding
            result = response.json()
            embedding = result.get("embedding", [])

            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to get embedding with Ollama Model",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)

            # Return a zero vector as fallback (assuming 4096 dimensions)
            return [0.0] * 4096

    def get_token_probabilities(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_k: int = 50,
        **kwargs
    ) -> List[Tuple[str, float]]:
        """Get token probabilities for the next token.

        Args:
            prompt: The prompt to get probabilities for
            temperature: Sampling temperature (higher = more random)
            top_k: Number of top tokens to return
            **kwargs: Additional model-specific parameters

        Returns:
            List of (token, probability) tuples
        """
        try:
            # Prepare request data
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "top_k": top_k
                }
            }

            # Add additional options
            for key, value in kwargs.items():
                if key not in data["options"]:
                    data["options"][key] = value

            # Generate completions with logprobs
            data["options"]["logprobs"] = True

            # Make request
            response = requests.post(f"{self.base_url}/api/generate", json=data)
            response.raise_for_status()

            # Extract token probabilities
            result = response.json()

            # Check if logprobs are available
            if "logprobs" in result:
                logprobs = result["logprobs"]
                tokens = []
                probs = []

                # Convert logprobs to probs
                for token, logprob in logprobs.items():
                    tokens.append(token)
                    probs.append(np.exp(logprob))

                # Normalize probabilities
                total_prob = sum(probs)
                if total_prob > 0:
                    probs = [p / total_prob for p in probs]

                # Sort by probability (descending)
                token_probs = list(zip(tokens, probs))
                token_probs.sort(key=lambda x: x[1], reverse=True)

                # Return top-k
                return token_probs[:top_k]
            else:
                # If logprobs are not available, generate multiple completions
                # and use the first token of each as a proxy for token probabilities
                tokens = []

                # Generate multiple completions
                for _ in range(min(5, top_k)):
                    try:
                        data["options"]["temperature"] = temperature + random.uniform(-0.1, 0.1)
                        response = requests.post(f"{self.base_url}/api/generate", json=data)
                        response.raise_for_status()
                        result = response.json()

                        if "response" in result and result["response"]:
                            tokens.append(result["response"][0])
                    except Exception:
                        pass

                # Count token frequencies
                token_counts = {}
                for token in tokens:
                    token_counts[token] = token_counts.get(token, 0) + 1

                # Convert to probabilities
                total_count = sum(token_counts.values())
                token_probs = [(token, count / total_count) for token, count in token_counts.items()]

                # Sort by probability (descending)
                token_probs.sort(key=lambda x: x[1], reverse=True)

                # If we have no tokens, return a default
                if not token_probs:
                    return [(" ", 1.0)]

                return token_probs
        except Exception as e:
            logger.warning(f"Error getting token probabilities: {e}")
            return [(" ", 1.0)]  # Return a default token with probability 1.0

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.

        Returns:
            A dictionary containing model information
        """
        try:
            # Get model information
            response = requests.get(f"{self.base_url}/api/show?name={self.model_name}")
            response.raise_for_status()

            # Extract model information
            result = response.json()

            return {
                "name": self.model_name,
                "provider": "Ollama",
                "type": "chat",
                "max_tokens": result.get("parameters", {}).get("num_ctx", 4096),
                "embedding_dimensions": 4096,  # Most Ollama models use 4096 dimensions
                "details": result
            }
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to get model information",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)

            # Return basic information
            return {
                "name": self.model_name,
                "provider": "Ollama",
                "type": "chat",
                "max_tokens": 4096,  # Default context size
                "embedding_dimensions": 4096  # Default embedding size
            }
