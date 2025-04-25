"""Anthropic Model implementation.

This module provides an implementation of the ModelInterface for Anthropic models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
import anthropic

from augment_adam.core.errors import (
    ResourceError, NetworkError, wrap_error, log_error, ErrorCategory
)
from augment_adam.models.model_interface import ModelInterface

logger = logging.getLogger(__name__)


class AnthropicModel(ModelInterface):
    """Anthropic Model implementation.
    
    This class provides an implementation of the ModelInterface for Anthropic models.
    
    Attributes:
        model_name: The name of the Anthropic model to use
        client: The Anthropic client
        api_key: The Anthropic API key
    """
    
    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize the Anthropic Model.
        
        Args:
            model_name: The name of the Anthropic model to use
            api_key: The Anthropic API key (if None, use environment variable)
            **kwargs: Additional parameters for the Anthropic client
        """
        try:
            self.model_name = model_name
            
            # Get API key from environment variable if not provided
            self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ResourceError(
                    message="Anthropic API key not provided",
                    details={"model_name": model_name}
                )
            
            # Initialize Anthropic client
            self.client = anthropic.Anthropic(
                api_key=self.api_key
            )
            
            logger.info(f"Initialized Anthropic Model: {model_name}")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to initialize Anthropic Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": model_name}
            )
            log_error(error, logger=logger)
            raise error
    
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
            # Generate message
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            
            # Extract generated text
            generated_text = response.content[0].text
            
            logger.info(f"Generated {len(generated_text)} characters with {self.model_name}")
            return generated_text
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate text with Anthropic Model",
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
            # Generate streaming message
            with self.client.messages.stream(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            ) as stream:
                # Yield chunks of generated text
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to stream text with Anthropic Model",
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
            # Use the Anthropic tokenizer
            tokens = self.client.count_tokens(text)
            return tokens.token_count
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to count tokens with Anthropic Model",
                category=ErrorCategory.RESOURCE,
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
        # Anthropic doesn't provide an embeddings API, so we'll raise an error
        raise NotImplementedError("Anthropic does not provide an embeddings API")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.
        
        Returns:
            A dictionary containing model information
        """
        # Model context windows
        context_windows = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000
        }
        
        return {
            "name": self.model_name,
            "provider": "Anthropic",
            "type": "chat",
            "max_tokens": context_windows.get(self.model_name, 100000),
            "embedding_dimensions": None  # Anthropic doesn't provide embeddings
        }
