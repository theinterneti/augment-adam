"""Model Interface for language models.

This module defines the core interface for language models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Generator

logger = logging.getLogger(__name__)


class ModelInterface(ABC):
    """Interface for language models.
    
    This interface defines the core methods that all language models must implement.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Get the number of tokens in a text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The number of tokens
        """
        pass
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Get the embedding for a text.
        
        Args:
            text: The text to get an embedding for
            
        Returns:
            The embedding as a list of floats
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.
        
        Returns:
            A dictionary containing model information
        """
        pass
