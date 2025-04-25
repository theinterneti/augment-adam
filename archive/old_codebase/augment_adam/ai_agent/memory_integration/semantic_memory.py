"""Semantic Memory Implementation.

This module provides the semantic memory for agents.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Concept:
    """Concept in semantic memory.

    Attributes:
        id: Unique identifier for the concept
        name: Name of the concept
        description: Description of the concept
        content: Detailed content of the concept
        timestamp: Timestamp when the concept was created
        updated_at: Timestamp when the concept was last updated
        metadata: Additional metadata for the concept
    """

    name: str
    description: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"con_{uuid.uuid4().hex[:12]}")
    timestamp: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def __str__(self) -> str:
        """Get a string representation of the concept.

        Returns:
            String representation of the concept
        """
        return f"{self.name} ({self.id}): {self.description[:50]}..."


class SemanticMemory:
    """Semantic memory for agents.

    This class manages the storage and retrieval of concepts,
    which are structured knowledge representations.

    Attributes:
        name: Name of the semantic memory
        max_size: Maximum size of the semantic memory
        concepts: List of concepts in the memory
    """

    def __init__(self, name: str, max_size: int = 500):
        """Initialize the semantic memory.

        Args:
            name: Name of the semantic memory
            max_size: Maximum size of the semantic memory
        """
        self.name = name
        self.max_size = max_size
        self.concepts = []

        logger.info(f"Initialized Semantic Memory '{name}' with max size {max_size}")

    def add_concept(
        self,
        name: str,
        description: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Concept:
        """Add a concept to the memory.

        Args:
            name: Name of the concept
            description: Description of the concept
            content: Detailed content of the concept
            metadata: Additional metadata for the concept

        Returns:
            The added concept

        Raises:
            ValueError: If the concept name, description, or content is empty
        """
        if not name or not description or not content:
            logger.warning(
                "Attempted to add concept with empty name, description, or content"
            )
            raise ValueError("Concept name, description, and content cannot be empty")

        # Check if concept with same name already exists
        for i, concept in enumerate(self.concepts):
            if concept.name.lower() == name.lower():
                # Update existing concept
                concept.description = description
                concept.content = content
                concept.updated_at = time.time()

                if metadata:
                    concept.metadata.update(metadata)

                logger.info(f"Updated concept: {concept.id}")
                return concept

        # Create the concept
        concept = Concept(
            name=name, description=description, content=content, metadata=metadata or {}
        )

        # Add to concepts
        self.concepts.append(concept)

        # Trim if necessary
        if len(self.concepts) > self.max_size:
            self.concepts = self.concepts[-self.max_size :]

        logger.info(f"Added concept with ID: {concept.id}")
        return concept

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by ID.

        Args:
            concept_id: ID of the concept to get

        Returns:
            The concept or None if not found
        """
        for concept in self.concepts:
            if concept.id == concept_id:
                return concept

        logger.warning(f"Concept with ID '{concept_id}' not found")
        return None

    def get_concept_by_name(self, name: str) -> Optional[Concept]:
        """Get a concept by name.

        Args:
            name: Name of the concept to get

        Returns:
            The concept or None if not found
        """
        for concept in self.concepts:
            if concept.name.lower() == name.lower():
                return concept

        logger.warning(f"Concept with name '{name}' not found")
        return None

    def search_concepts(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Concept, float]]:
        """Search for concepts by content similarity.

        Args:
            query: Query to search for
            n_results: Maximum number of results to return
            filter_metadata: Metadata to filter by

        Returns:
            List of tuples containing concepts and their similarity scores
        """
        # Simple keyword matching for now
        # In a real implementation, this would use vector similarity search
        results = []

        for concept in self.concepts:
            # Check metadata filter if provided
            if filter_metadata:
                match = True
                for key, value in filter_metadata.items():
                    if key not in concept.metadata or concept.metadata[key] != value:
                        match = False
                        break

                if not match:
                    continue

            # Calculate simple similarity score
            query_words = set(query.lower().split())

            # Combine name, description, and content for matching
            concept_text = f"{concept.name} {concept.description} {concept.content}"
            concept_words = set(concept_text.lower().split())

            if not query_words:
                continue

            # Jaccard similarity
            intersection = len(query_words.intersection(concept_words))
            union = len(query_words.union(concept_words))

            if union == 0:
                similarity = 0.0
            else:
                similarity = intersection / union

            # Boost score if query appears in name or description
            if any(word in concept.name.lower() for word in query.lower().split()):
                similarity += 0.3

            if any(
                word in concept.description.lower() for word in query.lower().split()
            ):
                similarity += 0.2

            if similarity > 0:
                results.append((concept, min(similarity, 1.0)))  # Cap at 1.0

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top n results
        return results[:n_results]

    def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept by ID.

        Args:
            concept_id: ID of the concept to delete

        Returns:
            True if deleted, False otherwise
        """
        for i, concept in enumerate(self.concepts):
            if concept.id == concept_id:
                del self.concepts[i]
                logger.info(f"Deleted concept with ID: {concept_id}")
                return True

        logger.warning(f"Concept with ID '{concept_id}' not found for deletion")
        return False

    def clear(self) -> None:
        """Clear all concepts from the memory."""
        self.concepts = []
        logger.info(f"Cleared all concepts from semantic memory '{self.name}'")

    def get_all_concepts(self) -> List[Concept]:
        """Get all concepts in the memory.

        Returns:
            List of all concepts
        """
        return self.concepts.copy()

    def get_size(self) -> int:
        """Get the size of the semantic memory.

        Returns:
            Size of the semantic memory
        """
        return len(self.concepts)

    def get_info(self) -> Dict[str, Any]:
        """Get information about the semantic memory.

        Returns:
            Information about the semantic memory
        """
        return {
            "name": self.name,
            "max_size": self.max_size,
            "current_size": len(self.concepts),
        }
