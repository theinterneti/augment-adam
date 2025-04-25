"""Memory module for the Augment Adam assistant.

This module provides memory systems for the Augment Adam assistant,
allowing it to store and retrieve information efficiently.

Available memory systems:
- FAISS memory: Efficient vector storage and retrieval
- Neo4j memory: Graph-based vector storage and retrieval

Version: 0.1.0
Created: 2025-04-25
"""

from augment_adam.memory.memory_interface import MemoryInterface
from augment_adam.memory.memory_factory import create_memory, get_default_memory

__all__ = [
    "MemoryInterface",
    "create_memory",
    "get_default_memory",
]