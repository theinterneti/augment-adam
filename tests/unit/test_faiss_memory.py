"""Unit tests for the FAISS-based memory system.

This module contains unit tests for the FAISS-based memory system,
testing the core functionality of the FAISSMemory class.

Version: 0.1.0
Created: 2025-04-24
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import pytest
import numpy as np
import faiss

from augment_adam.memory.faiss_memory import FAISSMemory, get_faiss_memory
from augment_adam.core.errors import ResourceError, DatabaseError


class TestFAISSMemory(unittest.TestCase):
    """Test the FAISSMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.persist_dir = os.path.join(self.temp_dir.name, "faiss_memory")

        # Create a real FAISS memory instance for testing
        self.memory = FAISSMemory(
            persist_dir=self.persist_dir,
            collection_name="test_memory",
        )

        # Store the collection name for convenience
        self.collection_name = "test_memory"

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def test_init(self):
        """Test that FAISSMemory initializes correctly."""
        # Check that the memory was initialized correctly
        self.assertEqual(self.memory.persist_dir, self.persist_dir)
        self.assertEqual(self.memory.default_collection, self.collection_name)
        self.assertIsNotNone(self.memory.embedding_model)
        self.assertIsNotNone(self.memory.collections.get(self.collection_name))
        self.assertIsNotNone(self.memory.metadata.get(self.collection_name))
        self.assertIsNotNone(self.memory.ids.get(self.collection_name))

    def test_add_retrieve(self):
        """Test adding and retrieving memories."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note", "tags": ["test", "example"]},
            collection_name=self.collection_name,
        )

        # Check that the memory was added
        self.assertIsNotNone(memory_id)
        self.assertTrue(memory_id.startswith("mem_"))

        # Retrieve the memory
        results = self.memory.retrieve(
            query="test memory",
            n_results=1,
            collection_name=self.collection_name,
        )

        # Check that the memory was retrieved
        self.assertEqual(len(results), 1)
        memory, score = results[0]
        self.assertEqual(memory["text"], "This is a test memory")
        self.assertEqual(memory["type"], "note")
        self.assertEqual(memory["tags"], ["test", "example"])
        self.assertGreater(score, 0)

    def test_get_by_id(self):
        """Test getting a memory by ID."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name=self.collection_name,
        )

        # Get the memory by ID
        memory = self.memory.get_by_id(memory_id, collection_name=self.collection_name)

        # Check that the memory was retrieved
        self.assertIsNotNone(memory)
        self.assertEqual(memory["text"], "This is a test memory")
        self.assertEqual(memory["type"], "note")

    def test_delete(self):
        """Test deleting a memory."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name=self.collection_name,
        )

        # Delete the memory
        result = self.memory.delete(memory_id, collection_name=self.collection_name)

        # Check that the memory was deleted
        self.assertTrue(result)

        # Try to get the deleted memory
        memory = self.memory.get_by_id(memory_id, collection_name=self.collection_name)

        # Check that the memory is gone
        self.assertIsNone(memory)

    def test_clear(self):
        """Test clearing all memories."""
        # Add some memories
        self.memory.add(
            text="Memory 1",
            metadata={"type": "note"},
            collection_name=self.collection_name,
        )
        self.memory.add(
            text="Memory 2",
            metadata={"type": "note"},
            collection_name=self.collection_name,
        )

        # Clear all memories
        result = self.memory.clear(collection_name=self.collection_name)

        # Check that the memories were cleared
        self.assertTrue(result)

        # Try to retrieve memories
        results = self.memory.retrieve(
            query="memory",
            n_results=10,
            collection_name=self.collection_name,
        )

        # Check that no memories were found
        self.assertEqual(len(results), 0)

    def test_filter_metadata(self):
        """Test filtering by metadata."""
        # Add memories with different metadata
        self.memory.add(
            text="Python is a programming language",
            metadata={"type": "note", "topic": "programming", "language": "python"},
            collection_name=self.collection_name,
        )
        self.memory.add(
            text="JavaScript is a programming language",
            metadata={"type": "note", "topic": "programming", "language": "javascript"},
            collection_name=self.collection_name,
        )
        self.memory.add(
            text="The weather is nice today",
            metadata={"type": "note", "topic": "weather"},
            collection_name=self.collection_name,
        )

        # Retrieve memories with filter
        results = self.memory.retrieve(
            query="programming language",
            n_results=10,
            filter_metadata={"language": "python"},
            collection_name=self.collection_name,
        )

        # Check that only Python memories were retrieved
        self.assertEqual(len(results), 1)
        memory, _ = results[0]
        self.assertEqual(memory["language"], "python")

        # Retrieve memories with a different filter
        results = self.memory.retrieve(
            query="programming language",
            n_results=10,
            filter_metadata={"topic": "programming"},
            collection_name=self.collection_name,
        )

        # Check that both programming memories were retrieved
        self.assertEqual(len(results), 2)
        languages = [memory["language"] for memory, _ in results if "language" in memory]
        self.assertIn("python", languages)
        self.assertIn("javascript", languages)

    @patch('os.makedirs')
    def test_init_directory_error(self, mock_makedirs):
        """Test handling of directory creation errors in __init__."""
        # Mock os.makedirs to raise an OSError
        mock_makedirs.side_effect = OSError("Permission denied")

        # Check that the error is wrapped and re-raised
        with self.assertRaises(ResourceError):
            FAISSMemory(
                persist_dir="/nonexistent/directory",
                collection_name="test_memory",  # Using string directly for this test
            )

    @patch('faiss.read_index')
    def test_init_collections_error(self, mock_read_index):
        """Test handling of errors in _init_collections."""
        # Mock faiss.read_index to raise an exception
        mock_read_index.side_effect = Exception("Index error")

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            persist_dir = os.path.join(temp_dir, "faiss_memory")
            os.makedirs(os.path.join(persist_dir, "test_memory"), exist_ok=True)

            # Create an empty index file to trigger read_index
            with open(os.path.join(persist_dir, "test_memory", "index.faiss"), "w") as f:
                f.write("")

            # Check that the error is wrapped and re-raised
            with self.assertRaises(DatabaseError):
                FAISSMemory(
                    persist_dir=persist_dir,
                    collection_name="test_memory",  # Using string directly for this test
                )

    def test_add_empty_text(self):
        """Test adding empty text."""
        # Try to add empty text
        memory_id = self.memory.add("", collection_name=self.collection_name)

        # Check that an empty string is returned
        self.assertEqual(memory_id, "")

    def test_retrieve_empty_query(self):
        """Test retrieving with empty query."""
        # Try to retrieve with empty query
        results = self.memory.retrieve("", collection_name=self.collection_name)

        # Check that an empty list is returned
        self.assertEqual(results, [])

    def test_get_by_id_not_found(self):
        """Test getting a memory by ID that doesn't exist."""
        # Try to get a memory that doesn't exist
        memory = self.memory.get_by_id("nonexistent_id", collection_name=self.collection_name)

        # Check that None is returned
        self.assertIsNone(memory)

    def test_delete_not_found(self):
        """Test deleting a memory that doesn't exist."""
        # Try to delete a memory that doesn't exist
        result = self.memory.delete("nonexistent_id", collection_name=self.collection_name)

        # Check that False is returned
        self.assertFalse(result)

    def test_get_faiss_memory(self):
        """Test the get_faiss_memory function."""
        # Get the default memory instance
        memory = get_faiss_memory(
            persist_dir=self.persist_dir,
            collection_name=self.collection_name,
        )

        # Check that the memory was initialized correctly
        self.assertIsNotNone(memory)
        self.assertEqual(memory.persist_dir, self.persist_dir)

        # Get the memory instance again (should be the same instance)
        memory2 = get_faiss_memory()

        # Check that the same instance was returned
        self.assertIs(memory, memory2)


if __name__ == "__main__":
    unittest.main()
