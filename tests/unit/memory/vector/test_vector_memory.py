"""
Unit tests for augment_adam.memory.vector.base module.

This module contains unit tests for the VectorMemory class and related functionality.
"""

import unittest
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from typing import List, Dict, Any, Optional

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.vector.base import VectorMemory, VectorMemoryItem


class TestVectorMemoryItem(unittest.TestCase):
    """Test cases for the VectorMemoryItem class."""

    def test_init_with_text(self):
        """Test initialization with text."""
        item = VectorMemoryItem(content="Test content", text="Test text")
        self.assertEqual(item.content, "Test content")
        self.assertEqual(item.text, "Test text")

    def test_init_without_text(self):
        """Test initialization without text but with string content."""
        item = VectorMemoryItem(content="Test content")
        self.assertEqual(item.text, "Test content")

    def test_init_with_non_string_content(self):
        """Test initialization with non-string content."""
        content = {"key": "value"}
        item = VectorMemoryItem(content=content)
        self.assertEqual(item.content, content)
        self.assertIsNone(item.text)

    def test_to_dict(self):
        """Test to_dict method."""
        item = VectorMemoryItem(content="Test content", text="Test text")
        item_dict = item.to_dict()

        self.assertEqual(item_dict["content"], "Test content")
        self.assertEqual(item_dict["text"], "Test text")
        self.assertIn("id", item_dict)
        self.assertIn("created_at", item_dict)
        self.assertIn("updated_at", item_dict)

    def test_from_dict(self):
        """Test from_dict method."""
        item_dict = {
            "id": "test-id",
            "content": "Test content",
            "text": "Test text",
            "metadata": {"key": "value"},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "importance": 0.8,
            "embedding": [0.1, 0.2, 0.3]
        }

        item = VectorMemoryItem.from_dict(item_dict)

        self.assertEqual(item.id, "test-id")
        self.assertEqual(item.content, "Test content")
        self.assertEqual(item.text, "Test text")
        self.assertEqual(item.metadata, {"key": "value"})
        self.assertEqual(item.created_at, "2023-01-01T00:00:00")
        self.assertEqual(item.updated_at, "2023-01-01T00:00:00")
        self.assertEqual(item.importance, 0.8)
        self.assertEqual(item.embedding, [0.1, 0.2, 0.3])


class TestVectorMemory(unittest.TestCase):
    """Test cases for the VectorMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory = VectorMemory("test-memory", dimension=3)

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.memory.name, "test-memory")
        self.assertEqual(self.memory.memory_type, MemoryType.VECTOR)
        self.assertEqual(self.memory.dimension, 3)
        self.assertEqual(self.memory.metadata["dimension"], 3)
        self.assertEqual(len(self.memory.items), 0)

    def test_add_with_embedding(self):
        """Test adding an item with an embedding."""
        item = VectorMemoryItem(
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )

        item_id = self.memory.add(item)

        self.assertEqual(item_id, item.id)
        self.assertIn(item_id, self.memory.items)
        self.assertEqual(self.memory.items[item_id], item)

    def test_add_without_embedding(self):
        """Test adding an item without an embedding."""
        # Mock the generate_embedding method
        self.memory.generate_embedding = MagicMock(return_value=[0.1, 0.2, 0.3])

        item = VectorMemoryItem(
            content="Test content",
            text="Test text"
        )

        item_id = self.memory.add(item)

        self.assertEqual(item_id, item.id)
        self.assertIn(item_id, self.memory.items)
        self.assertEqual(self.memory.items[item_id], item)
        self.assertEqual(item.embedding, [0.1, 0.2, 0.3])
        self.memory.generate_embedding.assert_called_once_with("Test text")

    def test_update_with_content(self):
        """Test updating an item with new content."""
        # Mock the generate_embedding method
        self.memory.generate_embedding = MagicMock(return_value=[0.4, 0.5, 0.6])

        # Add an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )
        item_id = self.memory.add(item)

        # Update the item
        updated_item = self.memory.update(item_id, content="New content")

        self.assertEqual(updated_item.content, "New content")
        self.assertEqual(updated_item.text, "New content")
        self.assertEqual(updated_item.embedding, [0.4, 0.5, 0.6])
        self.memory.generate_embedding.assert_called_once_with("New content")

    def test_update_with_metadata(self):
        """Test updating an item with new metadata."""
        # Add an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3],
            metadata={"key1": "value1"}
        )
        item_id = self.memory.add(item)

        # Update the item
        updated_item = self.memory.update(item_id, metadata={"key2": "value2"})

        self.assertEqual(updated_item.content, "Test content")
        self.assertEqual(updated_item.text, "Test text")
        self.assertEqual(updated_item.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(updated_item.metadata, {"key1": "value1", "key2": "value2"})

    def test_update_nonexistent_item(self):
        """Test updating a nonexistent item."""
        updated_item = self.memory.update("nonexistent-id", content="New content")
        self.assertIsNone(updated_item)

    def test_search_with_string_query(self):
        """Test searching with a string query."""
        # Mock the generate_embedding method
        self.memory.generate_embedding = MagicMock(return_value=[0.1, 0.2, 0.3])

        # Add some items
        item1 = VectorMemoryItem(
            content="Item 1",
            text="Item 1",
            embedding=[0.1, 0.2, 0.3]
        )
        item2 = VectorMemoryItem(
            content="Item 2",
            text="Item 2",
            embedding=[0.4, 0.5, 0.6]
        )
        self.memory.add(item1)
        self.memory.add(item2)

        # Mock the calculate_similarity method
        self.memory.calculate_similarity = MagicMock(side_effect=[0.9, 0.5])

        # Search for items
        results = self.memory.search("query", limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], item1)  # Higher similarity
        self.assertEqual(results[1], item2)  # Lower similarity

        self.memory.generate_embedding.assert_called_once_with("query")
        self.assertEqual(self.memory.calculate_similarity.call_count, 2)

    def test_search_with_vector_query(self):
        """Test searching with a vector query."""
        # Add some items
        item1 = VectorMemoryItem(
            content="Item 1",
            text="Item 1",
            embedding=[0.1, 0.2, 0.3]
        )
        item2 = VectorMemoryItem(
            content="Item 2",
            text="Item 2",
            embedding=[0.4, 0.5, 0.6]
        )
        self.memory.add(item1)
        self.memory.add(item2)

        # Mock the calculate_similarity method
        self.memory.calculate_similarity = MagicMock(side_effect=[0.5, 0.9])

        # Search for items
        results = self.memory.search([0.4, 0.5, 0.6], limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], item2)  # Higher similarity
        self.assertEqual(results[1], item1)  # Lower similarity

        self.assertEqual(self.memory.calculate_similarity.call_count, 2)

    def test_search_with_limit(self):
        """Test searching with a limit."""
        # Add some items
        item1 = VectorMemoryItem(
            content="Item 1",
            text="Item 1",
            embedding=[0.1, 0.2, 0.3]
        )
        item2 = VectorMemoryItem(
            content="Item 2",
            text="Item 2",
            embedding=[0.4, 0.5, 0.6]
        )
        item3 = VectorMemoryItem(
            content="Item 3",
            text="Item 3",
            embedding=[0.7, 0.8, 0.9]
        )
        self.memory.add(item1)
        self.memory.add(item2)
        self.memory.add(item3)

        # Mock the calculate_similarity method
        self.memory.calculate_similarity = MagicMock(side_effect=[0.5, 0.9, 0.7])

        # Search for items with limit=2
        results = self.memory.search([0.4, 0.5, 0.6], limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], item2)  # Highest similarity
        self.assertEqual(results[1], item3)  # Second highest similarity

        self.assertEqual(self.memory.calculate_similarity.call_count, 3)

    def test_generate_embedding(self):
        """Test generate_embedding method."""
        embedding = self.memory.generate_embedding("Test text")

        self.assertEqual(len(embedding), 3)  # Dimension is 3
        self.assertIsInstance(embedding, list)
        self.assertIsInstance(embedding[0], float)

    def test_calculate_similarity(self):
        """Test calculate_similarity method."""
        embedding1 = [0.1, 0.2, 0.3]
        embedding2 = [0.4, 0.5, 0.6]

        similarity = self.memory.calculate_similarity(embedding1, embedding2)

        # Calculate expected cosine similarity
        dot_product = 0.1 * 0.4 + 0.2 * 0.5 + 0.3 * 0.6
        magnitude1 = (0.1**2 + 0.2**2 + 0.3**2) ** 0.5
        magnitude2 = (0.4**2 + 0.5**2 + 0.6**2) ** 0.5
        expected_similarity = dot_product / (magnitude1 * magnitude2)

        self.assertAlmostEqual(similarity, expected_similarity)

    def test_calculate_similarity_with_none(self):
        """Test calculate_similarity method with None embedding."""
        embedding1 = [0.1, 0.2, 0.3]
        embedding2 = None

        similarity = self.memory.calculate_similarity(embedding1, embedding2)

        self.assertEqual(similarity, 0.0)

    def test_calculate_similarity_with_zero_magnitude(self):
        """Test calculate_similarity method with zero magnitude."""
        embedding1 = [0.0, 0.0, 0.0]
        embedding2 = [0.4, 0.5, 0.6]

        similarity = self.memory.calculate_similarity(embedding1, embedding2)

        self.assertEqual(similarity, 0.0)

    def test_to_dict(self):
        """Test to_dict method."""
        # Add an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )
        self.memory.add(item)

        memory_dict = self.memory.to_dict()

        self.assertEqual(memory_dict["name"], "test-memory")
        self.assertEqual(memory_dict["memory_type"], "VECTOR")
        self.assertEqual(memory_dict["dimension"], 3)
        self.assertIn(item.id, memory_dict["items"])
        self.assertEqual(memory_dict["items"][item.id]["content"], "Test content")

    def test_from_dict(self):
        """Test from_dict method."""
        memory_dict = {
            "name": "test-memory",
            "memory_type": "VECTOR",
            "dimension": 3,
            "items": {
                "test-id": {
                    "id": "test-id",
                    "content": "Test content",
                    "text": "Test text",
                    "metadata": {"key": "value"},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "importance": 0.8,
                    "embedding": [0.1, 0.2, 0.3]
                }
            },
            "metadata": {"key": "value"}
        }

        memory = VectorMemory.from_dict(memory_dict)

        self.assertEqual(memory.name, "test-memory")
        self.assertEqual(memory.dimension, 3)
        # Check that the metadata was loaded correctly
        self.assertEqual(memory.metadata["key"], "value")
        # Note: The dimension is not added to metadata in from_dict method
        self.assertEqual(len(memory.items), 1)
        self.assertIn("test-id", memory.items)
        self.assertEqual(memory.items["test-id"].content, "Test content")
        self.assertEqual(memory.items["test-id"].text, "Test text")
        self.assertEqual(memory.items["test-id"].embedding, [0.1, 0.2, 0.3])


if __name__ == "__main__":
    unittest.main()
