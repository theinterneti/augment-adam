"""
Model interface for augment-adam.

This module defines the interface for models used in the augment-adam system.
"""

from typing import Dict, List, Any, Optional


class ModelInterface:
    """Base interface for all models in the system."""

    def __init__(self, model_id: str, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the model interface.

        Args:
            model_id: The ID of the model.
            model_config: Optional configuration for the model.
        """
        self.model_id = model_id
        self.model_config = model_config or {}

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on the prompt.

        Args:
            prompt: The prompt to generate from.
            **kwargs: Additional arguments for generation.

        Returns:
            The generated text.
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for the given text.

        Args:
            text: The text to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            The embedding vector.
        """
        raise NotImplementedError("Subclasses must implement embed()")

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

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize the given text.

        Args:
            text: The text to tokenize.

        Returns:
            A list of tokens.
        """
        raise NotImplementedError("Subclasses must implement tokenize()")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the text.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens.
        """
        return len(self.tokenize(text))
