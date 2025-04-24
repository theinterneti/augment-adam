"""Model management for the Augment Adam assistant.

This module provides components for managing language models,
including interfaces for different model providers and caching.

Version: 0.1.0
Created: 2025-04-28
Updated: 2025-04-24
"""

from augment_adam.models.anthropic_model import AnthropicModel
from augment_adam.models.caching import ModelCache
from augment_adam.models.huggingface_model import HuggingFaceModel
from augment_adam.models.manager import ModelManager
from augment_adam.models.model_factory import ModelFactory, create_model, get_default_model
from augment_adam.models.model_interface import ModelInterface
from augment_adam.models.ollama_model import OllamaModel
from augment_adam.models.openai_model import OpenAIModel
from augment_adam.models.prompts import PromptTemplate, PromptManager

__all__ = [
    "AnthropicModel",
    "HuggingFaceModel",
    "ModelCache",
    "ModelFactory",
    "ModelInterface",
    "ModelManager",
    "OllamaModel",
    "OpenAIModel",
    "PromptTemplate",
    "PromptManager",
    "create_model",
    "get_default_model",
]
