#!/usr/bin/env python3
"""
Model Registry for Augment Adam

This module provides a registry for model backends, allowing for easy
switching between different model implementations.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Type

from .model_backend import ModelBackend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for model backends."""

    def __init__(self):
        """Initialize the model registry."""
        self.backends = {}
        self.models = {}
        
    def register_backend(self, backend_name: str, backend_class: Type[ModelBackend]):
        """
        Register a model backend.

        Args:
            backend_name: The name of the backend.
            backend_class: The backend class.
        """
        self.backends[backend_name] = backend_class
        logger.info(f"Registered backend: {backend_name}")
        
    def create_model(
        self,
        backend_name: str,
        model_id: str,
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[ModelBackend]:
        """
        Create a model instance.

        Args:
            backend_name: The name of the backend to use.
            model_id: The ID of the model.
            model_config: Optional configuration for the model.
            **kwargs: Additional arguments for model initialization.

        Returns:
            The model instance, or None if the backend is not registered.
        """
        if backend_name not in self.backends:
            logger.error(f"Backend not registered: {backend_name}")
            return None
            
        try:
            # Create the model instance
            model = self.backends[backend_name](
                model_id=model_id,
                model_config=model_config,
                **kwargs
            )
            
            # Register the model
            model_key = f"{backend_name}:{model_id}"
            self.models[model_key] = model
            
            logger.info(f"Created model: {model_key}")
            return model
        except Exception as e:
            logger.error(f"Error creating model {model_id} with backend {backend_name}: {e}")
            return None
            
    def get_model(self, backend_name: str, model_id: str) -> Optional[ModelBackend]:
        """
        Get a model instance.

        Args:
            backend_name: The name of the backend.
            model_id: The ID of the model.

        Returns:
            The model instance, or None if not found.
        """
        model_key = f"{backend_name}:{model_id}"
        return self.models.get(model_key)
        
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all registered models.

        Returns:
            A list of model information dictionaries.
        """
        return [
            {
                "backend": backend_name,
                "model_id": model_id,
                "info": model.get_model_info() if model.is_available() else {"available": False}
            }
            for (backend_name, model_id), model in self.models.items()
        ]
        
    def list_backends(self) -> List[str]:
        """
        List all registered backends.

        Returns:
            A list of backend names.
        """
        return list(self.backends.keys())
        
    def share_model(
        self,
        source_backend: str,
        source_model_id: str,
        target_backend: str
    ) -> bool:
        """
        Share a model between backends.

        Args:
            source_backend: The name of the source backend.
            source_model_id: The ID of the source model.
            target_backend: The name of the target backend.

        Returns:
            True if successful, False otherwise.
        """
        # Get the source model
        source_model = self.get_model(source_backend, source_model_id)
        if not source_model:
            logger.error(f"Source model not found: {source_backend}:{source_model_id}")
            return False
            
        # Check if the target backend is registered
        if target_backend not in self.backends:
            logger.error(f"Target backend not registered: {target_backend}")
            return False
            
        # Share the model
        return source_model.share_model(target_backend)


# Singleton instance
_registry = None


def get_registry() -> ModelRegistry:
    """
    Get the singleton ModelRegistry instance.

    Returns:
        The ModelRegistry instance.
    """
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
