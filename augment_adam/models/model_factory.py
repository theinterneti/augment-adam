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

# Recommended models for different use cases
RECOMMENDED_MODELS = {
    "huggingface": {
        "default": "mistralai/Mistral-7B-Instruct-v0.2",
        "small": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "medium": "microsoft/phi-2",
        "large": "meta-llama/Llama-3-8b-chat-hf",
        "xl": "meta-llama/Llama-3-70b-chat-hf",
        "code": "codellama/CodeLlama-7b-instruct-hf",
        "embedding": "sentence-transformers/all-MiniLM-L6-v2",
        # Small models with large context windows
        "small_context": "Qwen/Qwen1.5-0.5B-Chat",  # 32K context
        "tiny_context": "Qwen/Qwen1.5-0.5B-Chat",   # 32K context
        "medium_context": "Qwen/Qwen1.5-1.8B-Chat", # 32K context
        "long_context": "Qwen/Qwen1.5-7B-Chat"      # 32K context
    },
    "ollama": {
        "default": "llama3",
        "small": "phi2",
        "medium": "mistral",
        "large": "llama3",
        "xl": "llama3:70b",
        "code": "codellama:7b",
        # Small models with large context windows
        "small_context": "qwen:0.5b",  # 32K context
        "tiny_context": "qwen:0.5b",   # 32K context
        "medium_context": "qwen:1.8b", # 32K context
        "long_context": "qwen:7b"      # 32K context
    }
}

# Default context window sizes for different model sizes
DEFAULT_CONTEXT_SIZES = {
    "small": 2048,
    "medium": 4096,
    "large": 8192,
    "xl": 16384,
    "small_context": 32768,
    "tiny_context": 32768,
    "medium_context": 32768,
    "long_context": 32768
}

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
        model_size: Optional[str] = None,
        **kwargs
    ) -> ModelInterface:
        """Create a model.

        Args:
            model_type: The type of model to create (defaults to huggingface)
            model_name: The name of the model
            model_size: The size of the model (small, medium, large, xl, code)
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

            # Set model name and context window size based on model_size if provided
            context_window_size = kwargs.get("context_window_size")
            if model_size and not model_name:
                if model_type in RECOMMENDED_MODELS and model_size in RECOMMENDED_MODELS[model_type]:
                    model_name = RECOMMENDED_MODELS[model_type][model_size]
                    logger.info(f"Using recommended {model_size} model: {model_name}")

                    # Set context window size if not explicitly provided
                    if not context_window_size and model_size in DEFAULT_CONTEXT_SIZES:
                        context_window_size = DEFAULT_CONTEXT_SIZES[model_size]
                        kwargs["context_window_size"] = context_window_size
                        logger.info(f"Using default context window size for {model_size}: {context_window_size}")
                else:
                    logger.warning(f"No recommended {model_size} model for {model_type}, using default")

            # Set default model name if not provided
            if not model_name:
                if model_type in RECOMMENDED_MODELS and "default" in RECOMMENDED_MODELS[model_type]:
                    model_name = RECOMMENDED_MODELS[model_type]["default"]
                elif model_type == "huggingface":
                    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
                elif model_type == "ollama":
                    model_name = "llama3"
                elif model_type == "openai":
                    model_name = "gpt-4o"
                elif model_type == "anthropic":
                    model_name = "claude-3-opus-20240229"

            # Set Monte Carlo parameters for small models
            if model_size in ["small", "tiny_context", "small_context"] and model_type in ["huggingface", "ollama"]:
                # Enable Monte Carlo by default for small models
                if "use_monte_carlo" not in kwargs:
                    kwargs["use_monte_carlo"] = True
                    logger.info(f"Enabling Monte Carlo sampling for small model: {model_name}")

                # Set higher number of particles for small models
                if "monte_carlo_particles" not in kwargs:
                    kwargs["monte_carlo_particles"] = 100
                    logger.info(f"Using 100 particles for Monte Carlo sampling with small model: {model_name}")

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
    model_type: str = "huggingface",
    model_name: Optional[str] = None,
    model_size: Optional[str] = None,
    **kwargs
) -> ModelInterface:
    """Create a model using the global Model Factory.

    Args:
        model_type: The type of model to create
        model_name: The name of the model
        model_size: The size of the model (small, medium, large, xl, code)
        **kwargs: Additional arguments for the model

    Returns:
        The created model
    """
    factory = get_model_factory()
    return factory.create_model(
        model_type=model_type,
        model_name=model_name,
        model_size=model_size,
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
        model_size = settings.get("model", {}).get("size", "medium")

        # Create model
        _default_model = create_model(
            model_type=model_type,
            model_name=model_name,
            model_size=model_size
        )

    return _default_model
