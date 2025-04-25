"""Semantic memory for the Augment Adam assistant.

This module provides semantic memory functionality."""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from datetime import datetime
import time
import os
import json
from pathlib import Path
import uuid

import chromadb
from chromadb.config import Settings
import numpy as np

# Ensure compatibility with NumPy 2.0+
if not hasattr(np, 'float_'):
    np.float_ = np.float64

logger = logging.getLogger(__name__)


class Concept:
    """A concept in the assistant's semantic memory.

    This class represents a concept, which is a unit of knowledge
    or information about a specific topic.

    Attributes:
        id: The unique identifier for the concept.
        name: The name of the concept.
        description: A description of the concept.
        content: The detailed content of the concept.
        timestamp: The timestamp when the concept was created.
        updated_at: The timestamp when the concept was last updated.
        metadata: Additional metadata for the concept.
    """

    def __init__(
        self,
        name: str,
        description: str,
        content: str,
        timestamp: Optional[int] = None,
        updated_at: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        concept_id: Optional[str] = None,
    ):
        """Initialize a concept.

        Args:
            name: The name of the concept.
            description: A description of the concept.
            content: The detailed content of the concept.
            timestamp: The timestamp when the concept was created.
            updated_at: The timestamp when the concept was last updated.
            metadata: Additional metadata for the concept.
            concept_id: The unique identifier for the concept.
        """
        self.id = concept_id or f"con_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.content = content
        self.timestamp = timestamp or int(time.time())
        self.updated_at = updated_at or self.timestamp
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
            "updated_at": self.updated_at,
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
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {}),
            concept_id=data.get("id"),
        )

    def __str__(self) -> str:
        """Get a string representation of the concept.

        Returns:
            A string representation of the concept.
        """
        return f"{self.name} ({self.id}): {self.description}"


class SemanticMemory:
    """Semantic memory for the Augment Adam assistant.

    This class manages the storage and retrieval of concepts,
    which are units of knowledge or information.

    Attributes:
        persist_dir: Directory to persist memory data.
        client: ChromaDB client for vector storage.
        collection: ChromaDB collection for concepts.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "augment_adam_concepts",
    ):
        """Initialize the semantic memory.

        Args:
            persist_dir: Directory to persist memory data.
            collection_name: Name of the collection.
        """
        self.persist_dir = persist_dir or os.path.expanduser(
            "~/.augment_adam/memory/semantic")

        # Create directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)

        logger.info(
            f"Initializing semantic memory with persist_dir: {self.persist_dir}")

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Initialize collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Semantic memory collection for Augment Adam"}
        )

        logger.info(f"Initialized collection: {collection_name}")

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
            description: A description of the concept.
            content: The detailed content of the concept.
            metadata: Additional metadata for the concept.

        Returns:
            The added concept.
        """
        if not name or not description or not content:
            logger.warning(
                "Attempted to add concept with empty name, description, or content")
            raise ValueError(
                "Concept name, description, and content cannot be empty")

        # Create the concept
        concept = Concept(
            name=name,
            description=description,
            content=content,
            metadata=metadata or {},
        )

        try:
            # Add the concept to the collection
            self.collection.add(
                documents=[concept.content],
                metadatas=[{
                    "name": concept.name,
                    "description": concept.description,
                    "timestamp": concept.timestamp,
                    "updated_at": concept.updated_at,
                    **concept.metadata,
                }],
                ids=[concept.id],
            )

            logger.info(f"Added concept: {concept.id}")
            return concept

        except Exception as e:
            logger.error(f"Error adding concept: {str(e)}")
            raise RuntimeError(f"Error adding concept: {str(e)}")

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by ID.

        Args:
            concept_id: The ID of the concept to retrieve.

        Returns:
            The concept, or None if not found.
        """
        try:
            # Get the concept from the collection
            result = self.collection.get(
                ids=[concept_id],
                include=["documents", "metadatas"],
            )

            if not result["ids"]:
                logger.warning(f"Concept {concept_id} not found")
                return None

            # Create a concept from the result
            metadata = result["metadatas"][0]
            name = metadata.pop("name", "Unknown")
            description = metadata.pop("description", "")
            timestamp = metadata.pop("timestamp", None)
            updated_at = metadata.pop("updated_at", None)

            concept = Concept(
                name=name,
                description=description,
                content=result["documents"][0],
                timestamp=timestamp,
                updated_at=updated_at,
                metadata=metadata,
                concept_id=result["ids"][0],
            )

            logger.info(f"Retrieved concept: {concept.id}")
            return concept

        except Exception as e:
            logger.error(f"Error retrieving concept: {str(e)}")
            return None

    def search_concepts(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Concept, float]]:
        """Search for concepts by content.

        Args:
            query: The query to search for.
            n_results: Maximum number of results to return.
            filter_metadata: Metadata filters to apply.

        Returns:
            A list of concepts with their similarity scores.
        """
        try:
            # Search the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"],
            )

            # Create concepts from the results
            concepts = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                name = metadata.pop("name", "Unknown")
                description = metadata.pop("description", "")
                timestamp = metadata.pop("timestamp", None)
                updated_at = metadata.pop("updated_at", None)

                concept = Concept(
                    name=name,
                    description=description,
                    content=doc,
                    timestamp=timestamp,
                    updated_at=updated_at,
                    metadata=metadata,
                    concept_id=results["ids"][0][i],
                )

                distance = results["distances"][0][i] if "distances" in results else 1.0
                concepts.append((concept, distance))

            logger.info(
                f"Found {len(concepts)} concepts for query: {query[:50]}...")
            return concepts

        except Exception as e:
            logger.error(f"Error searching concepts: {str(e)}")
            return []

    def get_concept_by_name(
        self,
        name: str,
        exact_match: bool = True,
    ) -> Optional[Concept]:
        """Get a concept by name.

        Args:
            name: The name of the concept to retrieve.
            exact_match: Whether to require an exact match.

        Returns:
            The concept, or None if not found.
        """
        try:
            # Search for the concept by name
            if exact_match:
                results = self.collection.get(
                    where={"name": name},
                    include=["documents", "metadatas", "ids"],
                )
            else:
                # Use a query to find similar names
                results = self.collection.query(
                    query_texts=[name],
                    n_results=1,
                    include=["documents", "metadatas", "ids"],
                )

            if not (results["ids"] and (exact_match or results["ids"][0])):
                logger.warning(f"Concept with name {name} not found")
                return None

            # Create a concept from the result
            if exact_match:
                i = 0
                metadata = results["metadatas"][i]
                name = metadata.pop("name", "Unknown")
                description = metadata.pop("description", "")
                timestamp = metadata.pop("timestamp", None)
                updated_at = metadata.pop("updated_at", None)

                concept = Concept(
                    name=name,
                    description=description,
                    content=results["documents"][i],
                    timestamp=timestamp,
                    updated_at=updated_at,
                    metadata=metadata,
                    concept_id=results["ids"][i],
                )
            else:
                metadata = results["metadatas"][0][0]
                name = metadata.pop("name", "Unknown")
                description = metadata.pop("description", "")
                timestamp = metadata.pop("timestamp", None)
                updated_at = metadata.pop("updated_at", None)

                concept = Concept(
                    name=name,
                    description=description,
                    content=results["documents"][0][0],
                    timestamp=timestamp,
                    updated_at=updated_at,
                    metadata=metadata,
                    concept_id=results["ids"][0][0],
                )

            logger.info(f"Retrieved concept by name: {concept.id}")
            return concept

        except Exception as e:
            logger.error(f"Error retrieving concept by name: {str(e)}")
            return None

    def update_concept(
        self,
        concept_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update a concept.

        Args:
            concept_id: The ID of the concept to update.
            name: The new name for the concept.
            description: The new description for the concept.
            content: The new content for the concept.
            metadata: The new metadata for the concept.

        Returns:
            True if successful, False otherwise.
        """
        # Get the current concept
        concept = self.get_concept(concept_id)
        if concept is None:
            logger.warning(f"Concept {concept_id} not found")
            return False

        # Update the concept
        if name is not None:
            concept.name = name

        if description is not None:
            concept.description = description

        if content is not None:
            concept.content = content

        if metadata is not None:
            concept.metadata.update(metadata)

        # Update the timestamp
        concept.updated_at = int(time.time())

        try:
            # Update the concept in the collection
            self.collection.update(
                documents=[concept.content],
                metadatas=[{
                    "name": concept.name,
                    "description": concept.description,
                    "timestamp": concept.timestamp,
                    "updated_at": concept.updated_at,
                    **concept.metadata,
                }],
                ids=[concept.id],
            )

            logger.info(f"Updated concept: {concept.id}")
            return True

        except Exception as e:
            logger.error(f"Error updating concept: {str(e)}")
            return False

    def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept.

        Args:
            concept_id: The ID of the concept to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Delete the concept from the collection
            self.collection.delete(
                ids=[concept_id],
            )

            logger.info(f"Deleted concept: {concept_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting concept: {str(e)}")
            return False

    def clear(self) -> bool:
        """Clear all concepts from the memory.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Delete all concepts from the collection
            self.collection.delete(
                where={},
            )

            logger.info("Cleared all concepts")
            return True

        except Exception as e:
            logger.error(f"Error clearing concepts: {str(e)}")
            return False

    def count_concepts(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count the number of concepts.

        Args:
            filter_metadata: Metadata filters to apply.

        Returns:
            The number of concepts.
        """
        try:
            # Get all concepts
            results = self.collection.get(
                where=filter_metadata,
                include=["ids"],
            )

            count = len(results["ids"])
            logger.info(f"Counted {count} concepts")
            return count

        except Exception as e:
            logger.error(f"Error counting concepts: {str(e)}")
            return 0

    def get_all_concepts(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
        sort_by: str = "name",
        ascending: bool = True,
    ) -> List[Concept]:
        """Get all concepts.

        Args:
            filter_metadata: Metadata filters to apply.
            sort_by: Field to sort by (name, timestamp, updated_at).
            ascending: Whether to sort in ascending order.

        Returns:
            A list of all concepts.
        """
        try:
            # Get all concepts
            results = self.collection.get(
                where=filter_metadata,
                include=["documents", "metadatas", "ids"],
            )

            # Create concepts from the results
            concepts = []
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                name = metadata.pop("name", "Unknown")
                description = metadata.pop("description", "")
                timestamp = metadata.pop("timestamp", None)
                updated_at = metadata.pop("updated_at", None)

                concept = Concept(
                    name=name,
                    description=description,
                    content=doc,
                    timestamp=timestamp,
                    updated_at=updated_at,
                    metadata=metadata,
                    concept_id=results["ids"][i],
                )

                concepts.append(concept)

            # Sort the concepts
            if sort_by == "name":
                concepts.sort(key=lambda c: c.name, reverse=not ascending)
            elif sort_by == "timestamp":
                concepts.sort(key=lambda c: c.timestamp, reverse=not ascending)
            elif sort_by == "updated_at":
                concepts.sort(key=lambda c: c.updated_at,
                              reverse=not ascending)

            logger.info(f"Retrieved {len(concepts)} concepts")
            return concepts

        except Exception as e:
            logger.error(f"Error retrieving all concepts: {str(e)}")
            return []

    def get_recently_updated_concepts(
        self,
        n: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Concept]:
        """Get the most recently updated concepts.

        Args:
            n: Maximum number of concepts to return.
            filter_metadata: Metadata filters to apply.

        Returns:
            A list of concepts.
        """
        # Get all concepts
        concepts = self.get_all_concepts(
            filter_metadata=filter_metadata,
            sort_by="updated_at",
            ascending=False,
        )

        # Limit the number of concepts
        return concepts[:n]

    def get_related_concepts(
        self,
        concept_id: str,
        n_results: int = 5,
    ) -> List[Tuple[Concept, float]]:
        """Get concepts related to a specific concept.

        Args:
            concept_id: The ID of the concept to find related concepts for.
            n_results: Maximum number of results to return.

        Returns:
            A list of related concepts with their similarity scores.
        """
        # Get the concept
        concept = self.get_concept(concept_id)
        if concept is None:
            logger.warning(f"Concept {concept_id} not found")
            return []

        # Search for related concepts
        results = self.search_concepts(
            query=concept.content,
            n_results=n_results + 1,  # Add 1 to account for the concept itself
        )

        # Filter out the concept itself
        related = [(c, s) for c, s in results if c.id != concept_id]

        # Limit the number of results
        return related[:n_results]
