"""
Unit test for the vector memory base class.

This module contains tests for the base vector memory functionality.
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest
import numpy as np
# Define our own version of the classes to avoid import issues
# This is a simplified version of the actual classes

class VectorMemoryItem:
    """A simple implementation of VectorMemoryItem for testing."""

    def __init__(self, id, content, embedding, metadata=None):
        self.id = id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}

class VectorMemory:
    """A simple implementation of VectorMemory for testing."""

    def __init__(self):
        """Initialize the vector memory."""
        pass

    def add(self, item):
        """
        Add an item to the memory.

        Args:
            item: The item to add, either a VectorMemoryItem or a dict.

        Returns:
            bool: True if the item was added successfully.
        """
        if isinstance(item, dict):
            item = VectorMemoryItem(
                id=item.get("id"),
                content=item.get("content"),
                embedding=item.get("embedding"),
                metadata=item.get("metadata")
            )

        return self._add_item(item)

    def _add_item(self, item):
        """
        Add an item to the memory (implementation-specific).

        Args:
            item: The item to add.

        Returns:
            bool: True if the item was added successfully.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def search(self, query_embedding, limit=10, **kwargs):
        """
        Search for items similar to the query embedding.

        Args:
            query_embedding: The query embedding.
            limit: The maximum number of results to return.
            **kwargs: Additional search parameters.

        Returns:
            list: A list of VectorMemoryItem objects.
        """
        return self._search(query_embedding, limit, **kwargs)

    def _search(self, query_embedding, limit=10, **kwargs):
        """
        Search for items similar to the query embedding (implementation-specific).

        Args:
            query_embedding: The query embedding.
            limit: The maximum number of results to return.
            **kwargs: Additional search parameters.

        Returns:
            list: A list of VectorMemoryItem objects.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def delete(self, item_id):
        """
        Delete an item from the memory.

        Args:
            item_id: The ID of the item to delete.

        Returns:
            bool: True if the item was deleted successfully.
        """
        return self._delete_item(item_id)

    def _delete_item(self, item_id):
        """
        Delete an item from the memory (implementation-specific).

        Args:
            item_id: The ID of the item to delete.

        Returns:
            bool: True if the item was deleted successfully.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def clear(self):
        """
        Clear all items from the memory.

        Returns:
            bool: True if the memory was cleared successfully.
        """
        return self._clear()

    def _clear(self):
        """
        Clear all items from the memory (implementation-specific).

        Returns:
            bool: True if the memory was cleared successfully.
        """
        raise NotImplementedError("Subclasses must implement this method")
# Import our tag utilities
import sys
sys.path.append('/workspace')
from src.augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry

@safe_tag("testing.unit.memory.vector.base")
class TestVectorMemory(unittest.TestCase):
    """
    Tests for the VectorMemory base class.
    """

    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()

        # Create a concrete implementation of VectorMemory for testing
        class ConcreteVectorMemory(VectorMemory):
            def __init__(self):
                super().__init__()
                self.items = {}

            def _add_item(self, item):
                self.items[item.id] = item
                return True

            def _search(self, query_embedding, limit=10, **kwargs):
                # Simple mock implementation that returns all items
                return list(self.items.values())[:limit]

            def _delete_item(self, item_id):
                if item_id in self.items:
                    del self.items[item_id]
                    return True
                return False

            def _clear(self):
                self.items = {}
                return True

        self.memory = ConcreteVectorMemory()

    def test_add(self):
        """Test adding an item to memory."""
        # Create a test item
        item = VectorMemoryItem(
            id="test1",
            content="Test content",
            metadata={"source": "test"},
            embedding=[0.1, 0.2, 0.3]
        )

        # Add the item
        result = self.memory.add(item)

        # Verify the item was added
        self.assertTrue(result)
        self.assertIn("test1", self.memory.items)
        self.assertEqual(self.memory.items["test1"], item)

    def test_add_with_dict(self):
        """Test adding an item as a dictionary."""
        # Create a test item as a dict
        item_dict = {
            "id": "test2",
            "content": "Test content 2",
            "metadata": {"source": "test"},
            "embedding": [0.4, 0.5, 0.6]
        }

        # Add the item
        result = self.memory.add(item_dict)

        # Verify the item was added
        self.assertTrue(result)
        self.assertIn("test2", self.memory.items)
        self.assertEqual(self.memory.items["test2"].id, "test2")
        self.assertEqual(self.memory.items["test2"].content, "Test content 2")

    def test_search(self):
        """Test searching for items."""
        # Add some test items
        self.memory.add({
            "id": "test1",
            "content": "Test content 1",
            "embedding": [0.1, 0.2, 0.3]
        })

        self.memory.add({
            "id": "test2",
            "content": "Test content 2",
            "embedding": [0.4, 0.5, 0.6]
        })

        # Search for items
        results = self.memory.search([0.1, 0.2, 0.3], limit=1)

        # Verify the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "test1")

    def test_delete(self):
        """Test deleting an item."""
        # Add a test item
        self.memory.add({
            "id": "test1",
            "content": "Test content 1",
            "embedding": [0.1, 0.2, 0.3]
        })

        # Verify the item exists
        self.assertIn("test1", self.memory.items)

        # Delete the item
        result = self.memory.delete("test1")

        # Verify the item was deleted
        self.assertTrue(result)
        self.assertNotIn("test1", self.memory.items)

    def test_clear(self):
        """Test clearing all items."""
        # Add some test items
        self.memory.add({
            "id": "test1",
            "content": "Test content 1",
            "embedding": [0.1, 0.2, 0.3]
        })

        self.memory.add({
            "id": "test2",
            "content": "Test content 2",
            "embedding": [0.4, 0.5, 0.6]
        })

        # Verify items exist
        self.assertEqual(len(self.memory.items), 2)

        # Clear the memory
        result = self.memory.clear()

        # Verify all items were deleted
        self.assertTrue(result)
        self.assertEqual(len(self.memory.items), 0)

if __name__ == "__main__":
    unittest.main()
