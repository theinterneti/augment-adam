"""Memory module for the Augment Adam assistant.

This module provides memory systems for the Augment Adam assistant,
allowing it to store and retrieve information efficiently.

Available memory systems:
- FAISS memory: Efficient vector storage and retrieval
- Neo4j memory: Graph-based vector storage and retrieval
- Episodic memory: Time-based memory for sequential information
- Semantic memory: Concept-based memory for understanding
- Working memory: Short-term memory for active processing

Version: 0.1.0
Created: 2025-04-25
"""

from augment_adam.memory.base import BaseMemory
from augment_adam.memory.episodic import EpisodicMemory
from augment_adam.memory.faiss_episodic import FAISSEpisodicMemory
from augment_adam.memory.faiss_memory import FAISSMemory
from augment_adam.memory.faiss_semantic import FAISSSemanticMemory
from augment_adam.memory.memory_factory import create_memory, get_default_memory
from augment_adam.memory.memory_interface import MemoryInterface
from augment_adam.memory.neo4j_memory import Neo4jMemory
from augment_adam.memory.semantic import SemanticMemory
from augment_adam.memory.working import WorkingMemory

__all__ = [
    "BaseMemory",
    "EpisodicMemory",
    "FAISSEpisodicMemory",
    "FAISSMemory",
    "FAISSSemanticMemory",
    "MemoryInterface",
    "Neo4jMemory",
    "SemanticMemory",
    "WorkingMemory",
    "create_memory",
    "get_default_memory",
]