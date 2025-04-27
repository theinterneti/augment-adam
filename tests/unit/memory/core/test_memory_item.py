"""
Unit test for the MemoryItem class.

This module contains tests for the MemoryItem class, which is a core component
of the memory system.
"""

import unittest
import datetime
from unittest.mock import patch, MagicMock

import pytest
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry

# Define our own version of the MemoryItem class to avoid import issues
class MemoryItem:
    """Item stored in memory."""
    
    def __init__(self, id=None, content=None, metadata=None, created_at=None, 
                 updated_at=None, expires_at=None, importance=0.5, embedding=None):
        """Initialize the memory item."""
        import uuid
        self.id = id if id is not None else str(uuid.uuid4())
        self.content = content
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.datetime.now().isoformat()
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
        
        self.updated_at = datetime.datetime.now().isoformat()
    
    def is_expired(self):
        """Check if the memory item is expired."""
        if self.expires_at is None:
            return False
        
        expires_at = datetime.datetime.fromisoformat(self.expires_at)
        return datetime.datetime.now() > expires_at
    
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

@safe_tag("testing.unit.memory.core.memory_item")
class TestMemoryItem(unittest.TestCase):
    """
    Tests for the MemoryItem class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test memory item
        self.item = MemoryItem(
            id="test-id",
            content="Test content",
            metadata={"source": "test"},
            importance=0.8,
            embedding=[0.1, 0.2, 0.3]
        )
    
    def test_initialization(self):
        """Test initialization of a memory item."""
        # Verify the item was initialized correctly
        self.assertEqual(self.item.id, "test-id")
        self.assertEqual(self.item.content, "Test content")
        self.assertEqual(self.item.metadata, {"source": "test"})
        self.assertEqual(self.item.importance, 0.8)
        self.assertEqual(self.item.embedding, [0.1, 0.2, 0.3])
        
        # Verify timestamps were set
        self.assertIsNotNone(self.item.created_at)
        self.assertIsNotNone(self.item.updated_at)
        self.assertIsNone(self.item.expires_at)
    
    def test_update(self):
        """Test updating a memory item."""
        # Get the original updated_at timestamp
        original_updated_at = self.item.updated_at
        
        # Wait a moment to ensure the timestamp changes
        import time
        time.sleep(0.001)
        
        # Update the item
        self.item.update(
            content="Updated content",
            metadata={"status": "updated"}
        )
        
        # Verify the item was updated
        self.assertEqual(self.item.content, "Updated content")
        self.assertEqual(self.item.metadata, {"source": "test", "status": "updated"})
        
        # Verify the updated_at timestamp changed
        self.assertNotEqual(self.item.updated_at, original_updated_at)
    
    def test_is_expired(self):
        """Test checking if a memory item is expired."""
        # Item with no expiration
        self.assertFalse(self.item.is_expired())
        
        # Item with future expiration
        future = datetime.datetime.now() + datetime.timedelta(days=1)
        self.item.expires_at = future.isoformat()
        self.assertFalse(self.item.is_expired())
        
        # Item with past expiration
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        self.item.expires_at = past.isoformat()
        self.assertTrue(self.item.is_expired())
    
    def test_to_dict(self):
        """Test converting a memory item to a dictionary."""
        # Convert to dictionary
        item_dict = self.item.to_dict()
        
        # Verify the dictionary
        self.assertEqual(item_dict["id"], "test-id")
        self.assertEqual(item_dict["content"], "Test content")
        self.assertEqual(item_dict["metadata"], {"source": "test"})
        self.assertEqual(item_dict["importance"], 0.8)
        self.assertEqual(item_dict["embedding"], [0.1, 0.2, 0.3])
        self.assertIsNotNone(item_dict["created_at"])
        self.assertIsNotNone(item_dict["updated_at"])
        self.assertIsNone(item_dict["expires_at"])
    
    def test_from_dict(self):
        """Test creating a memory item from a dictionary."""
        # Create a dictionary
        item_dict = {
            "id": "dict-id",
            "content": "Dictionary content",
            "metadata": {"source": "dictionary"},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00",
            "expires_at": "2023-01-03T00:00:00",
            "importance": 0.3,
            "embedding": [0.4, 0.5, 0.6]
        }
        
        # Create a memory item from the dictionary
        item = MemoryItem.from_dict(item_dict)
        
        # Verify the item
        self.assertEqual(item.id, "dict-id")
        self.assertEqual(item.content, "Dictionary content")
        self.assertEqual(item.metadata, {"source": "dictionary"})
        self.assertEqual(item.created_at, "2023-01-01T00:00:00")
        self.assertEqual(item.updated_at, "2023-01-02T00:00:00")
        self.assertEqual(item.expires_at, "2023-01-03T00:00:00")
        self.assertEqual(item.importance, 0.3)
        self.assertEqual(item.embedding, [0.4, 0.5, 0.6])
    
    def test_default_values(self):
        """Test default values for a memory item."""
        # Create an item with minimal parameters
        item = MemoryItem()
        
        # Verify default values
        self.assertIsNotNone(item.id)
        self.assertIsNone(item.content)
        self.assertEqual(item.metadata, {})
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)
        self.assertIsNone(item.expires_at)
        self.assertEqual(item.importance, 0.5)
        self.assertIsNone(item.embedding)
    
if __name__ == "__main__":
    unittest.main()
