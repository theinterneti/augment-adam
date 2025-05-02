"""
Unit tests for base.

This module contains unit tests for the base module.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType
from augment_adam.memory.vector.base import *

class TestVectorMemoryItem(unittest.TestCase):
    """Tests for the VectorMemoryItem class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.instance = VectorMemoryItem()

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_to_dict_basic(self):
        """Test basic functionality of to_dict."""
        # Arrange
        expected_result = MagicMock()

        # Act
        result = self.instance.to_dict()

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    def test_from_dict_basic(self):
        """Test basic functionality of from_dict."""
        # Arrange
        data = {"id": "test_id", "content": "test content", "text": "test text"}

        # Act
        result = VectorMemoryItem.from_dict(data)

        # Assert
        self.assertEqual(result.id, "test_id")
        self.assertEqual(result.content, "test content")
        self.assertEqual(result.text, "test text")

    @patch("augment_adam.memory.core.base.MemoryItem.from_dict")
    def test_from_dict_with_mocks(self, mock_from_dict):
        """Test from_dict with mocked dependencies."""
        # Arrange
        mock_item = MagicMock()
        mock_from_dict.return_value = mock_item
        data = {"id": "test_id", "content": "test content", "text": "test text"}

        # Act
        result = VectorMemoryItem.from_dict(data)

        # Assert
        mock_from_dict.assert_called_once_with(data)
        # The result should be the mocked item
        self.assertEqual(result, mock_item)

class TestVectorMemory(unittest.TestCase):
    """Tests for the VectorMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.instance = VectorMemory(name="test_name", dimension=1536)

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test___init___basic(self):
        """Test basic functionality of __init__."""
        # Arrange
        name = "test_name"

        # Act
        instance = VectorMemory(name, dimension=1536)

        # Assert
        self.assertIsInstance(instance, VectorMemory)

    def test_add_basic(self):
        """Test basic functionality of add."""
        # Arrange
        item = MagicMock()
        expected_result = MagicMock()

        # Act
        result = self.instance.add(item)

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    @patch("augment_adam.memory.vector.base.VectorMemory.generate_embedding")
    def test_add_with_mocks(self, mock_generate_embedding):
        """Test add with mocked dependencies."""
        # Arrange
        mock_embedding = [0.1, 0.2, 0.3]
        mock_generate_embedding.return_value = mock_embedding
        item = VectorMemoryItem(content="test content", text="test text")

        # Act
        result = self.instance.add(item)

        # Assert
        # Verify the item was added to the memory
        self.assertIn(item.id, self.instance.items)
        # Verify the embedding was generated
        mock_generate_embedding.assert_called_once_with("test text")
        # Verify the embedding was set on the item
        self.assertEqual(item.embedding, mock_embedding)

    def test_update_basic(self):
        """Test basic functionality of update."""
        # Arrange
        item_id = "test_id"
        expected_result = MagicMock()

        # Act
        result = self.instance.update(item_id, content=None, metadata=None)

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    @patch("augment_adam.memory.vector.base.VectorMemory.generate_embedding")
    def test_update_with_mocks(self, mock_generate_embedding):
        """Test update with mocked dependencies."""
        # Arrange
        mock_embedding = [0.1, 0.2, 0.3]
        mock_generate_embedding.return_value = mock_embedding

        # Add an item to update (with embedding already set to avoid generate_embedding call)
        item = VectorMemoryItem(
            content="original content",
            text="original text",
            embedding=[0.4, 0.5, 0.6]  # Provide embedding to avoid generate_embedding call
        )
        self.instance.items[item.id] = item  # Add directly to items dict to bypass add() method

        # Reset the mock to clear any previous calls
        mock_generate_embedding.reset_mock()

        # Act
        result = self.instance.update(item.id, content="updated content", metadata={"key": "value"})

        # Assert
        # Verify the item was updated
        self.assertEqual(result.content, "updated content")
        self.assertEqual(result.metadata["key"], "value")
        # Verify the text was updated
        self.assertEqual(result.text, "updated content")
        # Verify the embedding was generated
        mock_generate_embedding.assert_called_once_with("updated content")
        # Verify the embedding was set on the item
        self.assertEqual(result.embedding, mock_embedding)

    def test_search_basic(self):
        """Test basic functionality of search."""
        # Arrange
        query = MagicMock()
        expected_result = MagicMock()

        # Act
        result = self.instance.search(query, limit=10)

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    @patch("augment_adam.memory.vector.base.VectorMemory.generate_embedding")
    @patch("augment_adam.memory.vector.base.VectorMemory.calculate_similarity")
    def test_search_with_mocks(self, mock_calculate_similarity, mock_generate_embedding):
        """Test search with mocked dependencies."""
        # Arrange
        mock_embedding = [0.1, 0.2, 0.3]
        mock_generate_embedding.return_value = mock_embedding

        # Set up similarity scores
        mock_calculate_similarity.side_effect = [0.8, 0.6, 0.9]

        # Add some items to search
        item1 = VectorMemoryItem(content="item 1", text="item 1", embedding=[0.4, 0.5, 0.6])
        item2 = VectorMemoryItem(content="item 2", text="item 2", embedding=[0.7, 0.8, 0.9])
        item3 = VectorMemoryItem(content="item 3", text="item 3", embedding=[0.1, 0.2, 0.3])

        self.instance.add(item1)
        self.instance.add(item2)
        self.instance.add(item3)

        # Act
        result = self.instance.search("test query", limit=2)

        # Assert
        # Verify the embedding was generated for the query
        mock_generate_embedding.assert_called_once_with("test query")

        # Verify similarity was calculated for each item
        self.assertEqual(mock_calculate_similarity.call_count, 3)

        # Verify the results are sorted by similarity (highest first)
        # Based on our mock setup, item3 should be first (0.9), then item1 (0.8)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], item3)
        self.assertEqual(result[1], item1)

    def test_generate_embedding_basic(self):
        """Test basic functionality of generate_embedding."""
        # Arrange
        text = MagicMock()
        expected_result = MagicMock()

        # Act
        result = self.instance.generate_embedding(text)

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    def test_generate_embedding_with_mocks(self):
        """Test generate_embedding with real implementation."""
        # Arrange
        text = "test text"

        # Act
        result = self.instance.generate_embedding(text)

        # Assert
        # Verify the result is a list of floats with the correct dimension
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), self.instance.dimension)
        for value in result:
            self.assertIsInstance(value, float)

    def test_calculate_similarity_basic(self):
        """Test basic functionality of calculate_similarity."""
        # Arrange
        embedding1 = MagicMock()
        embedding2 = MagicMock()
        expected_result = MagicMock()

        # Act
        result = self.instance.calculate_similarity(embedding1, embedding2)

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    def test_calculate_similarity_with_mocks(self):
        """Test calculate_similarity with real implementation."""
        # Arrange
        embedding1 = [1.0, 0.0, 0.0]  # Unit vector in x direction
        embedding2 = [0.0, 1.0, 0.0]  # Unit vector in y direction
        embedding3 = [1.0, 0.0, 0.0]  # Same as embedding1
        embedding4 = None  # None embedding

        # Act
        similarity1_2 = self.instance.calculate_similarity(embedding1, embedding2)
        similarity1_3 = self.instance.calculate_similarity(embedding1, embedding3)
        similarity1_4 = self.instance.calculate_similarity(embedding1, embedding4)

        # Assert
        # Orthogonal vectors should have similarity 0
        self.assertEqual(similarity1_2, 0.0)
        # Identical vectors should have similarity 1
        self.assertEqual(similarity1_3, 1.0)
        # None embedding should have similarity 0
        self.assertEqual(similarity1_4, 0.0)

    def test_to_dict_basic(self):
        """Test basic functionality of to_dict."""
        # Arrange
        expected_result = MagicMock()

        # Act
        result = self.instance.to_dict()

        # Assert
        # Verify the result
        # self.assertEqual(expected_result, result)

    def test_from_dict_basic(self):
        """Test basic functionality of from_dict."""
        # Arrange
        data = {
            "name": "test_memory",
            "memory_type": "VECTOR",
            "dimension": 768,
            "items": {
                "item1": {
                    "id": "item1",
                    "content": "test content 1",
                    "text": "test text 1",
                    "embedding": [0.1, 0.2, 0.3]
                },
                "item2": {
                    "id": "item2",
                    "content": "test content 2",
                    "text": "test text 2",
                    "embedding": [0.4, 0.5, 0.6]
                }
            },
            "metadata": {"key": "value"}
        }

        # Act
        result = VectorMemory.from_dict(data)

        # Assert
        self.assertEqual(result.name, "test_memory")
        self.assertEqual(result.memory_type, MemoryType.VECTOR)
        self.assertEqual(result.dimension, 768)
        self.assertEqual(result.metadata["key"], "value")
        self.assertEqual(len(result.items), 2)
        self.assertIn("item1", result.items)
        self.assertIn("item2", result.items)

    @patch("augment_adam.memory.vector.base.VectorMemoryItem.from_dict")
    def test_from_dict_with_mocks(self, mock_from_dict):
        """Test from_dict with mocked dependencies."""
        # Arrange
        mock_item1 = MagicMock()
        mock_item1.id = "item1"
        mock_item2 = MagicMock()
        mock_item2.id = "item2"

        # Set up the mock to return different items for different calls
        mock_from_dict.side_effect = [mock_item1, mock_item2]

        data = {
            "name": "test_memory",
            "memory_type": "VECTOR",
            "dimension": 768,
            "items": {
                "item1": {"id": "item1"},
                "item2": {"id": "item2"}
            },
            "metadata": {"key": "value"}
        }

        # Act
        result = VectorMemory.from_dict(data)

        # Assert
        # Verify the mock was called for each item
        self.assertEqual(mock_from_dict.call_count, 2)

        # Verify the items were added to the memory
        self.assertEqual(len(result.items), 2)
        self.assertIn("item1", result.items)
        self.assertIn("item2", result.items)
        self.assertEqual(result.items["item1"], mock_item1)
        self.assertEqual(result.items["item2"], mock_item2)


if __name__ == '__main__':
    unittest.main()
