"""Conversational Agent for the AI Agent.

This module provides a conversational agent.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.smc.potential import Potential, RegexPotential

logger = logging.getLogger(__name__)


class ConversationalAgent(BaseAgent):
    """Conversational Agent for the AI Agent.
    
    This class provides a conversational agent.
    
    Attributes:
        conversation_history: The conversation history
        max_history_length: Maximum number of turns in the history
    """
    
    def __init__(
        self,
        name: str = "Conversational Agent",
        description: str = "A conversational AI agent",
        memory_type: str = None,
        context_window_size: int = 4096,
        potentials: Optional[List[Potential]] = None,
        num_particles: int = 100,
        max_history_length: int = 10
    ):
        """Initialize the Conversational Agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent
            memory_type: The type of memory to use (if None, use default)
            context_window_size: The size of the context window
            potentials: List of potential functions for controlled generation
            num_particles: Number of particles for SMC sampling
            max_history_length: Maximum number of turns in the history
        """
        # Add conversation-specific potentials
        if potentials is None:
            potentials = []
        
        # Add a regex potential for proper sentence endings
        sentence_ending_potential = RegexPotential(
            pattern=r".*[.!?]$",
            name="sentence_ending_potential"
        )
        potentials.append(sentence_ending_potential)
        
        # Initialize base agent
        super().__init__(
            name=name,
            description=description,
            memory_type=memory_type,
            context_window_size=context_window_size,
            potentials=potentials,
            num_particles=num_particles
        )
        
        # Initialize conversation history
        self.conversation_history = []
        self.max_history_length = max_history_length
        
        logger.info(f"Initialized {name} with {max_history_length} max history length")
    
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
        try:
            # Add input to conversation history
            self.conversation_history.append({"role": "user", "content": input_text})
            
            # Trim history if needed
            if len(self.conversation_history) > self.max_history_length * 2:
                self.conversation_history = self.conversation_history[-self.max_history_length * 2:]
            
            # Format conversation history for context
            history_text = self._format_conversation_history()
            
            # Create context with conversation history
            if context is None:
                context = {}
            context["conversation_history"] = history_text
            
            # Process with base agent
            result = super().process(input_text, context)
            
            # Add response to conversation history
            self.conversation_history.append({"role": "assistant", "content": result["response"]})
            
            # Add conversation history to result
            result["conversation_history"] = self.conversation_history
            
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to process conversation",
                category=ErrorCategory.RESOURCE,
                details={"input_length": len(input_text) if input_text else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            response = "I'm sorry, I encountered an error while processing your request."
            
            # Add response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "response": response,
                "error": str(error),
                "conversation_history": self.conversation_history
            }
    
    def _format_conversation_history(self) -> str:
        """Format conversation history as text.
        
        Returns:
            The formatted conversation history
        """
        formatted = "Conversation History:\n\n"
        
        for turn in self.conversation_history:
            role = turn["role"].capitalize()
            content = turn["content"]
            formatted += f"{role}: {content}\n\n"
        
        return formatted
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Cleared conversation history")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history.
        
        Returns:
            The conversation history
        """
        return self.conversation_history
