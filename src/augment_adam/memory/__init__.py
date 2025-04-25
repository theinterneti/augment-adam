"""
Advanced memory system for AI agents.

This module provides advanced memory systems including vector-based, graph-based,
episodic, semantic, and working memory for AI agents.

TODO(Issue #6): Add memory persistence support
TODO(Issue #6): Implement memory validation against a schema
TODO(Issue #6): Add memory analytics to track usage and performance
"""

from augment_adam.memory.core.base import (
    Memory,
    MemoryItem,
    MemoryType,
    MemoryManager,
    get_memory_manager,
)

from augment_adam.memory.vector.base import (
    VectorMemory,
)
from augment_adam.memory.vector.faiss import FAISSMemory
from augment_adam.memory.vector.chroma import ChromaMemory

from augment_adam.memory.graph.base import (
    GraphMemory,
)
from augment_adam.memory.graph.neo4j import Neo4jMemory
from augment_adam.memory.graph.networkx import NetworkXMemory

from augment_adam.memory.episodic.base import (
    EpisodicMemory,
    Episode,
    Event,
)

from augment_adam.memory.semantic.base import (
    SemanticMemory,
    Concept,
    Relation,
)

from augment_adam.memory.working.base import (
    WorkingMemory,
    WorkingMemoryItem,
)

__all__ = [
    # Core
    "Memory",
    "MemoryItem",
    "MemoryType",
    "MemoryManager",
    "get_memory_manager",

    # Vector
    "VectorMemory",
    "FAISSMemory",
    "ChromaMemory",

    # Graph
    "GraphMemory",
    "Neo4jMemory",
    "NetworkXMemory",

    # Episodic
    "EpisodicMemory",
    "Episode",
    "Event",

    # Semantic
    "SemanticMemory",
    "Concept",
    "Relation",

    # Working
    "WorkingMemory",
    "WorkingMemoryItem",
]