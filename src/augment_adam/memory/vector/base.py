"""
Base classes for vector-based memory systems.

This module provides the base classes for vector-based memory systems,
including the VectorMemory base class and VectorMemoryItem class.
"""

from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType


@dataclass
class VectorMemoryItem(MemoryItem):
    """
    Item stored in vector memory.
    
    This class represents an item stored in vector memory, including its content,
    metadata, and vector embedding.
    
    Attributes:
        id: Unique identifier for the memory item.
        content: The content of the memory item.
        metadata: Additional metadata for the memory item.
        created_at: When the memory item was created.
        updated_at: When the memory item was last updated.
        expires_at: When the memory item expires (if applicable).
        importance: Importance score for the memory item (0-1).
        embedding: Vector embedding for the memory item.
        text: Text representation of the content (for text-based items).
    
    TODO(Issue #6): Add support for memory item versioning
    TODO(Issue #6): Implement memory item validation
    """
    
    text: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Initialize the vector memory item."""
        super().__post_init__()
        
        # If text is not provided but content is a string, use content as text
        if self.text is None and isinstance(self.content, str):
            self.text = self.content
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the vector memory item to a dictionary.
        
        Returns:
            Dictionary representation of the vector memory item.
        """
        data = super().to_dict()
        data["text"] = self.text
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorMemoryItem':
        """
        Create a vector memory item from a dictionary.
        
        Args:
            data: Dictionary representation of the vector memory item.
            
        Returns:
            Vector memory item.
        """
        item = super().from_dict(data)
        item.text = data.get("text")
        return item


T = TypeVar('T', bound=VectorMemoryItem)


@tag("memory.vector")
class VectorMemory(Memory[T]):
    """
    Base class for vector-based memory systems.
    
    This class defines the interface for vector-based memory systems, including
    methods for adding, retrieving, updating, and removing items from memory,
    as well as methods for similarity search.
    
    Attributes:
        name: The name of the memory system.
        dimension: The dimension of the vector embeddings.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str, dimension: int = 1536) -> None:
        """
        Initialize the vector memory system.
        
        Args:
            name: The name of the memory system.
            dimension: The dimension of the vector embeddings.
        """
        super().__init__(name, MemoryType.VECTOR)
        self.dimension = dimension
        self.metadata["dimension"] = dimension
    
    def add(self, item: T) -> str:
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
        
        return super().add(item)
    
    def update(self, item_id: str, content: Any = None, metadata: Dict[str, Any] = None) -> Optional[T]:
        """
        Update an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            content: New content for the item.
            metadata: New metadata for the item.
            
        Returns:
            The updated item, or None if it doesn't exist.
        """
        item = super().update(item_id, content, metadata)
        
        if item is not None and content is not None:
            # If the content was updated, update the text and embedding
            if isinstance(content, str):
                item.text = content
            
            if item.text is not None:
                item.embedding = self.generate_embedding(item.text)
        
        return item
    
    def search(self, query: Union[str, List[float]], limit: int = 10) -> List[T]:
        """
        Search for items in memory by similarity.
        
        Args:
            query: The query to search for (either a string or a vector embedding).
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query, sorted by similarity.
        """
        # If the query is a string, convert it to a vector embedding
        if isinstance(query, str):
            query_embedding = self.generate_embedding(query)
        else:
            query_embedding = query
        
        # Get items with embeddings
        items_with_embeddings = [item for item in self.items.values() if item.embedding is not None]
        
        # Calculate similarity scores
        items_with_scores = [(item, self.calculate_similarity(query_embedding, item.embedding)) for item in items_with_embeddings]
        
        # Sort by similarity score (descending)
        items_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top results
        return [item for item, score in items_with_scores[:limit]]
    
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
        return [0.0] * self.dimension
    
    def calculate_similarity(self, embedding1: List[float], embedding2: Optional[List[float]]) -> float:
        """
        Calculate the similarity between two vector embeddings.
        
        Args:
            embedding1: The first vector embedding.
            embedding2: The second vector embedding.
            
        Returns:
            Similarity score between the two embeddings (0-1).
        """
        if embedding2 is None:
            return 0.0
        
        # This is a placeholder implementation using cosine similarity
        # In a real implementation, you would use a more efficient method
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Calculate magnitudes
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        # Calculate cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the vector memory system to a dictionary.
        
        Returns:
            Dictionary representation of the vector memory system.
        """
        data = super().to_dict()
        data["dimension"] = self.dimension
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorMemory':
        """
        Create a vector memory system from a dictionary.
        
        Args:
            data: Dictionary representation of the vector memory system.
            
        Returns:
            Vector memory system.
        """
        memory = cls(
            name=data.get("name", ""),
            dimension=data.get("dimension", 1536),
        )
        
        memory.metadata = data.get("metadata", {})
        
        for item_data in data.get("items", {}).values():
            item = VectorMemoryItem.from_dict(item_data)
            memory.add(item)
        
        return memory
