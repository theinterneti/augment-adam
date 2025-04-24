"""Memory systems for the Dukat assistant.

This package contains the memory systems for the Dukat assistant,
including working memory, episodic memory, semantic memory, and procedural memory.

The memory systems are implemented using both ChromaDB and FAISS for vector storage.

Version: 0.1.0
Created: 2025-04-22
Updated: 2025-04-24
"""

# Import memory classes for easy access
from dukat.memory.working import WorkingMemory, Message
from dukat.memory.episodic import EpisodicMemory, Episode
from dukat.memory.semantic import SemanticMemory, Concept

# Import FAISS-based memory implementations
from dukat.memory.faiss_memory import FAISSMemory, get_faiss_memory
from dukat.memory.faiss_episodic import FAISSEpisodicMemory, Episode as FAISSEpisode
from dukat.memory.faiss_semantic import FAISSSemanticMemory, Concept as FAISSConcept
