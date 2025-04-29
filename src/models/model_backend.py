#!/usr/bin/env python3
"""
Model Backend Interface for Augment Adam

This module defines the abstract base class for all model backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Generator, Union, Tuple


class ModelBackend(ABC):
    """Abstract base class for all model backends."""

    @abstractmethod
    def __init__(
        self,
        model_id: str,
        model_config: Optional[Dict[str, Any]] = None,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the model backend.

        Args:
            model_id: The ID of the model.
            model_config: Optional configuration for the model.
            cache_dir: Directory to cache models.
            **kwargs: Additional arguments for model initialization.
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
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
            top_p: Nucleus sampling parameter.
            stop: List of strings that stop generation when encountered.
            **kwargs: Additional arguments for generation.

        Returns:
            The generated text.
        """
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
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
            top_p: Nucleus sampling parameter.
            stop: List of strings that stop generation when encountered.
            **kwargs: Additional arguments for generation.

        Returns:
            A generator yielding chunks of generated text.
        """
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the text.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens.
        """
        pass

    @abstractmethod
    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for the given text.

        Args:
            text: The text to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            The embedding vector.
        """
        pass

    @abstractmethod
    def batch_embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: The texts to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            A list of embedding vectors.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing model information.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the model is available for use.

        Returns:
            True if the model is available, False otherwise.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def share_model(self, target_backend: str) -> bool:
        """
        Share this model with another backend.

        Args:
            target_backend: The backend to share the model with.

        Returns:
            True if successful, False otherwise.
        """
        pass
