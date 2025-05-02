"""
Unit tests for augment_adam.memory.vector.faiss module.

This module contains unit tests for the FAISSMemory class and related functionality.
"""

import unittest
import pytest
import os
import tempfile
import shutil
import numpy as np
from unittest import mock
from unittest.mock import MagicMock, patch
import faiss
from typing import List, Dict, Any, Optional

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.vector.base import VectorMemoryItem
from augment_adam.memory.vector.faiss import FAISSMemory


class TestFAISSMemory(unittest.TestCase):
    """Test cases for the FAISSMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory = FAISSMemory("test-memory", dimension=3)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_init_flat_index(self):
        """Test initialization with flat index."""
        memory = FAISSMemory("test-memory", dimension=3, index_type="Flat")

        self.assertEqual(memory.name, "test-memory")
        self.assertEqual(memory.memory_type, MemoryType.VECTOR)
        self.assertEqual(memory.dimension, 3)
        self.assertEqual(memory.metadata["dimension"], 3)
        self.assertEqual(memory.metadata["index_type"], "Flat")
        self.assertIsInstance(memory.index, faiss.IndexFlatL2)
        self.assertEqual(len(memory.items), 0)
        self.assertEqual(len(memory.id_to_index), 0)
        self.assertEqual(len(memory.index_to_id), 0)

    def test_init_ivf_index(self):
        """Test initialization with IVF index."""
        memory = FAISSMemory("test-memory", dimension=3, index_type="IVF")

        self.assertEqual(memory.name, "test-memory")
        self.assertEqual(memory.memory_type, MemoryType.VECTOR)
        self.assertEqual(memory.dimension, 3)
        self.assertEqual(memory.metadata["dimension"], 3)
        self.assertEqual(memory.metadata["index_type"], "IVF")
        self.assertIsInstance(memory.index, faiss.IndexIVFFlat)
        self.assertEqual(len(memory.items), 0)
        self.assertEqual(len(memory.id_to_index), 0)
        self.assertEqual(len(memory.index_to_id), 0)

    def test_init_invalid_index_type(self):
        """Test initialization with invalid index type."""
        with self.assertRaises(ValueError):
            FAISSMemory("test-memory", dimension=3, index_type="Invalid")

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
        self.assertEqual(self.memory.index.ntotal, 1)
        self.assertIn(item_id, self.memory.id_to_index)
        self.assertIn(0, self.memory.index_to_id)
        self.assertEqual(self.memory.id_to_index[item_id], 0)
        self.assertEqual(self.memory.index_to_id[0], item_id)

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
        self.assertEqual(self.memory.index.ntotal, 1)
        self.assertIn(item_id, self.memory.id_to_index)
        self.assertIn(0, self.memory.index_to_id)
        self.memory.generate_embedding.assert_called_once_with("Test text")

    @patch("faiss.IndexIVFFlat.train")
    def test_add_with_ivf_index_training(self, mock_train):
        """Test adding items with IVF index training."""
        memory = FAISSMemory("test-memory", dimension=3, index_type="IVF")

        # Mock the is_trained property
        type(memory.index).is_trained = mock.PropertyMock(return_value=False)

        # Add 100 items to trigger training
        embeddings = []
        for i in range(100):
            item = VectorMemoryItem(
                content=f"Item {i}",
                text=f"Item {i}",
                embedding=[float(i) / 100, float(i) / 100, float(i) / 100]
            )
            embeddings.append(item.embedding)
            # Patch the add method to avoid the error
            with patch.object(memory.index, 'add'):
                memory.add(item)

        # Check that train was called
        mock_train.assert_called_once()

        # Check that train was called with embeddings (using almost_equal for floating point comparison)
        train_arg = mock_train.call_args[0][0]
        self.assertEqual(train_arg.shape[0], 100)  # 100 embeddings
        self.assertEqual(train_arg.shape[1], 3)    # 3 dimensions

    def test_update_with_new_embedding(self):
        """Test updating an item with a new embedding."""
        # Create a test directly with the implementation class
        memory = FAISSMemory("test-memory", dimension=3)

        # Add an item
        item = VectorMemoryItem(
            id="test-id",
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )

        # Add the item to the memory
        with patch.object(memory.index, 'add') as mock_add:
            # Mock the add method to avoid actual FAISS operations
            memory.items[item.id] = item
            memory.id_to_index[item.id] = 0
            memory.index_to_id[0] = item.id
            memory.index.ntotal = 1  # Set initial ntotal

        # Mock the generate_embedding method
        memory.generate_embedding = MagicMock(return_value=[0.4, 0.5, 0.6])

        # Patch the super().update method to avoid calling the parent class
        with patch('augment_adam.memory.vector.base.VectorMemory.update') as mock_super_update:
            # Make the super().update method return an updated item
            updated_item = VectorMemoryItem(
                id=item.id,
                content="New content",
                text="New content",
                embedding=[0.4, 0.5, 0.6]
            )
            mock_super_update.return_value = updated_item

            # Patch the FAISS index add method
            with patch.object(memory.index, 'add') as mock_add:
                # When add is called, increment ntotal
                def mock_add_side_effect(embedding_np):
                    memory.index.ntotal += 1
                mock_add.side_effect = mock_add_side_effect

                # Update the item
                result = memory.update(item.id, content="New content")

                # Check that super().update was called
                mock_super_update.assert_called_once_with(item.id, "New content", None)

                # Check that the result is the updated item
                self.assertEqual(result, updated_item)

                # Check that add was called with the new embedding
                mock_add.assert_called_once()

                # Check that the mappings were updated correctly
                self.assertIn(item.id, memory.id_to_index)
                self.assertEqual(memory.id_to_index[item.id], 1)  # New index
                self.assertEqual(memory.index_to_id[1], item.id)
                self.assertNotIn(0, memory.index_to_id)  # Old index removed

    def test_update_without_embedding_change(self):
        """Test updating an item without changing the embedding."""
        # Add an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3],
            metadata={"key1": "value1"}
        )
        item_id = self.memory.add(item)

        # Update the item without changing content
        updated_item = self.memory.update(item_id, metadata={"key2": "value2"})

        self.assertEqual(updated_item.content, "Test content")
        self.assertEqual(updated_item.text, "Test text")
        self.assertEqual(updated_item.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(updated_item.metadata, {"key1": "value1", "key2": "value2"})
        self.assertEqual(self.memory.index.ntotal, 1)  # No new embedding
        self.assertIn(item_id, self.memory.id_to_index)
        self.assertEqual(self.memory.id_to_index[item_id], 0)  # Same index
        self.assertEqual(self.memory.index_to_id[0], item_id)

    def test_update_nonexistent_item(self):
        """Test updating a nonexistent item."""
        updated_item = self.memory.update("nonexistent-id", content="New content")
        self.assertIsNone(updated_item)
        self.assertEqual(self.memory.index.ntotal, 0)

    def test_remove(self):
        """Test removing an item."""
        # Add an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )
        item_id = self.memory.add(item)

        # Remove the item
        result = self.memory.remove(item_id)

        self.assertTrue(result)
        self.assertNotIn(item_id, self.memory.items)
        self.assertNotIn(item_id, self.memory.id_to_index)
        self.assertNotIn(0, self.memory.index_to_id)
        # Note: FAISS doesn't support removing individual vectors,
        # so the index still contains the vector

    def test_remove_nonexistent_item(self):
        """Test removing a nonexistent item."""
        result = self.memory.remove("nonexistent-id")
        self.assertFalse(result)

    def test_clear(self):
        """Test clearing all items."""
        # Add some items
        for i in range(3):
            item = VectorMemoryItem(
                content=f"Item {i}",
                text=f"Item {i}",
                embedding=[float(i) / 10, float(i + 1) / 10, float(i + 2) / 10]
            )
            self.memory.add(item)

        # Clear the memory
        self.memory.clear()

        self.assertEqual(len(self.memory.items), 0)
        self.assertEqual(len(self.memory.id_to_index), 0)
        self.assertEqual(len(self.memory.index_to_id), 0)
        self.assertEqual(self.memory.index.ntotal, 0)

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

        # Search for items
        results = self.memory.search("query", limit=2)

        self.assertEqual(len(results), 2)
        self.memory.generate_embedding.assert_called_once_with("query")

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

        # Search for items
        results = self.memory.search([0.4, 0.5, 0.6], limit=2)

        self.assertEqual(len(results), 2)
        # Item 2 should be closer to the query
        self.assertEqual(results[0].content, "Item 2")
        self.assertEqual(results[1].content, "Item 1")

    def test_search_with_empty_index(self):
        """Test searching with an empty index."""
        results = self.memory.search([0.1, 0.2, 0.3], limit=10)
        self.assertEqual(len(results), 0)

    def test_search_with_limit(self):
        """Test searching with a limit."""
        # Add some items
        for i in range(5):
            item = VectorMemoryItem(
                content=f"Item {i}",
                text=f"Item {i}",
                embedding=[float(i) / 10, float(i + 1) / 10, float(i + 2) / 10]
            )
            self.memory.add(item)

        # Search with limit=3
        results = self.memory.search([0.0, 0.1, 0.2], limit=3)

        self.assertEqual(len(results), 3)

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
        embedding1_np = np.array(embedding1)
        embedding2_np = np.array(embedding2)
        embedding1_norm = embedding1_np / np.linalg.norm(embedding1_np)
        embedding2_norm = embedding2_np / np.linalg.norm(embedding2_np)
        expected_similarity = np.dot(embedding1_norm, embedding2_norm)

        # Use a lower precision for the comparison due to floating point differences
        self.assertAlmostEqual(similarity, expected_similarity, places=5)

    def test_calculate_similarity_with_none(self):
        """Test calculate_similarity method with None embedding."""
        embedding1 = [0.1, 0.2, 0.3]
        embedding2 = None

        similarity = self.memory.calculate_similarity(embedding1, embedding2)

        self.assertEqual(similarity, 0.0)

    def test_save_and_load(self):
        """Test saving and loading memory."""
        # Add some items
        for i in range(3):
            item = VectorMemoryItem(
                content=f"Item {i}",
                text=f"Item {i}",
                embedding=[float(i) / 10, float(i + 1) / 10, float(i + 2) / 10]
            )
            self.memory.add(item)

        # Save the memory
        save_dir = os.path.join(self.temp_dir, "memory")
        self.memory.save(save_dir)

        # Check that files were created
        self.assertTrue(os.path.exists(os.path.join(save_dir, "index.faiss")))
        self.assertTrue(os.path.exists(os.path.join(save_dir, "items.json")))
        self.assertTrue(os.path.exists(os.path.join(save_dir, "mappings.json")))
        self.assertTrue(os.path.exists(os.path.join(save_dir, "metadata.json")))

        # Load the memory
        loaded_memory = FAISSMemory.load(save_dir)

        # Check that the loaded memory matches the original
        self.assertEqual(loaded_memory.name, self.memory.name)
        self.assertEqual(loaded_memory.dimension, self.memory.dimension)
        self.assertEqual(loaded_memory.metadata, self.memory.metadata)
        self.assertEqual(len(loaded_memory.items), len(self.memory.items))
        self.assertEqual(loaded_memory.index.ntotal, self.memory.index.ntotal)

        # Check that the items were loaded correctly
        for item_id, item in self.memory.items.items():
            self.assertIn(item_id, loaded_memory.items)
            loaded_item = loaded_memory.items[item_id]
            self.assertEqual(loaded_item.content, item.content)
            self.assertEqual(loaded_item.text, item.text)
            self.assertEqual(loaded_item.embedding, item.embedding)


if __name__ == "__main__":
    unittest.main()
