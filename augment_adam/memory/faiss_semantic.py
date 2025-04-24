"""FAISS-based semantic memory for the Dukat assistant.

This module provides a FAISS-based implementation of semantic memory
for storing and retrieving concepts and knowledge.

Version: 0.1.0
Created: 2025-04-24
"""

import os
import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from augment_adam.core.settings import get_settings
from augment_adam.core.errors import (
    ResourceError, DatabaseError, wrap_error, log_error, ErrorCategory
)
from augment_adam.memory.faiss_memory import FAISSMemory

logger = logging.getLogger(__name__)


class Concept:
    """A concept in semantic memory.

    This class represents a concept in semantic memory, which
    is a piece of knowledge or information.

    Attributes:
        id: The unique identifier for the concept.
        name: The name of the concept.
        description: A short description of the concept.
        content: The detailed content of the concept.
        timestamp: The timestamp when the concept was created.
        metadata: Additional metadata for the concept.
    """

    def __init__(
        self,
        name: str,
        description: str,
        content: str,
        timestamp: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        concept_id: Optional[str] = None,
    ):
        """Initialize a concept.

        Args:
            name: The name of the concept.
            description: A short description of the concept.
            content: The detailed content of the concept.
            timestamp: The timestamp when the concept was created.
            metadata: Additional metadata for the concept.
            concept_id: The unique identifier for the concept.
        """
        self.id = concept_id or f"con_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.content = content
        self.timestamp = timestamp or int(time.time())
        self.metadata = metadata or {}

        logger.debug(f"Created concept {self.id}: {self.name}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the concept to a dictionary.

        Returns:
            A dictionary representation of the concept.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Concept":
        """Create a concept from a dictionary.

        Args:
            data: A dictionary representation of the concept.

        Returns:
            A new Concept instance.
        """
        return cls(
            name=data["name"],
            description=data["description"],
            content=data["content"],
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
            concept_id=data.get("id"),
        )

    def __str__(self) -> str:
        """Get a string representation of the concept.

        Returns:
            A string representation of the concept.
        """
        return f"{self.name} ({self.id}): {self.description}"


class FAISSSemanticMemory:
    """FAISS-based semantic memory for the Dukat assistant.

    This class manages the storage and retrieval of concepts using FAISS,
    which are pieces of knowledge or information.

    Attributes:
        persist_dir: Directory to persist memory data.
        memory: FAISS memory instance for vector storage.
        embedding_model: SentenceTransformer model for creating embeddings.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "augment_adam_concepts",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """Initialize the semantic memory.

        Args:
            persist_dir: Directory to persist memory data.
            collection_name: Name of the collection.
            embedding_model: Name of the SentenceTransformer model to use for embeddings.
        """
        self.persist_dir = persist_dir or os.path.expanduser(
            "~/.augment_adam/memory/faiss_semantic")

        # Create directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)

        logger.info(
            f"Initializing FAISS semantic memory with persist_dir: {self.persist_dir}")

        # Initialize FAISS memory
        self.memory = FAISSMemory(
            persist_dir=self.persist_dir,
            collection_name=collection_name,
            embedding_model=embedding_model,
        )

        # Store collection name for later use
        self.collection_name = collection_name

    def add_concept(
        self,
        name: str,
        description: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Concept:
        """Add a concept to the memory.

        Args:
            name: The name of the concept.
            description: A short description of the concept.
            content: The detailed content of the concept.
            metadata: Additional metadata for the concept.

        Returns:
            The added concept.

        Raises:
            ValueError: If the concept name, description, or content is empty.
        """
        if not name or not description or not content:
            logger.warning("Attempted to add concept with empty name, description, or content")
            raise ValueError("Concept name, description, and content cannot be empty")

        # Create the concept
        concept = Concept(
            name=name,
            description=description,
            content=content,
            metadata=metadata or {},
        )

        # Prepare text for embedding (combine name, description, and content)
        text = f"{name}\n{description}\n{content}"

        # Prepare metadata for storage
        storage_metadata = {
            **concept.metadata,
            "name": concept.name,
            "description": concept.description,
            "content": concept.content,
            "timestamp": concept.timestamp,
        }

        # Add to FAISS memory
        memory_id = self.memory.add(
            text=text,
            metadata=storage_metadata,
            collection_name=self.collection_name,
            id_prefix=concept.id,
        )

        if not memory_id:
            logger.error(f"Failed to add concept {concept.id} to memory")
            # Use the original ID since the add failed
            return concept

        # Update the concept ID to match the memory ID
        concept.id = memory_id

        logger.info(f"Added concept {concept.id} to memory")
        return concept

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by ID.

        Args:
            concept_id: The ID of the concept to get.

        Returns:
            The concept, or None if not found.
        """
        # Get from FAISS memory
        memory = self.memory.get_by_id(
            memory_id=concept_id,
            collection_name=self.collection_name,
        )

        if not memory:
            logger.warning(f"Concept {concept_id} not found")
            return None

        # Extract concept data
        name = memory.get("name", "Unknown Concept")
        description = memory.get("description", "")
        content = memory.get("content", "")
        timestamp = memory.get("timestamp", int(time.time()))

        # Remove known fields from metadata
        metadata = {k: v for k, v in memory.items() if k not in [
            "text", "name", "description", "content", "timestamp"]}

        # Create and return the concept
        concept = Concept(
            name=name,
            description=description,
            content=content,
            timestamp=timestamp,
            metadata=metadata,
            concept_id=concept_id,
        )

        return concept

    def get_concept_by_name(
        self,
        name: str,
        exact_match: bool = False,
    ) -> Optional[Concept]:
        """Get a concept by name.

        Args:
            name: The name of the concept to get.
            exact_match: Whether to require an exact match.

        Returns:
            The concept, or None if not found.
        """
        try:
            # Get all memory IDs
            memory_ids = self.memory.ids.get(self.collection_name, [])
            
            # Get metadata for each ID
            for memory_id in memory_ids:
                memory = self.memory.get_by_id(
                    memory_id=memory_id,
                    collection_name=self.collection_name,
                )
                
                if not memory:
                    continue
                
                # Check name
                memory_name = memory.get("name", "")
                if exact_match:
                    if memory_name != name:
                        continue
                else:
                    if name.lower() not in memory_name.lower():
                        continue
                
                # Extract concept data
                description = memory.get("description", "")
                content = memory.get("content", "")
                timestamp = memory.get("timestamp", int(time.time()))
                
                # Remove known fields from metadata
                metadata = {k: v for k, v in memory.items() if k not in [
                    "text", "name", "description", "content", "timestamp"]}
                
                # Create and return the concept
                concept = Concept(
                    name=memory_name,
                    description=description,
                    content=content,
                    timestamp=timestamp,
                    metadata=metadata,
                    concept_id=memory_id,
                )
                
                return concept
            
            # No matching concept found
            return None
        except Exception as e:
            # Handle errors
            error = wrap_error(
                e,
                message=f"Failed to get concept by name: {name}",
                category=ErrorCategory.DATABASE,
                details={
                    "name": name,
                    "exact_match": exact_match,
                },
            )
            log_error(error, logger=logger)
            return None

    def search_concepts(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Concept, float]]:
        """Search for concepts based on a query.

        Args:
            query: The search query.
            n_results: Maximum number of results to return.
            filter_metadata: Filter to apply to the metadata.

        Returns:
            A list of tuples containing the concept and its similarity score.
        """
        if not query:
            logger.warning("Attempted to search with empty query")
            return []

        # Search in FAISS memory
        results = self.memory.retrieve(
            query=query,
            n_results=n_results,
            filter_metadata=filter_metadata,
            collection_name=self.collection_name,
        )

        # Convert to concepts
        concepts = []
        for memory, score in results:
            # Extract concept data
            name = memory.get("name", "Unknown Concept")
            description = memory.get("description", "")
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", int(time.time()))
            concept_id = memory.get("id", f"con_{uuid.uuid4().hex[:8]}")

            # Remove known fields from metadata
            metadata = {k: v for k, v in memory.items() if k not in [
                "text", "name", "description", "content", "timestamp", "id"]}

            # Create the concept
            concept = Concept(
                name=name,
                description=description,
                content=content,
                timestamp=timestamp,
                metadata=metadata,
                concept_id=concept_id,
            )

            concepts.append((concept, score))

        return concepts

    def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept by ID.

        Args:
            concept_id: The ID of the concept to delete.

        Returns:
            True if the concept was deleted, False otherwise.
        """
        # Delete from FAISS memory
        result = self.memory.delete(
            memory_id=concept_id,
            collection_name=self.collection_name,
        )

        if result:
            logger.info(f"Deleted concept {concept_id}")
        else:
            logger.warning(f"Failed to delete concept {concept_id}")

        return result

    def clear(self) -> bool:
        """Clear all concepts from memory.

        Returns:
            True if the memory was cleared, False otherwise.
        """
        # Clear FAISS memory
        result = self.memory.clear(
            collection_name=self.collection_name,
        )

        if result:
            logger.info("Cleared all concepts from memory")
        else:
            logger.warning("Failed to clear concepts from memory")

        return result
