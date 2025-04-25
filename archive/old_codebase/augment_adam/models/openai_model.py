"""OpenAI Model implementation.

This module provides an implementation of the ModelInterface for OpenAI models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
import tiktoken
from openai import OpenAI

from augment_adam.core.errors import (
    ResourceError, NetworkError, wrap_error, log_error, ErrorCategory
)
from augment_adam.models.model_interface import ModelInterface

logger = logging.getLogger(__name__)


class OpenAIModel(ModelInterface):
    """OpenAI Model implementation.
    
    This class provides an implementation of the ModelInterface for OpenAI models.
    
    Attributes:
        model_name: The name of the OpenAI model to use
        client: The OpenAI client
        api_key: The OpenAI API key
        organization: The OpenAI organization ID
        encoding: The tokenizer encoding
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs
    ):
        """Initialize the OpenAI Model.
        
        Args:
            model_name: The name of the OpenAI model to use
            api_key: The OpenAI API key (if None, use environment variable)
            organization: The OpenAI organization ID (if None, use environment variable)
            **kwargs: Additional parameters for the OpenAI client
        """
        try:
            self.model_name = model_name
            
            # Get API key from environment variable if not provided
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ResourceError(
                    message="OpenAI API key not provided",
                    details={"model_name": model_name}
                )
            
            # Get organization from environment variable if not provided
            self.organization = organization or os.environ.get("OPENAI_ORGANIZATION")
            
            # Initialize OpenAI client
            self.client = OpenAI(
                api_key=self.api_key,
                organization=self.organization
            )
            
            # Initialize tokenizer
            try:
                self.encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                # Fall back to cl100k_base for newer models
                self.encoding = tiktoken.get_encoding("cl100k_base")
            
            logger.info(f"Initialized OpenAI Model: {model_name}")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to initialize OpenAI Model",
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
            # Create messages from prompt
            messages = [{"role": "user", "content": prompt}]
            
            # Generate completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                **kwargs
            )
            
            # Extract generated text
            generated_text = response.choices[0].message.content
            
            logger.info(f"Generated {len(generated_text)} characters with {self.model_name}")
            return generated_text
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate text with OpenAI Model",
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
            # Create messages from prompt
            messages = [{"role": "user", "content": prompt}]
            
            # Generate streaming completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                stream=True,
                **kwargs
            )
            
            # Yield chunks of generated text
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to stream text with OpenAI Model",
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
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to count tokens with OpenAI Model",
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
        try:
            # Use the embeddings API
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            
            # Extract embedding
            embedding = response.data[0].embedding
            
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to get embedding with OpenAI Model",
                category=ErrorCategory.NETWORK,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            
            # Return a zero vector as fallback
            return [0.0] * 1536  # Default embedding size for OpenAI
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.
        
        Returns:
            A dictionary containing model information
        """
        return {
            "name": self.model_name,
            "provider": "OpenAI",
            "type": "chat",
            "max_tokens": 4096 if "gpt-3.5" in self.model_name else 8192,
            "embedding_dimensions": 1536
        }
