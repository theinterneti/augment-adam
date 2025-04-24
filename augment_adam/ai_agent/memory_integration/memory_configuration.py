"""Memory Configuration for AI Agents.

This module provides configurations for agent memory systems based on roles and models.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

from augment_adam.ai_agent.memory_integration.memory_manager import MemoryManager
from augment_adam.ai_agent.memory_integration.context_memory import ContextMemory
from augment_adam.ai_agent.memory_integration.episodic_memory import EpisodicMemory
from augment_adam.ai_agent.memory_integration.semantic_memory import SemanticMemory
from augment_adam.context_engine.context_manager import ContextWindow, get_context_manager

logger = logging.getLogger(__name__)


@dataclass
class MemoryAllocation:
    """Memory allocation configuration.
    
    Attributes:
        working_memory_size: Size of working memory (number of messages)
        episodic_memory_size: Size of episodic memory (number of episodes)
        semantic_memory_size: Size of semantic memory (number of concepts)
        context_window_size: Size of context window (in tokens)
        working_memory_token_ratio: Ratio of context window allocated to working memory
        episodic_memory_token_ratio: Ratio of context window allocated to episodic memory
        semantic_memory_token_ratio: Ratio of context window allocated to semantic memory
        procedural_memory_token_ratio: Ratio of context window allocated to procedural memory
    """
    
    working_memory_size: int = 20
    episodic_memory_size: int = 100
    semantic_memory_size: int = 500
    context_window_size: int = 8192
    working_memory_token_ratio: float = 0.5
    episodic_memory_token_ratio: float = 0.3
    semantic_memory_token_ratio: float = 0.15
    procedural_memory_token_ratio: float = 0.05


class MemoryConfiguration:
    """Memory configuration for AI agents.
    
    This class manages memory configurations for different agent roles and models.
    
    Attributes:
        role_configurations: Dictionary mapping roles to memory allocations
        model_context_windows: Dictionary mapping model names to context window sizes
    """
    
    def __init__(self):
        """Initialize the memory configuration."""
        # Default role configurations
        self.role_configurations = {
            "default": MemoryAllocation(),
            "researcher": MemoryAllocation(
                working_memory_size=15,
                episodic_memory_size=150,
                semantic_memory_size=1000,
                working_memory_token_ratio=0.3,
                episodic_memory_token_ratio=0.3,
                semantic_memory_token_ratio=0.35,
                procedural_memory_token_ratio=0.05
            ),
            "coder": MemoryAllocation(
                working_memory_size=25,
                episodic_memory_size=100,
                semantic_memory_size=300,
                working_memory_token_ratio=0.4,
                episodic_memory_token_ratio=0.2,
                semantic_memory_token_ratio=0.2,
                procedural_memory_token_ratio=0.2
            ),
            "writer": MemoryAllocation(
                working_memory_size=30,
                episodic_memory_size=200,
                semantic_memory_size=400,
                working_memory_token_ratio=0.45,
                episodic_memory_token_ratio=0.35,
                semantic_memory_token_ratio=0.15,
                procedural_memory_token_ratio=0.05
            ),
            "coordinator": MemoryAllocation(
                working_memory_size=40,
                episodic_memory_size=80,
                semantic_memory_size=200,
                working_memory_token_ratio=0.6,
                episodic_memory_token_ratio=0.2,
                semantic_memory_token_ratio=0.1,
                procedural_memory_token_ratio=0.1
            )
        }
        
        # Model context window sizes (in tokens)
        self.model_context_windows = {
            # Anthropic models
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
            
            # OpenAI models
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385,
            
            # Hugging Face models (approximate)
            "llama-2-7b": 4096,
            "llama-2-13b": 4096,
            "llama-2-70b": 4096,
            "mistral-7b": 8192,
            "mixtral-8x7b": 32768,
            
            # Ollama models (approximate)
            "llama2": 4096,
            "mistral": 8192,
            "mixtral": 32768,
            
            # Default
            "default": 4096
        }
        
        logger.info("Memory configuration initialized")
    
    def get_allocation_for_role(self, role: str) -> MemoryAllocation:
        """Get memory allocation for a specific role.
        
        Args:
            role: The role to get allocation for
            
        Returns:
            Memory allocation for the role
        """
        return self.role_configurations.get(role.lower(), self.role_configurations["default"])
    
    def get_context_window_size(self, model_name: str) -> int:
        """Get context window size for a specific model.
        
        Args:
            model_name: The model name
            
        Returns:
            Context window size in tokens
        """
        return self.model_context_windows.get(model_name, self.model_context_windows["default"])
    
    def configure_memory_for_agent(
        self,
        agent_name: str,
        role: str,
        model_name: str,
        memory_manager: Optional[MemoryManager] = None
    ) -> Dict[str, Any]:
        """Configure memory for an agent.
        
        Args:
            agent_name: The name of the agent
            role: The role of the agent
            model_name: The model used by the agent
            memory_manager: Optional memory manager to use
            
        Returns:
            Dictionary with configured memory components
        """
        # Get allocation for role
        allocation = self.get_allocation_for_role(role)
        
        # Get context window size for model
        context_window_size = self.get_context_window_size(model_name)
        
        # Adjust allocation based on model's context window
        allocation.context_window_size = min(allocation.context_window_size, context_window_size)
        
        # Create memory manager if not provided
        if memory_manager is None:
            memory_manager = MemoryManager(agent_id=agent_name)
        
        # Get context manager
        context_manager = get_context_manager()
        
        # Create context window for agent
        context_window = context_manager.create_context_window(
            name=f"{agent_name}_window",
            max_tokens=allocation.context_window_size
        )
        
        # Create memory components
        working_memory = ContextMemory(
            name=f"{agent_name}_working_memory",
            max_size=allocation.working_memory_size
        )
        
        episodic_memory = EpisodicMemory(
            name=f"{agent_name}_episodic_memory",
            max_size=allocation.episodic_memory_size
        )
        
        semantic_memory = SemanticMemory(
            name=f"{agent_name}_semantic_memory",
            max_size=allocation.semantic_memory_size
        )
        
        # Calculate token budgets
        working_memory_tokens = int(allocation.context_window_size * allocation.working_memory_token_ratio)
        episodic_memory_tokens = int(allocation.context_window_size * allocation.episodic_memory_token_ratio)
        semantic_memory_tokens = int(allocation.context_window_size * allocation.semantic_memory_token_ratio)
        procedural_memory_tokens = int(allocation.context_window_size * allocation.procedural_memory_token_ratio)
        
        # Log configuration
        logger.info(f"Configured memory for agent '{agent_name}' with role '{role}' using model '{model_name}'")
        logger.info(f"Context window size: {allocation.context_window_size} tokens")
        logger.info(f"Working memory: {allocation.working_memory_size} items, {working_memory_tokens} tokens")
        logger.info(f"Episodic memory: {allocation.episodic_memory_size} episodes, {episodic_memory_tokens} tokens")
        logger.info(f"Semantic memory: {allocation.semantic_memory_size} concepts, {semantic_memory_tokens} tokens")
        logger.info(f"Procedural memory: {procedural_memory_tokens} tokens")
        
        # Return configured components
        return {
            "memory_manager": memory_manager,
            "context_window": context_window,
            "working_memory": working_memory,
            "episodic_memory": episodic_memory,
            "semantic_memory": semantic_memory,
            "allocation": allocation,
            "token_budgets": {
                "working_memory": working_memory_tokens,
                "episodic_memory": episodic_memory_tokens,
                "semantic_memory": semantic_memory_tokens,
                "procedural_memory": procedural_memory_tokens
            }
        }
    
    def register_role(self, role: str, allocation: MemoryAllocation) -> None:
        """Register a new role configuration.
        
        Args:
            role: The role name
            allocation: Memory allocation for the role
        """
        self.role_configurations[role.lower()] = allocation
        logger.info(f"Registered memory allocation for role '{role}'")
    
    def register_model(self, model_name: str, context_window_size: int) -> None:
        """Register a new model with its context window size.
        
        Args:
            model_name: The model name
            context_window_size: Context window size in tokens
        """
        self.model_context_windows[model_name] = context_window_size
        logger.info(f"Registered context window size {context_window_size} for model '{model_name}'")


# Global instance for singleton pattern
_memory_configuration = None


def get_memory_configuration() -> MemoryConfiguration:
    """Get the global memory configuration instance.
    
    Returns:
        The global memory configuration instance
    """
    global _memory_configuration
    
    if _memory_configuration is None:
        _memory_configuration = MemoryConfiguration()
    
    return _memory_configuration
