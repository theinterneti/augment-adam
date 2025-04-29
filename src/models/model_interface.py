#!/usr/bin/env python3
"""
Model Interface for Augment Adam (DEPRECATED)

This module defines the interface for all model backends used in the system.
This interface is deprecated and will be removed in a future version.
Please use model_backend.py instead.
"""

import warnings
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Generator, Union

# Show deprecation warning
warnings.warn(
    "ModelInterface is deprecated and will be removed in a future version. "
    "Please use ModelBackend from model_backend.py instead.",
    DeprecationWarning,
    stacklevel=2
)


class ModelInterface(ABC):
    """
    Base interface for all model backends in the system.

    DEPRECATED: This interface is deprecated and will be removed in a future version.
    Please use ModelBackend from model_backend.py instead.
    """

    @abstractmethod
    def __init__(self, model_id: str, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the model interface.

        Args:
            model_id: The ID of the model.
            model_config: Optional configuration for the model.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
