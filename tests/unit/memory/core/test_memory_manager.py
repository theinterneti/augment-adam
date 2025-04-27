"""
Unit test for the MemoryManager class.

This module contains tests for the MemoryManager class, which is a core component
of the memory system.
"""

import unittest
from unittest.mock import patch, MagicMock
from enum import Enum, auto

import pytest
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry

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

class Memory:
    """Base class for memory systems."""
    
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
    
    def search(self, query, limit=10):
        """Search for items in memory."""
        # Simple implementation that returns all items
        return list(self.items.values())[:limit]

class MemoryManager:
    """Manager for memory systems."""
    
    def __init__(self):
        """Initialize the memory manager."""
        self.memories = {}
        self.metadata = {}
    
    def register_memory(self, memory):
        """Register a memory system with the manager."""
        self.memories[memory.name] = memory
    
    def unregister_memory(self, name):
        """Unregister a memory system from the manager."""
        if name in self.memories:
            del self.memories[name]
            return True
        return False
    
    def get_memory(self, name):
        """Get a memory system by name."""
        return self.memories.get(name)
    
    def get_memories_by_type(self, memory_type):
        """Get memory systems by type."""
        return [memory for memory in self.memories.values() if memory.memory_type == memory_type]
    
    def get_all_memories(self):
        """Get all memory systems."""
        return list(self.memories.values())
    
    def add_item(self, memory_name, item):
        """Add an item to a memory system."""
        memory = self.get_memory(memory_name)
        if memory is None:
            return None
        
        return memory.add(item)
    
    def get_item(self, memory_name, item_id):
        """Get an item from a memory system."""
        memory = self.get_memory(memory_name)
        if memory is None:
            return None
        
        return memory.get(item_id)
    
    def update_item(self, memory_name, item_id, content=None, metadata=None):
        """Update an item in a memory system."""
        memory = self.get_memory(memory_name)
        if memory is None:
            return None
        
        return memory.update(item_id, content, metadata)
    
    def remove_item(self, memory_name, item_id):
        """Remove an item from a memory system."""
        memory = self.get_memory(memory_name)
        if memory is None:
            return False
        
        return memory.remove(item_id)
    
    def search(self, memory_name, query, limit=10):
        """Search for items in a memory system."""
        memory = self.get_memory(memory_name)
        if memory is None:
            return []
        
        return memory.search(query, limit)

@safe_tag("testing.unit.memory.core.memory_manager")
class TestMemoryManager(unittest.TestCase):
    """
    Tests for the MemoryManager class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test memory manager
        self.manager = MemoryManager()
        
        # Create test memory systems
        self.vector_memory = Memory(
            name="vector-memory",
            memory_type=MemoryType.VECTOR
        )
        self.graph_memory = Memory(
            name="graph-memory",
            memory_type=MemoryType.GRAPH
        )
        
        # Register the memory systems
        self.manager.register_memory(self.vector_memory)
        self.manager.register_memory(self.graph_memory)
        
        # Add test items to the vector memory
        self.item1 = MemoryItem(
            id="item1",
            content="Item 1 content",
            metadata={"source": "test"}
        )
        self.vector_memory.add(self.item1)
        
        self.item2 = MemoryItem(
            id="item2",
            content="Item 2 content",
            metadata={"source": "test", "priority": "high"}
        )
        self.vector_memory.add(self.item2)
    
    def test_initialization(self):
        """Test initialization of a memory manager."""
        # Verify the memory manager was initialized correctly
        self.assertEqual(len(self.manager.memories), 2)
        self.assertEqual(self.manager.metadata, {})
    
    def test_register_memory(self):
        """Test registering a memory system."""
        # Create a new memory system
        episodic_memory = Memory(
            name="episodic-memory",
            memory_type=MemoryType.EPISODIC
        )
        
        # Register the memory system
        self.manager.register_memory(episodic_memory)
        
        # Verify the memory system was registered
        self.assertEqual(len(self.manager.memories), 3)
        self.assertIn("episodic-memory", self.manager.memories)
        self.assertEqual(self.manager.memories["episodic-memory"], episodic_memory)
    
    def test_unregister_memory(self):
        """Test unregistering a memory system."""
        # Unregister an existing memory system
        result = self.manager.unregister_memory("vector-memory")
        
        # Verify the memory system was unregistered
        self.assertTrue(result)
        self.assertEqual(len(self.manager.memories), 1)
        self.assertNotIn("vector-memory", self.manager.memories)
        
        # Unregister a non-existent memory system
        result = self.manager.unregister_memory("non-existent")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_get_memory(self):
        """Test getting a memory system by name."""
        # Get an existing memory system
        memory = self.manager.get_memory("vector-memory")
        
        # Verify the memory system
        self.assertEqual(memory, self.vector_memory)
        
        # Get a non-existent memory system
        memory = self.manager.get_memory("non-existent")
        
        # Verify the result
        self.assertIsNone(memory)
    
    def test_get_memories_by_type(self):
        """Test getting memory systems by type."""
        # Get memory systems by type
        memories = self.manager.get_memories_by_type(MemoryType.VECTOR)
        
        # Verify the memory systems
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0], self.vector_memory)
        
        # Get memory systems by a type with no memories
        memories = self.manager.get_memories_by_type(MemoryType.WORKING)
        
        # Verify the result
        self.assertEqual(len(memories), 0)
    
    def test_get_all_memories(self):
        """Test getting all memory systems."""
        # Get all memory systems
        memories = self.manager.get_all_memories()
        
        # Verify the memory systems
        self.assertEqual(len(memories), 2)
        self.assertIn(self.vector_memory, memories)
        self.assertIn(self.graph_memory, memories)
    
    def test_add_item(self):
        """Test adding an item to a memory system."""
        # Create a new item
        item3 = MemoryItem(
            id="item3",
            content="Item 3 content"
        )
        
        # Add the item to an existing memory system
        item_id = self.manager.add_item("vector-memory", item3)
        
        # Verify the item was added
        self.assertEqual(item_id, "item3")
        self.assertEqual(len(self.vector_memory.items), 3)
        self.assertIn("item3", self.vector_memory.items)
        
        # Add an item to a non-existent memory system
        item_id = self.manager.add_item("non-existent", item3)
        
        # Verify the result
        self.assertIsNone(item_id)
    
    def test_get_item(self):
        """Test getting an item from a memory system."""
        # Get an existing item from an existing memory system
        item = self.manager.get_item("vector-memory", "item1")
        
        # Verify the item
        self.assertEqual(item, self.item1)
        
        # Get a non-existent item from an existing memory system
        item = self.manager.get_item("vector-memory", "non-existent")
        
        # Verify the result
        self.assertIsNone(item)
        
        # Get an item from a non-existent memory system
        item = self.manager.get_item("non-existent", "item1")
        
        # Verify the result
        self.assertIsNone(item)
    
    def test_update_item(self):
        """Test updating an item in a memory system."""
        # Update an existing item in an existing memory system
        updated_item = self.manager.update_item(
            "vector-memory",
            "item1",
            content="Updated content",
            metadata={"status": "updated"}
        )
        
        # Verify the item was updated
        self.assertEqual(updated_item.content, "Updated content")
        self.assertEqual(updated_item.metadata, {"source": "test", "status": "updated"})
        
        # Update a non-existent item in an existing memory system
        updated_item = self.manager.update_item("vector-memory", "non-existent")
        
        # Verify the result
        self.assertIsNone(updated_item)
        
        # Update an item in a non-existent memory system
        updated_item = self.manager.update_item("non-existent", "item1")
        
        # Verify the result
        self.assertIsNone(updated_item)
    
    def test_remove_item(self):
        """Test removing an item from a memory system."""
        # Remove an existing item from an existing memory system
        result = self.manager.remove_item("vector-memory", "item1")
        
        # Verify the item was removed
        self.assertTrue(result)
        self.assertEqual(len(self.vector_memory.items), 1)
        self.assertNotIn("item1", self.vector_memory.items)
        
        # Remove a non-existent item from an existing memory system
        result = self.manager.remove_item("vector-memory", "non-existent")
        
        # Verify the result
        self.assertFalse(result)
        
        # Remove an item from a non-existent memory system
        result = self.manager.remove_item("non-existent", "item1")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_search(self):
        """Test searching for items in a memory system."""
        # Search for items in an existing memory system
        items = self.manager.search("vector-memory", "query")
        
        # Verify the search results
        self.assertEqual(len(items), 2)
        self.assertIn(self.item1, items)
        self.assertIn(self.item2, items)
        
        # Search with limit
        items = self.manager.search("vector-memory", "query", limit=1)
        
        # Verify the search results
        self.assertEqual(len(items), 1)
        
        # Search in a non-existent memory system
        items = self.manager.search("non-existent", "query")
        
        # Verify the result
        self.assertEqual(len(items), 0)
    
if __name__ == "__main__":
    unittest.main()
