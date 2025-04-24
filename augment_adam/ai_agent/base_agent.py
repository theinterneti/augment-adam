"""Base Agent for the AI Agent.

This module provides a base implementation of the Agent interface.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import numpy as np

from augment_adam.core.errors import (
    ResourceError, ValidationError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine import get_context_manager
from augment_adam.memory import create_memory, get_default_memory
from augment_adam.ai_agent.agent_interface import AgentInterface
from augment_adam.ai_agent.memory_integration.memory_manager import MemoryManager
from augment_adam.ai_agent.reasoning.chain_of_thought import ChainOfThought

# Sequential Monte Carlo imports
from augment_adam.ai_agent.smc.particle import Particle
from augment_adam.ai_agent.smc.potential import Potential, GrammarPotential, SemanticPotential
from augment_adam.ai_agent.smc.sampler import SequentialMonteCarlo

logger = logging.getLogger(__name__)


class BaseAgent(AgentInterface):
    """Base implementation of the Agent interface.
    
    This class provides a base implementation of the Agent interface with
    Sequential Monte Carlo for controlled generation.
    
    Attributes:
        name: The name of the agent
        description: A description of the agent
        context_manager: The context manager for the agent
        memory_manager: The memory manager for the agent
        reasoning_engine: The reasoning engine for the agent
        smc_sampler: The Sequential Monte Carlo sampler for controlled generation
    """
    
    def __init__(
        self,
        name: str = "Base Agent",
        description: str = "A base AI agent",
        memory_type: str = None,
        context_window_size: int = 4096,
        potentials: Optional[List[Potential]] = None,
        num_particles: int = 100
    ):
        """Initialize the Base Agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent
            memory_type: The type of memory to use (if None, use default)
            context_window_size: The size of the context window
            potentials: List of potential functions for controlled generation
            num_particles: Number of particles for SMC sampling
        """
        self.name = name
        self.description = description
        
        # Initialize context manager
        self.context_manager = get_context_manager()
        
        # Create a context window for this agent
        self.context_window = self.context_manager.create_context_window(
            name=f"{name}_window",
            max_tokens=context_window_size
        )
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(memory_type=memory_type)
        
        # Initialize reasoning engine
        self.reasoning_engine = ChainOfThought()
        
        # Initialize SMC sampler with potentials
        self.potentials = potentials or []
        self.smc_sampler = SequentialMonteCarlo(
            num_particles=num_particles,
            potentials=self.potentials
        )
        
        logger.info(f"Initialized {name} agent")
    
    def add_potential(self, potential: Potential) -> None:
        """Add a potential function for controlled generation.
        
        Args:
            potential: The potential function to add
        """
        self.potentials.append(potential)
        self.smc_sampler.update_potentials(self.potentials)
        logger.info(f"Added potential: {potential.__class__.__name__}")
    
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
            # Retrieve relevant context
            context_items = self.context_manager.retrieve(
                query=input_text,
                sources=["memory", "web", "document", "code"],
                max_items=10
            )
            
            # Compose context
            window = self.context_manager.compose_context(
                query=input_text,
                items=context_items,
                composer_name="default",
                window_name=f"{self.name}_window"
            )
            
            # Optimize context
            window = self.context_manager.optimize_context(
                window=window,
                optimizer_name="default"
            )
            
            # Create prompt
            prompt = self.context_manager.create_prompt(
                query=input_text,
                window=window,
                prompt_type="default"
            )
            
            # Generate response using SMC
            response = self.generate(
                prompt=prompt,
                constraints=context.get("constraints") if context else None
            )
            
            # Remember the interaction
            memory_id = self.remember(
                text=f"User: {input_text}\nAssistant: {response}",
                metadata={
                    "type": "conversation",
                    "input": input_text,
                    "response": response
                }
            )
            
            return {
                "response": response,
                "memory_id": memory_id,
                "context_items": len(context_items)
            }
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to process input",
                category=ErrorCategory.RESOURCE,
                details={"input_length": len(input_text) if input_text else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return {
                "response": "I'm sorry, I encountered an error while processing your request.",
                "error": str(error)
            }
    
    def generate(
        self,
        prompt: str,
        constraints: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> str:
        """Generate text based on a prompt using Sequential Monte Carlo.
        
        Args:
            prompt: The prompt to generate from
            constraints: Constraints for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text
        """
        try:
            # Apply constraints if provided
            if constraints:
                # Add grammar constraint if specified
                if "grammar" in constraints:
                    grammar = constraints["grammar"]
                    grammar_potential = GrammarPotential(grammar)
                    self.add_potential(grammar_potential)
                
                # Add semantic constraint if specified
                if "semantic" in constraints:
                    semantic_fn = constraints["semantic"]
                    semantic_potential = SemanticPotential(semantic_fn)
                    self.add_potential(semantic_potential)
            
            # Generate using SMC
            result = self.smc_sampler.sample(
                prompt=prompt,
                max_tokens=max_tokens
            )
            
            logger.info(f"Generated response with {len(result)} characters")
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate response",
                category=ErrorCategory.RESOURCE,
                details={"prompt_length": len(prompt) if prompt else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return "I'm sorry, I encountered an error while generating a response."
    
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
        try:
            memory_id = self.memory_manager.add(
                text=text,
                metadata=metadata or {}
            )
            
            logger.info(f"Stored memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to store memory",
                category=ErrorCategory.RESOURCE,
                details={"text_length": len(text) if text else 0},
            )
            log_error(error, logger=logger)
            return ""
    
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
        try:
            results = self.memory_manager.retrieve(
                query=query,
                n_results=n_results,
                filter_metadata=filter_metadata
            )
            
            # Convert to list of dictionaries
            memories = []
            for memory, similarity in results:
                memory_dict = dict(memory)
                memory_dict["similarity"] = similarity
                memories.append(memory_dict)
            
            logger.info(f"Retrieved {len(memories)} memories for query: {query}")
            return memories
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to retrieve memories",
                category=ErrorCategory.RESOURCE,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return []
    
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
        try:
            # Retrieve relevant context if not provided
            if not context or "context_items" not in context:
                context_items = self.context_manager.retrieve(
                    query=query,
                    sources=["memory", "web", "document", "code"],
                    max_items=10
                )
                
                # Compose context
                window = self.context_manager.compose_context(
                    query=query,
                    items=context_items,
                    composer_name="default",
                    window_name=f"{self.name}_window"
                )
                
                # Get context content
                context_content = window.get_content()
            else:
                context_content = context.get("context_items", "")
            
            # Perform reasoning
            reasoning_result = self.reasoning_engine.reason(
                query=query,
                context=context_content
            )
            
            logger.info(f"Performed reasoning for query: {query}")
            return reasoning_result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to perform reasoning",
                category=ErrorCategory.RESOURCE,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return {
                "conclusion": "Unable to perform reasoning due to an error.",
                "error": str(error)
            }
