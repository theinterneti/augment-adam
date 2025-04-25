"""
Base classes for the memory system.

This module provides the base classes for the memory system, including
the Memory base class, MemoryItem class, and MemoryManager class.
"""

import uuid
import json
import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory


class MemoryType(Enum):
    """
    Types of memory in the memory system.
    
    This enum defines the types of memory in the memory system, including
    vector, graph, episodic, semantic, and working memory.
    """
    
    VECTOR = auto()
    GRAPH = auto()
    EPISODIC = auto()
    SEMANTIC = auto()
    WORKING = auto()


@dataclass
class MemoryItem:
    """
    Item stored in memory.
    
    This class represents an item stored in memory, including its content,
    metadata, and other properties.
    
    Attributes:
        id: Unique identifier for the memory item.
        content: The content of the memory item.
        metadata: Additional metadata for the memory item.
        created_at: When the memory item was created.
        updated_at: When the memory item was last updated.
        expires_at: When the memory item expires (if applicable).
        importance: Importance score for the memory item (0-1).
        embedding: Vector embedding for the memory item (if applicable).
    
    TODO(Issue #6): Add support for memory item versioning
    TODO(Issue #6): Implement memory item validation
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    expires_at: Optional[str] = None
    importance: float = 0.5
    embedding: Optional[List[float]] = None
    
    def __post_init__(self) -> None:
        """Initialize the memory item with timestamps."""
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def update(self, content: Any = None, metadata: Dict[str, Any] = None) -> None:
        """
        Update the memory item.
        
        Args:
            content: New content for the memory item.
            metadata: New metadata for the memory item.
        """
        if content is not None:
            self.content = content
        
        if metadata is not None:
            self.metadata.update(metadata)
        
        self.updated_at = datetime.datetime.now().isoformat()
    
    def is_expired(self) -> bool:
        """
        Check if the memory item is expired.
        
        Returns:
            True if the memory item is expired, False otherwise.
        """
        if self.expires_at is None:
            return False
        
        expires_at = datetime.datetime.fromisoformat(self.expires_at)
        return datetime.datetime.now() > expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary.
        
        Returns:
            Dictionary representation of the memory item.
        """
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "importance": self.importance,
            "embedding": self.embedding,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """
        Create a memory item from a dictionary.
        
        Args:
            data: Dictionary representation of the memory item.
            
        Returns:
            Memory item.
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            expires_at=data.get("expires_at"),
            importance=data.get("importance", 0.5),
            embedding=data.get("embedding"),
        )


T = TypeVar('T', bound=MemoryItem)


@tag("memory")
class Memory(Generic[T], ABC):
    """
    Base class for memory systems.
    
    This class defines the interface for memory systems, including methods
    for adding, retrieving, updating, and removing items from memory.
    
    Attributes:
        name: The name of the memory system.
        memory_type: The type of memory system.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str, memory_type: MemoryType) -> None:
        """
        Initialize the memory system.
        
        Args:
            name: The name of the memory system.
            memory_type: The type of memory system.
        """
        self.name = name
        self.memory_type = memory_type
        self.items: Dict[str, T] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add(self, item: T) -> str:
        """
        Add an item to memory.
        
        Args:
            item: The item to add to memory.
            
        Returns:
            The ID of the added item.
        """
        self.items[item.id] = item
        return item.id
    
    def get(self, item_id: str) -> Optional[T]:
        """
        Get an item from memory by ID.
        
        Args:
            item_id: The ID of the item to get.
            
        Returns:
            The item, or None if it doesn't exist.
        """
        return self.items.get(item_id)
    
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
        item = self.get(item_id)
        if item is None:
            return None
        
        item.update(content, metadata)
        return item
    
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.
        
        Args:
            item_id: The ID of the item to remove.
            
        Returns:
            True if the item was removed, False otherwise.
        """
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
    
    def clear(self) -> None:
        """Remove all items from memory."""
        self.items = {}
    
    def get_all(self) -> List[T]:
        """
        Get all items from memory.
        
        Returns:
            List of all items in memory.
        """
        return list(self.items.values())
    
    def count(self) -> int:
        """
        Get the number of items in memory.
        
        Returns:
            The number of items in memory.
        """
        return len(self.items)
    
    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        """
        Filter items in memory.
        
        Args:
            predicate: Function that takes an item and returns True if it should be included.
            
        Returns:
            List of items that match the predicate.
        """
        return [item for item in self.items.values() if predicate(item)]
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the memory system.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the memory system.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    @abstractmethod
    def search(self, query: Any, limit: int = 10) -> List[T]:
        """
        Search for items in memory.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query.
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory system to a dictionary.
        
        Returns:
            Dictionary representation of the memory system.
        """
        return {
            "name": self.name,
            "memory_type": self.memory_type.name,
            "items": {item_id: item.to_dict() for item_id, item in self.items.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """
        Create a memory system from a dictionary.
        
        Args:
            data: Dictionary representation of the memory system.
            
        Returns:
            Memory system.
        """
        memory = cls(
            name=data.get("name", ""),
            memory_type=MemoryType[data.get("memory_type", "VECTOR")],
        )
        
        memory.metadata = data.get("metadata", {})
        
        for item_data in data.get("items", {}).values():
            item = MemoryItem.from_dict(item_data)
            memory.add(item)
        
        return memory


@tag("memory")
class MemoryManager:
    """
    Manager for memory systems.
    
    This class manages multiple memory systems, providing a unified interface
    for adding, retrieving, updating, and removing items from memory.
    
    Attributes:
        memories: Dictionary of memory systems, keyed by name.
        metadata: Additional metadata for the memory manager.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self) -> None:
        """Initialize the memory manager."""
        self.memories: Dict[str, Memory] = {}
        self.metadata: Dict[str, Any] = {}
    
    def register_memory(self, memory: Memory) -> None:
        """
        Register a memory system with the manager.
        
        Args:
            memory: The memory system to register.
        """
        self.memories[memory.name] = memory
    
    def unregister_memory(self, name: str) -> bool:
        """
        Unregister a memory system from the manager.
        
        Args:
            name: The name of the memory system to unregister.
            
        Returns:
            True if the memory system was unregistered, False otherwise.
        """
        if name in self.memories:
            del self.memories[name]
            return True
        return False
    
    def get_memory(self, name: str) -> Optional[Memory]:
        """
        Get a memory system by name.
        
        Args:
            name: The name of the memory system.
            
        Returns:
            The memory system, or None if it doesn't exist.
        """
        return self.memories.get(name)
    
    def get_memories_by_type(self, memory_type: MemoryType) -> List[Memory]:
        """
        Get memory systems by type.
        
        Args:
            memory_type: The type of memory systems to get.
            
        Returns:
            List of memory systems of the specified type.
        """
        return [memory for memory in self.memories.values() if memory.memory_type == memory_type]
    
    def get_all_memories(self) -> List[Memory]:
        """
        Get all memory systems.
        
        Returns:
            List of all memory systems.
        """
        return list(self.memories.values())
    
    def add_item(self, memory_name: str, item: MemoryItem) -> Optional[str]:
        """
        Add an item to a memory system.
        
        Args:
            memory_name: The name of the memory system.
            item: The item to add.
            
        Returns:
            The ID of the added item, or None if the memory system doesn't exist.
        """
        memory = self.get_memory(memory_name)
        if memory is None:
            return None
        
        return memory.add(item)
    
    def get_item(self, memory_name: str, item_id: str) -> Optional[MemoryItem]:
        """
        Get an item from a memory system.
        
        Args:
            memory_name: The name of the memory system.
            item_id: The ID of the item.
            
        Returns:
            The item, or None if the memory system or item doesn't exist.
        """
        memory = self.get_memory(memory_name)
        if memory is None:
            return None
        
        return memory.get(item_id)
    
    def update_item(self, memory_name: str, item_id: str, content: Any = None, metadata: Dict[str, Any] = None) -> Optional[MemoryItem]:
        """
        Update an item in a memory system.
        
        Args:
            memory_name: The name of the memory system.
            item_id: The ID of the item.
            content: New content for the item.
            metadata: New metadata for the item.
            
        Returns:
            The updated item, or None if the memory system or item doesn't exist.
        """
        memory = self.get_memory(memory_name)
        if memory is None:
            return None
        
        return memory.update(item_id, content, metadata)
    
    def remove_item(self, memory_name: str, item_id: str) -> bool:
        """
        Remove an item from a memory system.
        
        Args:
            memory_name: The name of the memory system.
            item_id: The ID of the item.
            
        Returns:
            True if the item was removed, False otherwise.
        """
        memory = self.get_memory(memory_name)
        if memory is None:
            return False
        
        return memory.remove(item_id)
    
    def search(self, memory_name: str, query: Any, limit: int = 10) -> List[MemoryItem]:
        """
        Search for items in a memory system.
        
        Args:
            memory_name: The name of the memory system.
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query, or an empty list if the memory system doesn't exist.
        """
        memory = self.get_memory(memory_name)
        if memory is None:
            return []
        
        return memory.search(query, limit)
    
    def search_all(self, query: Any, limit: int = 10) -> Dict[str, List[MemoryItem]]:
        """
        Search for items in all memory systems.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return per memory system.
            
        Returns:
            Dictionary of search results, keyed by memory system name.
        """
        results = {}
        for name, memory in self.memories.items():
            results[name] = memory.search(query, limit)
        
        return results
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the memory manager.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the memory manager.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory manager to a dictionary.
        
        Returns:
            Dictionary representation of the memory manager.
        """
        return {
            "memories": {name: memory.to_dict() for name, memory in self.memories.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryManager':
        """
        Create a memory manager from a dictionary.
        
        Args:
            data: Dictionary representation of the memory manager.
            
        Returns:
            Memory manager.
        """
        manager = cls()
        manager.metadata = data.get("metadata", {})
        
        # Note: This is a simplified implementation
        # In a real implementation, you would need to create the appropriate
        # memory system for each memory type
        
        return manager


# Singleton instance
_memory_manager: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    """
    Get the singleton instance of the memory manager.
    
    Returns:
        The memory manager instance.
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
