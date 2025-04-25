"""
Base classes for working memory system.

This module provides the base classes for the working memory system,
including the WorkingMemory class and WorkingMemoryItem class.
"""

import uuid
import datetime
import time
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType


@dataclass
class WorkingMemoryItem(MemoryItem):
    """
    Item stored in working memory.
    
    This class represents an item stored in working memory, including its content,
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
        task_id: ID of the task this item is associated with.
        priority: Priority of the item (0-10).
        status: Status of the item (e.g., "active", "completed", "pending").
        ttl: Time-to-live in seconds (0 means no expiration).
    
    TODO(Issue #6): Add support for memory item versioning
    TODO(Issue #6): Implement memory item validation
    """
    
    task_id: Optional[str] = None
    priority: int = 5
    status: str = "active"
    ttl: int = 0
    
    def __post_init__(self) -> None:
        """Initialize the working memory item with timestamps."""
        super().__post_init__()
        
        # Set expires_at based on ttl if provided
        if self.ttl > 0 and self.expires_at is None:
            created_at = datetime.datetime.fromisoformat(self.created_at)
            expires_at = created_at + datetime.timedelta(seconds=self.ttl)
            self.expires_at = expires_at.isoformat()
    
    def is_expired(self) -> bool:
        """
        Check if the working memory item is expired.
        
        Returns:
            True if the working memory item is expired, False otherwise.
        """
        # If ttl is 0, the item never expires
        if self.ttl == 0:
            return False
        
        return super().is_expired()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the working memory item to a dictionary.
        
        Returns:
            Dictionary representation of the working memory item.
        """
        data = super().to_dict()
        data["task_id"] = self.task_id
        data["priority"] = self.priority
        data["status"] = self.status
        data["ttl"] = self.ttl
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkingMemoryItem':
        """
        Create a working memory item from a dictionary.
        
        Args:
            data: Dictionary representation of the working memory item.
            
        Returns:
            Working memory item.
        """
        item = super().from_dict(data)
        item.task_id = data.get("task_id")
        item.priority = data.get("priority", 5)
        item.status = data.get("status", "active")
        item.ttl = data.get("ttl", 0)
        return item


T = TypeVar('T', bound=WorkingMemoryItem)


@tag("memory.working")
class WorkingMemory(Memory[T]):
    """
    Working memory system.
    
    This class implements a working memory system for temporary storage of
    information during ongoing tasks.
    
    Attributes:
        name: The name of the memory system.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
        capacity: Maximum number of items in memory (0 means unlimited).
        cleanup_interval: Interval in seconds for automatic cleanup of expired items.
        last_cleanup: Timestamp of the last cleanup.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str, capacity: int = 0, cleanup_interval: int = 60) -> None:
        """
        Initialize the working memory system.
        
        Args:
            name: The name of the memory system.
            capacity: Maximum number of items in memory (0 means unlimited).
            cleanup_interval: Interval in seconds for automatic cleanup of expired items.
        """
        super().__init__(name, MemoryType.WORKING)
        
        self.capacity = capacity
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        
        self.metadata["capacity"] = capacity
        self.metadata["cleanup_interval"] = cleanup_interval
    
    def add(self, item: T) -> str:
        """
        Add an item to memory.
        
        Args:
            item: The item to add to memory.
            
        Returns:
            The ID of the added item.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        # Check if capacity is reached
        if self.capacity > 0 and len(self.items) >= self.capacity:
            # Remove the least important item
            self._remove_least_important()
        
        return super().add(item)
    
    def get(self, item_id: str) -> Optional[T]:
        """
        Get an item from memory by ID.
        
        Args:
            item_id: The ID of the item to get.
            
        Returns:
            The item, or None if it doesn't exist or is expired.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        item = super().get(item_id)
        
        # Check if the item is expired
        if item is not None and item.is_expired():
            self.remove(item_id)
            return None
        
        return item
    
    def update(self, item_id: str, content: Any = None, metadata: Dict[str, Any] = None) -> Optional[T]:
        """
        Update an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            content: New content for the item.
            metadata: New metadata for the item.
            
        Returns:
            The updated item, or None if it doesn't exist or is expired.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        item = super().get(item_id)
        
        # Check if the item is expired
        if item is not None and item.is_expired():
            self.remove(item_id)
            return None
        
        return super().update(item_id, content, metadata)
    
    def get_all(self) -> List[T]:
        """
        Get all items from memory.
        
        Returns:
            List of all items in memory that are not expired.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        # Filter out expired items
        return [item for item in super().get_all() if not item.is_expired()]
    
    def get_by_task(self, task_id: str) -> List[T]:
        """
        Get items from memory by task ID.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            List of items associated with the task.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        return [item for item in self.items.values() if item.task_id == task_id and not item.is_expired()]
    
    def get_by_status(self, status: str) -> List[T]:
        """
        Get items from memory by status.
        
        Args:
            status: The status of the items.
            
        Returns:
            List of items with the specified status.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        return [item for item in self.items.values() if item.status == status and not item.is_expired()]
    
    def get_by_priority(self, min_priority: int = 0, max_priority: int = 10) -> List[T]:
        """
        Get items from memory by priority range.
        
        Args:
            min_priority: The minimum priority (inclusive).
            max_priority: The maximum priority (inclusive).
            
        Returns:
            List of items with priority in the specified range.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        return [item for item in self.items.values() if min_priority <= item.priority <= max_priority and not item.is_expired()]
    
    def update_status(self, item_id: str, status: str) -> Optional[T]:
        """
        Update the status of an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            status: The new status for the item.
            
        Returns:
            The updated item, or None if it doesn't exist or is expired.
        """
        item = self.get(item_id)
        if item is None:
            return None
        
        item.status = status
        item.updated_at = datetime.datetime.now().isoformat()
        
        return item
    
    def update_priority(self, item_id: str, priority: int) -> Optional[T]:
        """
        Update the priority of an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            priority: The new priority for the item.
            
        Returns:
            The updated item, or None if it doesn't exist or is expired.
        """
        item = self.get(item_id)
        if item is None:
            return None
        
        item.priority = priority
        item.updated_at = datetime.datetime.now().isoformat()
        
        return item
    
    def update_ttl(self, item_id: str, ttl: int) -> Optional[T]:
        """
        Update the time-to-live of an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            ttl: The new time-to-live in seconds.
            
        Returns:
            The updated item, or None if it doesn't exist or is expired.
        """
        item = self.get(item_id)
        if item is None:
            return None
        
        item.ttl = ttl
        
        # Update expires_at based on ttl
        if ttl > 0:
            updated_at = datetime.datetime.fromisoformat(item.updated_at)
            expires_at = updated_at + datetime.timedelta(seconds=ttl)
            item.expires_at = expires_at.isoformat()
        else:
            item.expires_at = None
        
        return item
    
    def search(self, query: Any, limit: int = 10) -> List[T]:
        """
        Search for items in memory.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query.
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        # If the query is a string, search for items with matching content
        if isinstance(query, str):
            results = []
            
            for item in self.items.values():
                # Skip expired items
                if item.is_expired():
                    continue
                
                # Check if the item content contains the query
                if item.content and isinstance(item.content, str) and query.lower() in item.content.lower():
                    results.append(item)
            
            return results[:limit]
        
        # If the query is a dictionary, search for items with matching attributes
        elif isinstance(query, dict):
            results = []
            
            for item in self.items.values():
                # Skip expired items
                if item.is_expired():
                    continue
                
                # Check if all query attributes match
                match = True
                for key, value in query.items():
                    if key == "task_id" and item.task_id != value:
                        match = False
                        break
                    elif key == "priority" and item.priority != value:
                        match = False
                        break
                    elif key == "status" and item.status != value:
                        match = False
                        break
                    elif key == "ttl" and item.ttl != value:
                        match = False
                        break
                    elif key in item.metadata and item.metadata[key] != value:
                        match = False
                        break
                    elif key not in ["task_id", "priority", "status", "ttl"] and key not in item.metadata:
                        match = False
                        break
                
                if match:
                    results.append(item)
            
            return results[:limit]
        
        # Otherwise, use the default search
        return super().search(query, limit)
    
    def _maybe_cleanup(self) -> None:
        """
        Clean up expired items if the cleanup interval has passed.
        """
        now = time.time()
        if now - self.last_cleanup >= self.cleanup_interval:
            self._cleanup()
            self.last_cleanup = now
    
    def _cleanup(self) -> None:
        """
        Clean up expired items.
        """
        # Find expired items
        expired_ids = []
        for item_id, item in self.items.items():
            if item.is_expired():
                expired_ids.append(item_id)
        
        # Remove expired items
        for item_id in expired_ids:
            super().remove(item_id)
    
    def _remove_least_important(self) -> None:
        """
        Remove the least important item from memory.
        """
        if not self.items:
            return
        
        # Find the item with the lowest importance and priority
        least_important_id = None
        least_importance = float('inf')
        least_priority = float('inf')
        
        for item_id, item in self.items.items():
            # Skip expired items (they will be cleaned up anyway)
            if item.is_expired():
                continue
            
            # Calculate a score based on importance and priority
            score = item.importance * 10 + item.priority
            
            if score < least_importance or (score == least_importance and item.priority < least_priority):
                least_important_id = item_id
                least_importance = score
                least_priority = item.priority
        
        # Remove the least important item
        if least_important_id is not None:
            super().remove(least_important_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the working memory system to a dictionary.
        
        Returns:
            Dictionary representation of the working memory system.
        """
        data = super().to_dict()
        data["capacity"] = self.capacity
        data["cleanup_interval"] = self.cleanup_interval
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkingMemory':
        """
        Create a working memory system from a dictionary.
        
        Args:
            data: Dictionary representation of the working memory system.
            
        Returns:
            Working memory system.
        """
        memory = cls(
            name=data.get("name", ""),
            capacity=data.get("capacity", 0),
            cleanup_interval=data.get("cleanup_interval", 60)
        )
        
        memory.metadata = data.get("metadata", {})
        
        for item_data in data.get("items", {}).values():
            item = WorkingMemoryItem.from_dict(item_data)
            
            # Skip expired items
            if not item.is_expired():
                memory.add(item)
        
        return memory
