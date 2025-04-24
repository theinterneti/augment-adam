"""Memory Integration Components for the AI Agent.

This module provides components for integrating with memory systems.

Version: 0.1.0
Created: 2025-04-27
Updated: 2025-05-01
"""

from augment_adam.ai_agent.memory_integration.memory_manager import MemoryManager
from augment_adam.ai_agent.memory_integration.context_memory import ContextMemory
from augment_adam.ai_agent.memory_integration.episodic_memory import EpisodicMemory
from augment_adam.ai_agent.memory_integration.semantic_memory import SemanticMemory
from augment_adam.ai_agent.memory_integration.memory_configuration import (
    MemoryConfiguration,
    MemoryAllocation,
    get_memory_configuration
)

__all__ = [
    "MemoryManager",
    "ContextMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "MemoryConfiguration",
    "MemoryAllocation",
    "get_memory_configuration",
]
