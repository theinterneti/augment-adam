"""
Chroma-based vector memory system.

This module provides a vector memory system based on Chroma,
which is a database for storing and querying embeddings.
"""

import os
import json
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, cast
import chromadb
from chromadb.config import Settings

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.vector.base import VectorMemory, VectorMemoryItem


@tag("memory.vector.chroma")
class ChromaMemory(VectorMemory[VectorMemoryItem]):
    """
    Chroma-based vector memory system.

    This class implements a vector memory system using Chroma for efficient
    storage and retrieval of vector embeddings.

    Attributes:
        name: The name of the memory system.
        dimension: The dimension of the vector embeddings.
        client: The Chroma client.
        collection: The Chroma collection.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.

    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """

    def __init__(self, name: str, dimension: int = 1536, persist_directory: Optional[str] = None) -> None:
        """
        Initialize the Chroma memory system.

        Args:
            name: The name of the memory system.
            dimension: The dimension of the vector embeddings.
            persist_directory: Directory to persist the Chroma database to.
        """
        super().__init__(name, dimension)

        # Create Chroma client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(name=name)

        self.metadata["persist_directory"] = persist_directory

    def add(self, item: VectorMemoryItem) -> str:
        """
        Add an item to memory.

        Args:
            item: The item to add to memory.

        Returns:
            The ID of the added item.
        """
        # If the item doesn't have an embedding, generate one
        if item.embedding is None and item.text is not None:
            item.embedding = self.generate_embedding(item.text)

        # Add the item to the dictionary
        super().add(item)

        # Add the item to the Chroma collection
        if item.embedding is not None and item.text is not None:
            # Prepare metadata, filtering out None values
            metadata = {
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "importance": item.importance,
                **item.metadata
            }

            # Remove None values from metadata as Chroma doesn't handle them well
            metadata = {k: v for k, v in metadata.items() if v is not None}

            self.collection.add(
                ids=[item.id],
                embeddings=[item.embedding],
                documents=[item.text],
                metadatas=[metadata]
            )

        return item.id

    def update(self, item_id: str, content: Any = None, metadata: Dict[str, Any] = None) -> Optional[VectorMemoryItem]:
        """
        Update an item in memory.

        Args:
            item_id: The ID of the item to update.
            content: New content for the item.
            metadata: New metadata for the item.

        Returns:
            The updated item, or None if it doesn't exist.
        """
        # Update the item in the dictionary
        updated_item = super().update(item_id, content, metadata)

        # If the item was updated, update it in the Chroma collection
        if updated_item is not None and updated_item.embedding is not None and updated_item.text is not None:
            # Prepare metadata, filtering out None values
            metadata = {
                "created_at": updated_item.created_at,
                "updated_at": updated_item.updated_at,
                "importance": updated_item.importance,
                **updated_item.metadata
            }

            # Remove None values from metadata as Chroma doesn't handle them well
            metadata = {k: v for k, v in metadata.items() if v is not None}

            self.collection.update(
                ids=[item_id],
                embeddings=[updated_item.embedding],
                documents=[updated_item.text],
                metadatas=[metadata]
            )

        return updated_item

    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.

        Args:
            item_id: The ID of the item to remove.

        Returns:
            True if the item was removed, False otherwise.
        """
        # Remove the item from the dictionary
        if not super().remove(item_id):
            return False

        # Remove the item from the Chroma collection
        self.collection.delete(ids=[item_id])

        return True

    def clear(self) -> None:
        """Remove all items from memory."""
        super().clear()

        # Clear the Chroma collection
        self.collection.delete(ids=self.collection.get()["ids"])

    def search(self, query: Union[str, List[float]], limit: int = 10) -> List[VectorMemoryItem]:
        """
        Search for items in memory by similarity.

        Args:
            query: The query to search for (either a string or a vector embedding).
            limit: The maximum number of results to return.

        Returns:
            List of items that match the query, sorted by similarity.
        """
        # If the collection is empty, return an empty list
        if self.collection.count() == 0:
            return []

        # If the query is a string, search by text
        if isinstance(query, str):
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
        # Otherwise, search by embedding
        else:
            results = self.collection.query(
                query_embeddings=[query],
                n_results=limit
            )

        # Convert the results to memory items
        items = []
        for i, item_id in enumerate(results["ids"][0]):
            item = self.get(item_id)
            if item is not None:
                items.append(item)

        return items

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a vector embedding for a text.

        Args:
            text: The text to generate an embedding for.

        Returns:
            Vector embedding for the text.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use a model to generate embeddings
        # For example, using OpenAI's text-embedding-ada-002 model

        # For now, we'll just use a random embedding
        embedding = np.random.randn(self.dimension).astype(np.float32)
        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.tolist()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Chroma memory system to a dictionary.

        Returns:
            Dictionary representation of the Chroma memory system.
        """
        data = super().to_dict()
        data["persist_directory"] = self.metadata.get("persist_directory")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChromaMemory':
        """
        Create a Chroma memory system from a dictionary.

        Args:
            data: Dictionary representation of the Chroma memory system.

        Returns:
            Chroma memory system.
        """
        memory = cls(
            name=data.get("name", ""),
            dimension=data.get("dimension", 1536),
            persist_directory=data.get("persist_directory"),
        )

        memory.metadata = data.get("metadata", {})

        # Load items from the Chroma collection
        results = memory.collection.get()

        for i, item_id in enumerate(results["ids"]):
            embedding = results["embeddings"][i] if "embeddings" in results else None
            text = results["documents"][i] if "documents" in results else None
            metadata = results["metadatas"][i] if "metadatas" in results else {}

            # Extract standard metadata
            created_at = metadata.pop("created_at", None)
            updated_at = metadata.pop("updated_at", None)
            expires_at = metadata.pop("expires_at", None)
            importance = metadata.pop("importance", 0.5)

            # Create the memory item
            item = VectorMemoryItem(
                id=item_id,
                content=text,
                metadata=metadata,
                created_at=created_at,
                updated_at=updated_at,
                expires_at=expires_at,
                importance=importance,
                embedding=embedding,
                text=text,
            )

            # Add the item to the dictionary
            memory.items[item_id] = item

        return memory
