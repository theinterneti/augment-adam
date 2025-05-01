"""Agent Interface for the AI Agent.

This module defines the core interface for AI agents.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class AgentInterface(ABC):
    """Interface for AI agents.
    
    This interface defines the core methods that all agents must implement.
    """
    
    @abstractmethod
    def process(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input and generate a response.
        
        Args:
            input_text: The input text to process
            context: Additional context for processing
            
        Returns:
            A dictionary containing the response and additional information
        """
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        constraints: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> str:
        """Generate text based on a prompt.
        
        Args:
            prompt: The prompt to generate from
            constraints: Constraints for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text
        """
        pass
    
    @abstractmethod
    def remember(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store information in memory.
        
        Args:
            text: The text to remember
            metadata: Additional metadata for the memory
            
        Returns:
            The ID of the stored memory
        """
        pass
    
    @abstractmethod
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve information from memory.
        
        Args:
            query: The query to retrieve information for
            n_results: Maximum number of results to retrieve
            filter_metadata: Filter to apply to the metadata
            
        Returns:
            A list of retrieved memories
        """
        pass
    
    @abstractmethod
    def reason(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform reasoning on a query.
        
        Args:
            query: The query to reason about
            context: Additional context for reasoning
            
        Returns:
            The reasoning results
        """
        pass
