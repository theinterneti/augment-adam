"""Model Factory for language models.

This module provides a factory for creating different types of language models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, ValidationError, wrap_error, log_error, ErrorCategory
)
from augment_adam.core.settings import get_settings
from augment_adam.models.model_interface import ModelInterface
from augment_adam.models.huggingface_model import HuggingFaceModel
from augment_adam.models.ollama_model import OllamaModel
from augment_adam.models.openai_model import OpenAIModel
from augment_adam.models.anthropic_model import AnthropicModel

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating different types of language models.

    This class provides methods for creating different types of language models.

    Attributes:
        model_types: Dictionary of model types
    """

    def __init__(self):
        """Initialize the Model Factory."""
        self.model_types = {
            "huggingface": HuggingFaceModel,
            "ollama": OllamaModel,
            "openai": OpenAIModel,
            "anthropic": AnthropicModel
        }

        # Local models are prioritized
        self.local_model_types = ["huggingface", "ollama"]
        self.cloud_model_types = ["openai", "anthropic"]

        logger.info("Initialized Model Factory")

    def create_model(
        self,
        model_type: str = "huggingface",
        model_name: Optional[str] = None,
        **kwargs
    ) -> ModelInterface:
        """Create a model.

        Args:
            model_type: The type of model to create (defaults to huggingface)
            model_name: The name of the model
            **kwargs: Additional arguments for the model

        Returns:
            The created model

        Raises:
            ValidationError: If the model type is not supported
        """
        try:
            # Get model class
            model_class = self.model_types.get(model_type)
            if not model_class:
                raise ValidationError(
                    message=f"Unsupported model type: {model_type}",
                    details={"supported_types": list(self.model_types.keys())}
                )

            # Set default model name if not provided
            if not model_name:
                if model_type == "huggingface":
                    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
                elif model_type == "ollama":
                    model_name = "llama3"
                elif model_type == "openai":
                    model_name = "gpt-4o"
                elif model_type == "anthropic":
                    model_name = "claude-3-opus-20240229"

            # Create model
            model = model_class(
                model_name=model_name,
                **kwargs
            )

            logger.info(f"Created {model_type} model: {model_name}")
            return model
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to create {model_type} model",
                category=ErrorCategory.VALIDATION,
                details={"model_type": model_type, "model_name": model_name}
            )
            log_error(error, logger=logger)

            # Try to fall back to a local model
            for fallback_type in self.local_model_types:
                if fallback_type != model_type:
                    try:
                        logger.info(f"Falling back to {fallback_type} model")
                        fallback_class = self.model_types.get(fallback_type)

                        # Set default model name for fallback
                        fallback_name = None
                        if fallback_type == "huggingface":
                            fallback_name = "mistralai/Mistral-7B-Instruct-v0.2"
                        elif fallback_type == "ollama":
                            fallback_name = "llama3"

                        return fallback_class(model_name=fallback_name)
                    except Exception as fallback_error:
                        logger.warning(f"Failed to create fallback {fallback_type} model: {fallback_error}")

            # If all else fails, raise the original error
            raise error


# Global instance for singleton pattern
_model_factory = None


def get_model_factory() -> ModelFactory:
    """Get the global Model Factory instance.

    Returns:
        The global Model Factory instance
    """
    global _model_factory

    if _model_factory is None:
        _model_factory = ModelFactory()

    return _model_factory


def create_model(
    model_type: str = "openai",
    model_name: Optional[str] = None,
    **kwargs
) -> ModelInterface:
    """Create a model using the global Model Factory.

    Args:
        model_type: The type of model to create
        model_name: The name of the model
        **kwargs: Additional arguments for the model

    Returns:
        The created model
    """
    factory = get_model_factory()
    return factory.create_model(
        model_type=model_type,
        model_name=model_name,
        **kwargs
    )


# Default model instance
_default_model = None


def get_default_model() -> ModelInterface:
    """Get the default model instance.

    Returns:
        The default model instance
    """
    global _default_model

    if _default_model is None:
        # Get settings
        settings = get_settings()

        # Get model settings, defaulting to huggingface
        model_type = settings.get("model", {}).get("type", "huggingface")
        model_name = settings.get("model", {}).get("name", None)

        # Create model
        _default_model = create_model(
            model_type=model_type,
            model_name=model_name
        )

    return _default_model
