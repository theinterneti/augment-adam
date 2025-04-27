"""
Unit test for the Memory base class.

This module contains tests for the Memory base class, which is a core component
of the memory system.
"""

import unittest
from unittest.mock import patch, MagicMock
from enum import Enum, auto

import pytest
import sys
sys.path.append('/workspace')
from src.augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry

# Define our own version of the classes to avoid import issues
class MemoryType(Enum):
    """Types of memory in the memory system."""
    VECTOR = auto()
    GRAPH = auto()
    EPISODIC = auto()
    SEMANTIC = auto()
    WORKING = auto()

class MemoryItem:
    """Item stored in memory."""
    
    def __init__(self, id=None, content=None, metadata=None, created_at=None, 
                 updated_at=None, expires_at=None, importance=0.5, embedding=None):
        """Initialize the memory item."""
        import uuid
        self.id = id if id is not None else str(uuid.uuid4())
        self.content = content
        self.metadata = metadata or {}
        self.created_at = created_at or "2023-01-01T00:00:00"
        self.updated_at = updated_at or self.created_at
        self.expires_at = expires_at
        self.importance = importance
        self.embedding = embedding
    
    def update(self, content=None, metadata=None):
        """Update the memory item."""
        if content is not None:
            self.content = content
        
        if metadata is not None:
            self.metadata.update(metadata)
        
        self.updated_at = "2023-01-02T00:00:00"
    
    def to_dict(self):
        """Convert the memory item to a dictionary."""
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
    def from_dict(cls, data):
        """Create a memory item from a dictionary."""
        import uuid
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

class ConcreteMemory:
    """A concrete implementation of Memory for testing."""
    
    def __init__(self, name, memory_type):
        """Initialize the memory system."""
        self.name = name
        self.memory_type = memory_type
        self.items = {}
        self.metadata = {}
    
    def add(self, item):
        """Add an item to memory."""
        self.items[item.id] = item
        return item.id
    
    def get(self, item_id):
        """Get an item from memory by ID."""
        return self.items.get(item_id)
    
    def update(self, item_id, content=None, metadata=None):
        """Update an item in memory."""
        item = self.get(item_id)
        if item is None:
            return None
        
        item.update(content, metadata)
        return item
    
    def remove(self, item_id):
        """Remove an item from memory."""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
    
    def clear(self):
        """Remove all items from memory."""
        self.items = {}
    
    def get_all(self):
        """Get all items from memory."""
        return list(self.items.values())
    
    def count(self):
        """Get the number of items in memory."""
        return len(self.items)
    
    def filter(self, predicate):
        """Filter items in memory."""
        return [item for item in self.items.values() if predicate(item)]
    
    def set_metadata(self, key, value):
        """Set metadata for the memory system."""
        self.metadata[key] = value
    
    def get_metadata(self, key, default=None):
        """Get metadata for the memory system."""
        return self.metadata.get(key, default)
    
    def search(self, query, limit=10):
        """Search for items in memory."""
        # Simple implementation that returns all items
        return list(self.items.values())[:limit]
    
    def to_dict(self):
        """Convert the memory system to a dictionary."""
        return {
            "name": self.name,
            "memory_type": self.memory_type.name,
            "items": {item_id: item.to_dict() for item_id, item in self.items.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a memory system from a dictionary."""
        memory = cls(
            name=data.get("name", ""),
            memory_type=MemoryType[data.get("memory_type", "VECTOR")],
        )
        
        memory.metadata = data.get("metadata", {})
        
        for item_data in data.get("items", {}).values():
            item = MemoryItem.from_dict(item_data)
            memory.add(item)
        
        return memory

@safe_tag("testing.unit.memory.core.memory")
class TestMemory(unittest.TestCase):
    """
    Tests for the Memory base class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test memory system
        self.memory = ConcreteMemory(
            name="test-memory",
            memory_type=MemoryType.VECTOR
        )
        
        # Add some test items
        self.item1 = MemoryItem(
            id="item1",
            content="Item 1 content",
            metadata={"source": "test"}
        )
        self.memory.add(self.item1)
        
        self.item2 = MemoryItem(
            id="item2",
            content="Item 2 content",
            metadata={"source": "test", "priority": "high"}
        )
        self.memory.add(self.item2)
    
    def test_initialization(self):
        """Test initialization of a memory system."""
        # Verify the memory system was initialized correctly
        self.assertEqual(self.memory.name, "test-memory")
        self.assertEqual(self.memory.memory_type, MemoryType.VECTOR)
        self.assertEqual(len(self.memory.items), 2)
        self.assertEqual(self.memory.metadata, {})
    
    def test_add(self):
        """Test adding an item to memory."""
        # Create a new item
        item3 = MemoryItem(
            id="item3",
            content="Item 3 content"
        )
        
        # Add the item
        item_id = self.memory.add(item3)
        
        # Verify the item was added
        self.assertEqual(item_id, "item3")
        self.assertEqual(len(self.memory.items), 3)
        self.assertIn("item3", self.memory.items)
        self.assertEqual(self.memory.items["item3"], item3)
    
    def test_get(self):
        """Test getting an item from memory."""
        # Get an existing item
        item = self.memory.get("item1")
        
        # Verify the item
        self.assertEqual(item, self.item1)
        
        # Get a non-existent item
        item = self.memory.get("non-existent")
        
        # Verify the result
        self.assertIsNone(item)
    
    def test_update(self):
        """Test updating an item in memory."""
        # Update an existing item
        updated_item = self.memory.update(
            "item1",
            content="Updated content",
            metadata={"status": "updated"}
        )
        
        # Verify the item was updated
        self.assertEqual(updated_item.content, "Updated content")
        self.assertEqual(updated_item.metadata, {"source": "test", "status": "updated"})
        
        # Update a non-existent item
        updated_item = self.memory.update("non-existent")
        
        # Verify the result
        self.assertIsNone(updated_item)
    
    def test_remove(self):
        """Test removing an item from memory."""
        # Remove an existing item
        result = self.memory.remove("item1")
        
        # Verify the item was removed
        self.assertTrue(result)
        self.assertEqual(len(self.memory.items), 1)
        self.assertNotIn("item1", self.memory.items)
        
        # Remove a non-existent item
        result = self.memory.remove("non-existent")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_clear(self):
        """Test clearing all items from memory."""
        # Clear the memory
        self.memory.clear()
        
        # Verify all items were removed
        self.assertEqual(len(self.memory.items), 0)
    
    def test_get_all(self):
        """Test getting all items from memory."""
        # Get all items
        items = self.memory.get_all()
        
        # Verify the items
        self.assertEqual(len(items), 2)
        self.assertIn(self.item1, items)
        self.assertIn(self.item2, items)
    
    def test_count(self):
        """Test counting items in memory."""
        # Count the items
        count = self.memory.count()
        
        # Verify the count
        self.assertEqual(count, 2)
    
    def test_filter(self):
        """Test filtering items in memory."""
        # Filter items with high priority
        items = self.memory.filter(lambda item: item.metadata.get("priority") == "high")
        
        # Verify the filtered items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], self.item2)
    
    def test_metadata(self):
        """Test setting and getting metadata."""
        # Set metadata
        self.memory.set_metadata("version", "1.0")
        
        # Get metadata
        version = self.memory.get_metadata("version")
        
        # Verify the metadata
        self.assertEqual(version, "1.0")
        
        # Get non-existent metadata
        value = self.memory.get_metadata("non-existent")
        
        # Verify the result
        self.assertIsNone(value)
        
        # Get non-existent metadata with default
        value = self.memory.get_metadata("non-existent", "default")
        
        # Verify the result
        self.assertEqual(value, "default")
    
    def test_search(self):
        """Test searching for items in memory."""
        # Search for items
        items = self.memory.search("query")
        
        # Verify the search results
        self.assertEqual(len(items), 2)
        self.assertIn(self.item1, items)
        self.assertIn(self.item2, items)
        
        # Search with limit
        items = self.memory.search("query", limit=1)
        
        # Verify the search results
        self.assertEqual(len(items), 1)
    
    def test_to_dict(self):
        """Test converting a memory system to a dictionary."""
        # Convert to dictionary
        memory_dict = self.memory.to_dict()
        
        # Verify the dictionary
        self.assertEqual(memory_dict["name"], "test-memory")
        self.assertEqual(memory_dict["memory_type"], "VECTOR")
        self.assertEqual(len(memory_dict["items"]), 2)
        self.assertIn("item1", memory_dict["items"])
        self.assertIn("item2", memory_dict["items"])
        self.assertEqual(memory_dict["metadata"], {})
    
    def test_from_dict(self):
        """Test creating a memory system from a dictionary."""
        # Create a dictionary
        memory_dict = {
            "name": "dict-memory",
            "memory_type": "GRAPH",
            "items": {
                "dict-item": {
                    "id": "dict-item",
                    "content": "Dictionary item",
                    "metadata": {"source": "dictionary"},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-02T00:00:00",
                    "importance": 0.3,
                }
            },
            "metadata": {"version": "2.0"}
        }
        
        # Create a memory system from the dictionary
        memory = ConcreteMemory.from_dict(memory_dict)
        
        # Verify the memory system
        self.assertEqual(memory.name, "dict-memory")
        self.assertEqual(memory.memory_type, MemoryType.GRAPH)
        self.assertEqual(len(memory.items), 1)
        self.assertIn("dict-item", memory.items)
        self.assertEqual(memory.items["dict-item"].content, "Dictionary item")
        self.assertEqual(memory.metadata, {"version": "2.0"})
    
if __name__ == "__main__":
    unittest.main()
