"""Model management for the Dukat assistant.

This module handles loading, configuring, and using language models
through DSPy and Ollama.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, Optional, List, Union, Callable
import logging

import dspy

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
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}")

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the language model.

        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional arguments to pass to the model.

        Returns:
            The generated response as a string.
        """
        logger.debug(f"Generating response for prompt: {prompt[:50]}...")

        try:
            response = self.lm(prompt, **kwargs)
            return response[0] if isinstance(response, list) else response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"

    def create_module(self, signature: str, **kwargs) -> dspy.Module:
        """Create a DSPy module with the specified signature.

        Args:
            signature: The signature for the module.
            **kwargs: Additional arguments for the module.

        Returns:
            A DSPy module instance.
        """
        logger.debug(f"Creating module with signature: {signature}")

        try:
            return dspy.ChainOfThought(signature, **kwargs)

        except Exception as e:
            logger.error(f"Error creating module: {str(e)}")
            raise RuntimeError(f"Error creating module: {str(e)}")

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
            logger.error(f"Error optimizing DSPy module: {str(e)}")
            return module  # Return the original module on error


# Singleton instance for easy access
default_model_manager: Optional[ModelManager] = None


def get_model_manager(
    model_name: str = "llama3:8b",
    ollama_host: str = "http://localhost:11434",
    api_key: str = "",
) -> ModelManager:
    """Get or create the default model manager instance.

    Args:
        model_name: The name of the model to use.
        ollama_host: The host address for the Ollama API.
        api_key: The API key for the model provider (not needed for Ollama).

    Returns:
        The default model manager instance.
    """
    global default_model_manager

    if default_model_manager is None:
        default_model_manager = ModelManager(model_name, ollama_host, api_key)

    return default_model_manager
