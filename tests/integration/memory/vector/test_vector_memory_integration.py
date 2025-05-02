"""
Integration tests for augment_adam.memory.vector module.

This module contains integration tests for the vector memory components,
testing how they work together and with other components.
"""

import unittest
import pytest
import os
import tempfile
import shutil
import numpy as np
from typing import List, Dict, Any, Optional

from augment_adam.memory.core.base import MemoryType, MemoryManager
from augment_adam.memory.vector.base import VectorMemory, VectorMemoryItem
from augment_adam.memory.vector.faiss import FAISSMemory
from augment_adam.memory.vector.chroma import ChromaMemory


class TestVectorMemoryIntegration(unittest.TestCase):
    """Integration tests for vector memory components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MemoryManager()
        
        # Create memory systems
        self.faiss_memory = FAISSMemory("faiss-memory", dimension=3)
        self.chroma_memory = ChromaMemory("chroma-memory", dimension=3, persist_directory=self.temp_dir)
        
        # Register memory systems with the manager
        self.manager.register_memory(self.faiss_memory)
        self.manager.register_memory(self.chroma_memory)

    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_memory_manager_registration(self):
        """Test registering memory systems with the manager."""
        self.assertEqual(len(self.manager.memories), 2)
        self.assertIn("faiss-memory", self.manager.memories)
        self.assertIn("chroma-memory", self.manager.memories)
        
        # Test getting memory by name
        faiss_memory = self.manager.get_memory("faiss-memory")
        chroma_memory = self.manager.get_memory("chroma-memory")
        
        self.assertEqual(faiss_memory, self.faiss_memory)
        self.assertEqual(chroma_memory, self.chroma_memory)
        
        # Test getting memories by type
        vector_memories = self.manager.get_memories_by_type(MemoryType.VECTOR)
        self.assertEqual(len(vector_memories), 2)
        self.assertIn(self.faiss_memory, vector_memories)
        self.assertIn(self.chroma_memory, vector_memories)

    def test_add_and_retrieve_items(self):
        """Test adding and retrieving items through the manager."""
        # Create items
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
        
        # Add items to both memory systems
        faiss_item1_id = self.manager.add_item("faiss-memory", item1)
        faiss_item2_id = self.manager.add_item("faiss-memory", item2)
        chroma_item1_id = self.manager.add_item("chroma-memory", item1)
        chroma_item2_id = self.manager.add_item("chroma-memory", item2)
        
        # Retrieve items
        faiss_item1 = self.manager.get_item("faiss-memory", faiss_item1_id)
        faiss_item2 = self.manager.get_item("faiss-memory", faiss_item2_id)
        chroma_item1 = self.manager.get_item("chroma-memory", chroma_item1_id)
        chroma_item2 = self.manager.get_item("chroma-memory", chroma_item2_id)
        
        # Check that the items were retrieved correctly
        self.assertEqual(faiss_item1.content, "Item 1")
        self.assertEqual(faiss_item2.content, "Item 2")
        self.assertEqual(chroma_item1.content, "Item 1")
        self.assertEqual(chroma_item2.content, "Item 2")

    def test_update_items(self):
        """Test updating items through the manager."""
        # Create an item
        item = VectorMemoryItem(
            content="Original content",
            text="Original content",
            embedding=[0.1, 0.2, 0.3],
            metadata={"key1": "value1"}
        )
        
        # Add the item to both memory systems
        faiss_item_id = self.manager.add_item("faiss-memory", item)
        chroma_item_id = self.manager.add_item("chroma-memory", item)
        
        # Update the items
        self.manager.update_item("faiss-memory", faiss_item_id, content="Updated content", metadata={"key2": "value2"})
        self.manager.update_item("chroma-memory", chroma_item_id, content="Updated content", metadata={"key2": "value2"})
        
        # Retrieve the updated items
        faiss_item = self.manager.get_item("faiss-memory", faiss_item_id)
        chroma_item = self.manager.get_item("chroma-memory", chroma_item_id)
        
        # Check that the items were updated correctly
        self.assertEqual(faiss_item.content, "Updated content")
        self.assertEqual(faiss_item.text, "Updated content")
        self.assertEqual(faiss_item.metadata, {"key1": "value1", "key2": "value2"})
        
        self.assertEqual(chroma_item.content, "Updated content")
        self.assertEqual(chroma_item.text, "Updated content")
        self.assertEqual(chroma_item.metadata, {"key1": "value1", "key2": "value2"})

    def test_remove_items(self):
        """Test removing items through the manager."""
        # Create an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test content",
            embedding=[0.1, 0.2, 0.3]
        )
        
        # Add the item to both memory systems
        faiss_item_id = self.manager.add_item("faiss-memory", item)
        chroma_item_id = self.manager.add_item("chroma-memory", item)
        
        # Remove the items
        faiss_result = self.manager.remove_item("faiss-memory", faiss_item_id)
        chroma_result = self.manager.remove_item("chroma-memory", chroma_item_id)
        
        # Check that the items were removed
        self.assertTrue(faiss_result)
        self.assertTrue(chroma_result)
        
        # Try to retrieve the removed items
        faiss_item = self.manager.get_item("faiss-memory", faiss_item_id)
        chroma_item = self.manager.get_item("chroma-memory", chroma_item_id)
        
        # Check that the items are no longer in memory
        self.assertIsNone(faiss_item)
        self.assertIsNone(chroma_item)

    def test_search_across_memories(self):
        """Test searching across multiple memory systems."""
        # Create items with different similarities to the query
        item1 = VectorMemoryItem(
            content="Item 1",
            text="Item 1",
            embedding=[0.1, 0.2, 0.3]  # More similar to query
        )
        item2 = VectorMemoryItem(
            content="Item 2",
            text="Item 2",
            embedding=[0.4, 0.5, 0.6]  # Less similar to query
        )
        item3 = VectorMemoryItem(
            content="Item 3",
            text="Item 3",
            embedding=[0.7, 0.8, 0.9]  # Least similar to query
        )
        
        # Add items to both memory systems
        self.manager.add_item("faiss-memory", item1)
        self.manager.add_item("faiss-memory", item2)
        self.manager.add_item("chroma-memory", item2)
        self.manager.add_item("chroma-memory", item3)
        
        # Search in FAISS memory
        faiss_results = self.faiss_memory.search([0.1, 0.2, 0.3], limit=2)
        
        # Search in Chroma memory
        chroma_results = self.chroma_memory.search([0.1, 0.2, 0.3], limit=2)
        
        # Check FAISS results
        self.assertEqual(len(faiss_results), 2)
        self.assertEqual(faiss_results[0].content, "Item 1")  # Most similar
        self.assertEqual(faiss_results[1].content, "Item 2")  # Less similar
        
        # Check Chroma results
        self.assertEqual(len(chroma_results), 2)
        self.assertEqual(chroma_results[0].content, "Item 2")  # More similar
        self.assertEqual(chroma_results[1].content, "Item 3")  # Less similar

    def test_memory_persistence(self):
        """Test memory persistence for Chroma memory."""
        # Create an item
        item = VectorMemoryItem(
            content="Test content",
            text="Test content",
            embedding=[0.1, 0.2, 0.3]
        )
        
        # Add the item to Chroma memory
        item_id = self.chroma_memory.add(item)
        
        # Create a new Chroma memory with the same persist directory
        new_chroma_memory = ChromaMemory("chroma-memory", dimension=3, persist_directory=self.temp_dir)
        
        # Check that the item is still in memory
        retrieved_item = new_chroma_memory.get(item_id)
        
        # The item might not be in the items dictionary, but it should be in the Chroma collection
        if retrieved_item is None:
            # Search for the item
            results = new_chroma_memory.search([0.1, 0.2, 0.3], limit=1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].text, "Test content")
        else:
            self.assertEqual(retrieved_item.content, "Test content")
            self.assertEqual(retrieved_item.text, "Test content")
            self.assertEqual(retrieved_item.embedding, [0.1, 0.2, 0.3])

    def test_faiss_memory_save_and_load(self):
        """Test saving and loading FAISS memory."""
        # Create items
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
        
        # Add items to FAISS memory
        self.faiss_memory.add(item1)
        self.faiss_memory.add(item2)
        
        # Save FAISS memory
        save_dir = os.path.join(self.temp_dir, "faiss")
        self.faiss_memory.save(save_dir)
        
        # Load FAISS memory
        loaded_memory = FAISSMemory.load(save_dir)
        
        # Check that the loaded memory has the same items
        self.assertEqual(len(loaded_memory.items), 2)
        
        # Search for items
        results = loaded_memory.search([0.1, 0.2, 0.3], limit=2)
        
        # Check that the search returns the correct items
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].content, "Item 1")  # Most similar
        self.assertEqual(results[1].content, "Item 2")  # Less similar


if __name__ == "__main__":
    unittest.main()
