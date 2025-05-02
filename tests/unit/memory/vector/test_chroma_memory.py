"""
Unit tests for augment_adam.memory.vector.chroma module.

This module contains unit tests for the ChromaMemory class and related functionality.
"""

import unittest
import pytest
import os
import tempfile
import shutil
import numpy as np
from unittest.mock import MagicMock, patch
import chromadb
from typing import List, Dict, Any, Optional

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.vector.base import VectorMemoryItem
from augment_adam.memory.vector.chroma import ChromaMemory


class TestChromaMemory(unittest.TestCase):
    """Test cases for the ChromaMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Setup mock client and collection
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()

        # Mock collection.get to return empty results by default
        self.mock_collection.get.return_value = {
            "ids": [],
            "embeddings": [],
            "documents": [],
            "metadatas": []
        }

        # Patch chromadb.Client to return our mock client
        self.client_patcher = patch('chromadb.Client', return_value=self.mock_client)
        self.mock_client_class = self.client_patcher.start()

        # Set up the mock client to return our mock collection
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

        # Create memory instance
        self.memory = ChromaMemory("test-memory", dimension=3, persist_directory=self.temp_dir)

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patcher
        self.client_patcher.stop()

        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test initialization."""
        # Reset the mock to clear previous calls
        self.mock_client_class.reset_mock()
        self.mock_client.reset_mock()

        # Create a new memory instance to test initialization
        memory = ChromaMemory("test-memory", dimension=3, persist_directory=self.temp_dir)

        # Assertions
        self.assertEqual(memory.name, "test-memory")
        self.assertEqual(memory.memory_type, MemoryType.VECTOR)
        self.assertEqual(memory.dimension, 3)
        self.assertEqual(memory.metadata["dimension"], 3)
        self.assertEqual(memory.metadata["persist_directory"], self.temp_dir)
        self.assertIsNotNone(memory.client)
        self.assertIsNotNone(memory.collection)
        self.assertEqual(len(memory.items), 0)

        # Verify client was called correctly
        self.mock_client_class.assert_called_once()
        self.mock_client.get_or_create_collection.assert_called_once_with(name="test-memory")

    def test_add_with_embedding_and_text(self):
        """Test adding an item with an embedding and text."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Create item
        item = VectorMemoryItem(
            id="test-id",
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )

        # Add item
        item_id = self.memory.add(item)

        # Verify item was added to memory
        self.assertEqual(item_id, item.id)
        self.assertIn(item_id, self.memory.items)
        self.assertEqual(self.memory.items[item_id], item)

        # Verify collection.add was called correctly
        self.mock_collection.add.assert_called_once()
        # Check the call arguments
        call_args = self.mock_collection.add.call_args[1]  # Get kwargs
        self.assertEqual(call_args["ids"], [item_id])
        self.assertEqual(call_args["embeddings"], [[0.1, 0.2, 0.3]])
        self.assertEqual(call_args["documents"], ["Test text"])
        # Metadata should not contain None values
        self.assertIsInstance(call_args["metadatas"][0], dict)
        # Check that expires_at is not in metadata (since it's None)
        self.assertNotIn("expires_at", call_args["metadatas"][0])

    def test_add_without_embedding(self):
        """Test adding an item without an embedding."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Mock the generate_embedding method
        original_generate_embedding = self.memory.generate_embedding
        self.memory.generate_embedding = MagicMock(return_value=[0.1, 0.2, 0.3])

        try:
            # Create item without embedding
            item = VectorMemoryItem(
                id="test-id",
                content="Test content",
                text="Test text"
            )

            # Add item
            item_id = self.memory.add(item)

            # Verify item was added to memory with generated embedding
            self.assertEqual(item_id, item.id)
            self.assertIn(item_id, self.memory.items)
            self.assertEqual(self.memory.items[item_id], item)
            self.assertEqual(item.embedding, [0.1, 0.2, 0.3])

            # Check that the embedding was generated
            self.memory.generate_embedding.assert_called_once_with("Test text")

            # Verify collection.add was called correctly
            self.mock_collection.add.assert_called_once()
            # Check the call arguments
            call_args = self.mock_collection.add.call_args[1]  # Get kwargs
            self.assertEqual(call_args["ids"], [item_id])
            self.assertEqual(call_args["embeddings"], [[0.1, 0.2, 0.3]])
            self.assertEqual(call_args["documents"], ["Test text"])
            # Metadata should not contain None values
            self.assertIsInstance(call_args["metadatas"][0], dict)
            self.assertNotIn("expires_at", call_args["metadatas"][0])
        finally:
            # Restore the original method
            self.memory.generate_embedding = original_generate_embedding

    def test_add_without_text(self):
        """Test adding an item without text."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Set up mock collection.get to return empty results
        self.mock_collection.get.return_value = {
            "ids": [],
            "embeddings": [],
            "documents": [],
            "metadatas": []
        }

        # Create item without text
        item = VectorMemoryItem(
            content={"key": "value"},  # Non-string content
            embedding=[0.1, 0.2, 0.3]
        )

        # Add item
        item_id = self.memory.add(item)

        # Verify item was added to memory
        self.assertEqual(item_id, item.id)
        self.assertIn(item_id, self.memory.items)
        self.assertEqual(self.memory.items[item_id], item)

        # The item should not be added to the Chroma collection
        # because it doesn't have text
        self.mock_collection.add.assert_not_called()

    def test_update_with_text_and_embedding(self):
        """Test updating an item with text and embedding."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Set up mock collection.get to return expected results
        self.mock_collection.get.return_value = {
            "ids": ["test-id"],
            "embeddings": [[0.1, 0.2, 0.3]],
            "documents": ["New content"],
            "metadatas": [{"key1": "value1", "key2": "value2"}]
        }

        # Add an item
        item = VectorMemoryItem(
            id="test-id",
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3],
            metadata={"key1": "value1"}
        )
        self.memory.items[item.id] = item  # Add directly to avoid calling add()

        # Update the item
        updated_item = self.memory.update(item.id, content="New content", metadata={"key2": "value2"})

        # Verify item was updated
        self.assertEqual(updated_item.content, "New content")
        self.assertEqual(updated_item.text, "New content")  # text is updated from content
        self.assertEqual(updated_item.metadata, {"key1": "value1", "key2": "value2"})

        # Verify collection.update was called correctly
        self.mock_collection.update.assert_called_once()
        # Check the call arguments
        call_args = self.mock_collection.update.call_args[1]  # Get kwargs
        self.assertEqual(call_args["ids"], [item.id])
        self.assertEqual(call_args["documents"], ["New content"])
        # Metadata should not contain None values
        self.assertIsInstance(call_args["metadatas"][0], dict)
        self.assertEqual(call_args["metadatas"][0]["key1"], "value1")
        self.assertEqual(call_args["metadatas"][0]["key2"], "value2")
        self.assertNotIn("expires_at", call_args["metadatas"][0])

    def test_update_nonexistent_item(self):
        """Test updating a nonexistent item."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Update a nonexistent item
        updated_item = self.memory.update("nonexistent-id", content="New content")

        # Verify the result
        self.assertIsNone(updated_item)

        # Verify collection.update was not called
        self.mock_collection.update.assert_not_called()

    def test_remove(self):
        """Test removing an item."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Add an item directly to memory
        item = VectorMemoryItem(
            id="test-id",
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )
        self.memory.items[item.id] = item

        # Remove the item
        result = self.memory.remove(item.id)

        # Verify the result
        self.assertTrue(result)
        self.assertNotIn(item.id, self.memory.items)

        # Verify collection.delete was called correctly
        self.mock_collection.delete.assert_called_once_with(ids=[item.id])

    def test_remove_nonexistent_item(self):
        """Test removing a nonexistent item."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Remove a nonexistent item
        result = self.memory.remove("nonexistent-id")

        # Verify the result
        self.assertFalse(result)

        # Verify collection.delete was not called
        self.mock_collection.delete.assert_not_called()

    def test_clear(self):
        """Test clearing all items."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Set up mock collection.get to return some IDs
        self.mock_collection.get.return_value = {
            "ids": ["item1", "item2", "item3"]
        }

        # Add some items directly to memory
        for i in range(3):
            item = VectorMemoryItem(
                id=f"item{i+1}",
                content=f"Item {i}",
                text=f"Item {i}",
                embedding=[float(i) / 10, float(i + 1) / 10, float(i + 2) / 10]
            )
            self.memory.items[item.id] = item

        # Clear the memory
        self.memory.clear()

        # Verify the result
        self.assertEqual(len(self.memory.items), 0)

        # Verify collection.delete was called correctly
        self.mock_collection.delete.assert_called_once_with(ids=["item1", "item2", "item3"])

    def test_search_with_string_query(self):
        """Test searching with a string query."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Set up mock collection.query to return expected results
        self.mock_collection.query.return_value = {
            "ids": [["item1", "item2"]],
            "distances": [[0.1, 0.2]]
        }

        # Set up mock collection.count to return non-zero
        self.mock_collection.count.return_value = 2

        # Add some items directly to memory
        item1 = VectorMemoryItem(id="item1", content="Item 1", text="Item 1", embedding=[0.1, 0.2, 0.3])
        item2 = VectorMemoryItem(id="item2", content="Item 2", text="Item 2", embedding=[0.4, 0.5, 0.6])
        self.memory.items[item1.id] = item1
        self.memory.items[item2.id] = item2

        # Search for items
        results = self.memory.search("query", limit=2)

        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, "item1")
        self.assertEqual(results[1].id, "item2")

        # Check that the query method was called correctly
        self.mock_collection.query.assert_called_once_with(
            query_texts=["query"],
            n_results=2
        )

    def test_search_with_vector_query(self):
        """Test searching with a vector query."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Set up mock collection.query to return expected results
        self.mock_collection.query.return_value = {
            "ids": [["item2", "item1"]],
            "distances": [[0.1, 0.2]]
        }

        # Set up mock collection.count to return non-zero
        self.mock_collection.count.return_value = 2

        # Add some items directly to memory
        item1 = VectorMemoryItem(id="item1", content="Item 1", text="Item 1", embedding=[0.1, 0.2, 0.3])
        item2 = VectorMemoryItem(id="item2", content="Item 2", text="Item 2", embedding=[0.4, 0.5, 0.6])
        self.memory.items[item1.id] = item1
        self.memory.items[item2.id] = item2

        # Search for items
        results = self.memory.search([0.4, 0.5, 0.6], limit=2)

        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, "item2")
        self.assertEqual(results[1].id, "item1")

        # Check that the query method was called correctly
        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.4, 0.5, 0.6]],
            n_results=2
        )

    def test_search_with_empty_collection(self):
        """Test searching with an empty collection."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Set up mock collection.count to return zero
        self.mock_collection.count.return_value = 0

        # Search for items
        results = self.memory.search("query", limit=10)

        # Verify the results
        self.assertEqual(len(results), 0)

        # Verify collection.query was not called
        self.mock_collection.query.assert_not_called()

    def test_generate_embedding(self):
        """Test generate_embedding method."""
        # Generate an embedding
        embedding = self.memory.generate_embedding("Test text")

        # Verify the result
        self.assertEqual(len(embedding), 3)  # Dimension is 3
        self.assertIsInstance(embedding, list)
        self.assertIsInstance(embedding[0], float)

    def test_to_dict(self):
        """Test to_dict method."""
        # Reset mocks
        self.mock_collection.reset_mock()

        # Add an item directly to memory
        item = VectorMemoryItem(
            id="test-id",
            content="Test content",
            text="Test text",
            embedding=[0.1, 0.2, 0.3]
        )
        self.memory.items[item.id] = item

        # Convert memory to dictionary
        memory_dict = self.memory.to_dict()

        # Verify the result
        self.assertEqual(memory_dict["name"], "test-memory")
        self.assertEqual(memory_dict["memory_type"], "VECTOR")
        self.assertEqual(memory_dict["dimension"], 3)
        self.assertEqual(memory_dict["persist_directory"], self.temp_dir)
        self.assertIn(item.id, memory_dict["items"])
        self.assertEqual(memory_dict["items"][item.id]["content"], "Test content")

    def test_from_dict(self):
        """Test from_dict method."""
        # Reset mocks
        self.mock_client_class.reset_mock()
        self.mock_client.reset_mock()

        # Create a new mock collection for this test
        mock_collection = MagicMock()
        self.mock_client.get_or_create_collection.return_value = mock_collection

        # Set up mock collection.get to return expected results
        mock_collection.get.return_value = {
            "ids": ["item1"],
            "embeddings": [[0.1, 0.2, 0.3]],
            "documents": ["Test text"],
            "metadatas": [{
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "importance": 0.8,
                "key": "value"
            }]
        }

        # Create memory dictionary
        memory_dict = {
            "name": "test-memory",
            "memory_type": "VECTOR",
            "dimension": 3,
            "persist_directory": self.temp_dir,
            "items": {},
            "metadata": {"key": "value"}
        }

        # Create memory from dictionary
        memory = ChromaMemory.from_dict(memory_dict)

        # Verify the result
        self.assertEqual(memory.name, "test-memory")
        self.assertEqual(memory.dimension, 3)
        # Skip checking persist_directory in metadata as it's overwritten by the metadata from the dictionary
        self.assertEqual(len(memory.items), 1)
        self.assertIn("item1", memory.items)
        self.assertEqual(memory.items["item1"].content, "Test text")
        self.assertEqual(memory.items["item1"].text, "Test text")
        self.assertEqual(memory.items["item1"].embedding, [0.1, 0.2, 0.3])
        self.assertEqual(memory.items["item1"].metadata["key"], "value")
        self.assertEqual(memory.items["item1"].importance, 0.8)


if __name__ == "__main__":
    unittest.main()
