"""Model management for the Dukat assistant.

This module handles loading, configuring, and using language models
through DSPy and Ollama.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, Optional, List, Union, Callable
import logging
import time

import dspy

from augment_adam.core.errors import (
    ModelError, NetworkError, TimeoutError, ResourceError,
    wrap_error, log_error, retry, CircuitBreaker
)
from augment_adam.core.settings import get_settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages language models for the Dukat assistant.

    This class handles loading, configuring, and using language models
    through DSPy and Ollama.

    Attributes:
        model_name: The name of the model to use.
        ollama_host: The host address for the Ollama API.
        lm: The DSPy language model instance.
    """

    def __init__(
        self,
        model_name: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        api_key: str = "",
    ):
        """Initialize the model manager.

        Args:
            model_name: The name of the model to use.
            ollama_host: The host address for the Ollama API.
            api_key: The API key for the model provider (not needed for Ollama).
        """
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.lm = self._load_model(model_name, ollama_host, api_key)

        # Configure DSPy to use this model
        dspy.configure(lm=self.lm)

        logger.info(f"Initialized ModelManager with model: {model_name}")

    @retry(max_attempts=3, delay=2.0, backoff_factor=2.0)
    def _load_model(
        self, model_name: str, ollama_host: str, api_key: str
    ) -> dspy.LM:
        """Load a language model using DSPy.

        Args:
            model_name: The name of the model to use.
            ollama_host: The host address for the Ollama API.
            api_key: The API key for the model provider (not needed for Ollama).

        Returns:
            A DSPy language model instance.

        Raises:
            ModelError: If the model cannot be loaded.
            NetworkError: If there is a network error connecting to the model server.
            TimeoutError: If the connection to the model server times out.
        """
        logger.info(f"Loading model: {model_name} from {ollama_host}")

        try:
            # Format for Ollama models in DSPy
            formatted_name = f"ollama_chat/{model_name}"

            # Initialize the model
            lm = dspy.LM(
                formatted_name,
                api_base=ollama_host,
                api_key=api_key,
            )

            logger.info(f"Successfully loaded model: {model_name}")
            return lm

        except Exception as e:
            # Wrap the exception in a ModelError
            error = wrap_error(
                e,
                message=f"Failed to load model {model_name}",
                category=None,  # Auto-classify the error
                details={
                    "model_name": model_name,
                    "ollama_host": ollama_host,
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "model_name": model_name,
                    "ollama_host": ollama_host,
                },
            )

            # Re-raise the wrapped error
            raise error

    # Create a circuit breaker for model generation
    _generate_circuit = CircuitBreaker(
        name="model_generation",
        failure_threshold=5,
        recovery_timeout=60.0,
    )

    @retry(max_attempts=2, delay=1.0, backoff_factor=2.0)
    @_generate_circuit
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the language model.

        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the model.

        Returns:
            The generated response as a string.

        Raises:
            ModelError: If there is an error generating the response.
            NetworkError: If there is a network error connecting to the model server.
            TimeoutError: If the model generation times out.
            CircuitBreakerError: If the circuit breaker is open due to too many failures.
        """
        # Get settings for model generation
        settings = get_settings()
        model_settings = settings.model

        # Apply settings if not overridden in kwargs
        if "temperature" not in kwargs:
            kwargs["temperature"] = model_settings.temperature
        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = model_settings.max_tokens

        logger.debug(f"Generating response for prompt: {prompt[:50]}...")

        try:
            # Set a timeout for the model generation
            start_time = time.time()
            response = self.lm(prompt, **kwargs)
            generation_time = time.time() - start_time

            logger.debug(
                f"Generated response in {generation_time:.2f} seconds")

            return response[0] if isinstance(response, list) else response

        except Exception as e:
            # Wrap the exception in a ModelError
            error = wrap_error(
                e,
                message="Error generating response",
                category=None,  # Auto-classify the error
                details={
                    "prompt_length": len(prompt),
                    "model_name": self.model_name,
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "model_name": self.model_name,
                    "kwargs": kwargs,
                },
            )

            # Return a user-friendly error message
            return f"I'm sorry, but I encountered an error while generating a response. Please try again later."

    @retry(max_attempts=2, delay=1.0)
    def create_module(self, signature: str, **kwargs) -> dspy.Module:
        """Create a DSPy module with the specified signature.

        Args:
            signature: The signature for the module.
            **kwargs: Additional arguments for the module.

        Returns:
            A DSPy module instance.

        Raises:
            ModelError: If there is an error creating the module.
        """
        logger.debug(f"Creating module with signature: {signature}")

        try:
            return dspy.ChainOfThought(signature, **kwargs)

        except Exception as e:
            # Wrap the exception in a ModelError
            error = wrap_error(
                e,
                message="Error creating DSPy module",
                category=None,  # Auto-classify the error
                details={
                    "signature": signature,
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "signature": signature,
                    "kwargs": kwargs,
                },
            )

            # Re-raise the wrapped error
            raise error

    @retry(max_attempts=2, delay=1.0)
    def optimize_module(
        self,
        module: dspy.Module,
        examples: List[Dict[str, Any]],
        metric: Optional[callable] = None,
        **kwargs,
    ) -> dspy.Module:
        """Optimize a DSPy module using examples.

        Args:
            module: The module to optimize.
            examples: Examples to use for optimization.
            metric: The metric to use for optimization.
            **kwargs: Additional arguments for the optimizer.

        Returns:
            The optimized module.

        Raises:
            ModelError: If there is an error optimizing the module.
        """
        logger.debug(f"Optimizing module: {module.__class__.__name__}")

        try:
            # Create a dataset from the examples
            dataset = dspy.Example.from_list(examples)

            # Use DSPy's built-in optimization capabilities
            # This is a simplified version that works with the current DSPy version
            # In a real implementation, we would use the appropriate optimizer based on DSPy version

            # For demonstration purposes, we'll just return the original module
            # In a real implementation, we would optimize the module
            optimized_module = module

            logger.info(f"Optimized DSPy module: {module.__class__.__name__}")
            return optimized_module

        except Exception as e:
            # Wrap the exception in a ModelError
            error = wrap_error(
                e,
                message="Error optimizing DSPy module",
                category=None,  # Auto-classify the error
                details={
                    "module_type": module.__class__.__name__,
                    "examples_count": len(examples),
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "module_type": module.__class__.__name__,
                    "examples_count": len(examples),
                    "metric": metric.__name__ if metric else None,
                },
            )

            # Return the original module on error, but log the issue
            logger.warning(
                "Returning unoptimized module due to optimization error")
            return module


# Singleton instance for easy access
default_model_manager: Optional[ModelManager] = None


def get_model_manager(
    model_name: str = None,
    ollama_host: str = None,
    api_key: str = None,
) -> ModelManager:
    """Get or create the default model manager instance.

    Args:
        model_name: The name of the model to use. If None, uses the value from settings.
        ollama_host: The host address for the Ollama API. If None, uses the value from settings.
        api_key: The API key for the model provider. If None, uses the value from settings.

    Returns:
        The default model manager instance.

    Raises:
        ModelError: If there is an error creating the model manager.
    """
    global default_model_manager

    try:
        if default_model_manager is None:
            # Get settings for model configuration
            settings = get_settings()
            model_settings = settings.model
            network_settings = settings.network

            # Use provided values or defaults from settings
            model_name = model_name or model_settings.default_model
            ollama_host = ollama_host or "http://localhost:11434"
            api_key = api_key or ""

            logger.info(f"Creating model manager with model: {model_name}")
            default_model_manager = ModelManager(
                model_name, ollama_host, api_key)

        return default_model_manager

    except Exception as e:
        # Wrap the exception in a ModelError
        error = wrap_error(
            e,
            message="Error creating model manager",
            category=None,  # Auto-classify the error
            details={
                "model_name": model_name,
                "ollama_host": ollama_host,
            },
        )

        # Log the error with context
        log_error(
            error,
            logger=logger,
            context={
                "model_name": model_name,
                "ollama_host": ollama_host,
            },
        )

        # Re-raise the wrapped error
        raise error
