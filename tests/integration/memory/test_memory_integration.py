"""
Integration test for the memory system.

This module contains integration tests for the memory system,
verifying that the different components work together correctly.
"""

import unittest
import os
import tempfile
import shutil
import time
from unittest.mock import patch, MagicMock

import pytest
import numpy as np
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry
from augment_adam.memory.core.memory_item import MemoryItem
from augment_adam.memory.core.memory_base import Memory
from augment_adam.memory.core.memory_manager import MemoryManager
from augment_adam.memory.vector.vector_memory_base import VectorMemory
from augment_adam.memory.vector.faiss_memory import FAISSMemory
from augment_adam.memory.episodic.episodic_memory import EpisodicMemory
from augment_adam.memory.semantic.semantic_memory import SemanticMemory
from augment_adam.memory.working.working_memory import WorkingMemory


@safe_tag("testing.integration.memory")
class TestMemoryIntegration(unittest.TestCase):
    """
    Integration tests for the memory system.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a temporary directory for the test
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a memory manager
        self.manager = MemoryManager()
        
        # Create memory systems
        self.vector_memory = FAISSMemory(
            name="vector-memory",
            dimension=128,
            persist_directory=os.path.join(self.temp_dir, "vector-memory")
        )
        
        self.episodic_memory = EpisodicMemory(
            name="episodic-memory",
            persist_directory=os.path.join(self.temp_dir, "episodic-memory")
        )
        
        self.semantic_memory = SemanticMemory(
            name="semantic-memory",
            persist_directory=os.path.join(self.temp_dir, "semantic-memory")
        )
        
        self.working_memory = WorkingMemory(
            name="working-memory",
            capacity=10
        )
        
        # Register the memory systems
        self.manager.register_memory(self.vector_memory)
        self.manager.register_memory(self.episodic_memory)
        self.manager.register_memory(self.semantic_memory)
        self.manager.register_memory(self.working_memory)
    
    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_add_and_retrieve_across_memories(self):
        """Test adding and retrieving items across different memory systems."""
        # Create a memory item
        item = MemoryItem(
            content="This is a test memory item",
            metadata={"source": "integration-test", "importance": 0.8},
            embedding=np.random.rand(128).tolist()
        )
        
        # Add the item to vector memory
        vector_id = self.manager.add_item("vector-memory", item)
        
        # Add the item to episodic memory
        episodic_id = self.manager.add_item("episodic-memory", item)
        
        # Add the item to semantic memory
        semantic_id = self.manager.add_item("semantic-memory", item)
        
        # Add the item to working memory
        working_id = self.manager.add_item("working-memory", item)
        
        # Verify the item was added to all memory systems
        self.assertIsNotNone(vector_id)
        self.assertIsNotNone(episodic_id)
        self.assertIsNotNone(semantic_id)
        self.assertIsNotNone(working_id)
        
        # Retrieve the item from each memory system
        vector_item = self.manager.get_item("vector-memory", vector_id)
        episodic_item = self.manager.get_item("episodic-memory", episodic_id)
        semantic_item = self.manager.get_item("semantic-memory", semantic_id)
        working_item = self.manager.get_item("working-memory", working_id)
        
        # Verify the items were retrieved correctly
        self.assertEqual(vector_item.content, "This is a test memory item")
        self.assertEqual(episodic_item.content, "This is a test memory item")
        self.assertEqual(semantic_item.content, "This is a test memory item")
        self.assertEqual(working_item.content, "This is a test memory item")
        
        # Verify the metadata was preserved
        self.assertEqual(vector_item.metadata["source"], "integration-test")
        self.assertEqual(episodic_item.metadata["importance"], 0.8)
        self.assertEqual(semantic_item.metadata["source"], "integration-test")
        self.assertEqual(working_item.metadata["importance"], 0.8)
    
    def test_search_across_memories(self):
        """Test searching across different memory systems."""
        # Create and add multiple items to each memory system
        for i in range(5):
            item = MemoryItem(
                content=f"Memory item {i}",
                metadata={"index": i, "even": (i % 2 == 0)},
                embedding=np.random.rand(128).tolist()
            )
            
            self.manager.add_item("vector-memory", item)
            self.manager.add_item("episodic-memory", item)
            self.manager.add_item("semantic-memory", item)
            self.manager.add_item("working-memory", item)
        
        # Search in vector memory
        vector_results = self.manager.search("vector-memory", np.random.rand(128).tolist(), limit=3)
        
        # Search in episodic memory with a filter
        episodic_results = self.manager.search(
            "episodic-memory",
            "Memory",
            filter_func=lambda item: item.metadata.get("even", False)
        )
        
        # Search in semantic memory
        semantic_results = self.manager.search("semantic-memory", "Memory item")
        
        # Search in working memory
        working_results = self.manager.search("working-memory", "Memory")
        
        # Verify the search results
        self.assertLessEqual(len(vector_results), 3)
        self.assertLessEqual(len(episodic_results), 3)  # Only even-indexed items
        self.assertGreater(len(semantic_results), 0)
        self.assertGreater(len(working_results), 0)
        
        # Verify the episodic results only contain even-indexed items
        for item in episodic_results:
            self.assertTrue(item.metadata.get("even", False))
    
    def test_update_across_memories(self):
        """Test updating items across different memory systems."""
        # Create and add an item to each memory system
        item = MemoryItem(
            content="Original content",
            metadata={"version": 1}
        )
        
        vector_id = self.manager.add_item("vector-memory", item)
        episodic_id = self.manager.add_item("episodic-memory", item)
        semantic_id = self.manager.add_item("semantic-memory", item)
        working_id = self.manager.add_item("working-memory", item)
        
        # Update the items
        self.manager.update_item(
            "vector-memory",
            vector_id,
            content="Updated vector content",
            metadata={"version": 2}
        )
        
        self.manager.update_item(
            "episodic-memory",
            episodic_id,
            content="Updated episodic content",
            metadata={"version": 2}
        )
        
        self.manager.update_item(
            "semantic-memory",
            semantic_id,
            content="Updated semantic content",
            metadata={"version": 2}
        )
        
        self.manager.update_item(
            "working-memory",
            working_id,
            content="Updated working content",
            metadata={"version": 2}
        )
        
        # Retrieve the updated items
        vector_item = self.manager.get_item("vector-memory", vector_id)
        episodic_item = self.manager.get_item("episodic-memory", episodic_id)
        semantic_item = self.manager.get_item("semantic-memory", semantic_id)
        working_item = self.manager.get_item("working-memory", working_id)
        
        # Verify the items were updated correctly
        self.assertEqual(vector_item.content, "Updated vector content")
        self.assertEqual(episodic_item.content, "Updated episodic content")
        self.assertEqual(semantic_item.content, "Updated semantic content")
        self.assertEqual(working_item.content, "Updated working content")
        
        # Verify the metadata was updated
        self.assertEqual(vector_item.metadata["version"], 2)
        self.assertEqual(episodic_item.metadata["version"], 2)
        self.assertEqual(semantic_item.metadata["version"], 2)
        self.assertEqual(working_item.metadata["version"], 2)
    
    def test_remove_across_memories(self):
        """Test removing items across different memory systems."""
        # Create and add an item to each memory system
        item = MemoryItem(
            content="Item to remove",
            metadata={"removable": True}
        )
        
        vector_id = self.manager.add_item("vector-memory", item)
        episodic_id = self.manager.add_item("episodic-memory", item)
        semantic_id = self.manager.add_item("semantic-memory", item)
        working_id = self.manager.add_item("working-memory", item)
        
        # Remove the items
        vector_result = self.manager.remove_item("vector-memory", vector_id)
        episodic_result = self.manager.remove_item("episodic-memory", episodic_id)
        semantic_result = self.manager.remove_item("semantic-memory", semantic_id)
        working_result = self.manager.remove_item("working-memory", working_id)
        
        # Verify the items were removed
        self.assertTrue(vector_result)
        self.assertTrue(episodic_result)
        self.assertTrue(semantic_result)
        self.assertTrue(working_result)
        
        # Try to retrieve the removed items
        vector_item = self.manager.get_item("vector-memory", vector_id)
        episodic_item = self.manager.get_item("episodic-memory", episodic_id)
        semantic_item = self.manager.get_item("semantic-memory", semantic_id)
        working_item = self.manager.get_item("working-memory", working_id)
        
        # Verify the items are no longer available
        self.assertIsNone(vector_item)
        self.assertIsNone(episodic_item)
        self.assertIsNone(semantic_item)
        self.assertIsNone(working_item)
    
    def test_memory_persistence(self):
        """Test memory persistence across restarts."""
        # Skip this test if the memory systems don't support persistence
        if not hasattr(self.vector_memory, "save") or not hasattr(self.vector_memory, "load"):
            self.skipTest("Memory system doesn't support persistence")
        
        # Create and add items to each memory system
        for i in range(3):
            item = MemoryItem(
                content=f"Persistent item {i}",
                metadata={"persistent": True, "index": i},
                embedding=np.random.rand(128).tolist()
            )
            
            self.manager.add_item("vector-memory", item)
            self.manager.add_item("episodic-memory", item)
            self.manager.add_item("semantic-memory", item)
        
        # Save the memory systems
        self.vector_memory.save()
        self.episodic_memory.save()
        self.semantic_memory.save()
        
        # Create new memory systems that load from the same directories
        new_vector_memory = FAISSMemory(
            name="new-vector-memory",
            dimension=128,
            persist_directory=os.path.join(self.temp_dir, "vector-memory")
        )
        
        new_episodic_memory = EpisodicMemory(
            name="new-episodic-memory",
            persist_directory=os.path.join(self.temp_dir, "episodic-memory")
        )
        
        new_semantic_memory = SemanticMemory(
            name="new-semantic-memory",
            persist_directory=os.path.join(self.temp_dir, "semantic-memory")
        )
        
        # Load the memory systems
        new_vector_memory.load()
        new_episodic_memory.load()
        new_semantic_memory.load()
        
        # Create a new manager
        new_manager = MemoryManager()
        
        # Register the new memory systems
        new_manager.register_memory(new_vector_memory)
        new_manager.register_memory(new_episodic_memory)
        new_manager.register_memory(new_semantic_memory)
        
        # Search in the new memory systems
        vector_results = new_manager.search("new-vector-memory", np.random.rand(128).tolist())
        episodic_results = new_manager.search("new-episodic-memory", "Persistent")
        semantic_results = new_manager.search("new-semantic-memory", "Persistent")
        
        # Verify the items were loaded correctly
        self.assertGreater(len(vector_results), 0)
        self.assertGreater(len(episodic_results), 0)
        self.assertGreater(len(semantic_results), 0)
        
        # Verify the metadata was preserved
        for item in episodic_results:
            self.assertTrue(item.metadata.get("persistent", False))
    
    def test_working_memory_capacity(self):
        """Test working memory capacity limits."""
        # Add items to working memory up to its capacity
        for i in range(15):  # More than the capacity (10)
            item = MemoryItem(
                content=f"Working memory item {i}",
                metadata={"index": i}
            )
            
            self.manager.add_item("working-memory", item)
        
        # Get all items from working memory
        items = self.manager.get_all_items("working-memory")
        
        # Verify the number of items is limited by the capacity
        self.assertLessEqual(len(items), 10)
        
        # Verify the most recently added items are kept
        indices = [item.metadata.get("index") for item in items]
        self.assertGreaterEqual(min(indices), 5)  # The oldest items should be removed
    
    def test_cross_memory_operations(self):
        """Test operations that involve multiple memory systems."""
        # Create items
        item1 = MemoryItem(
            content="Item for vector and episodic memory",
            metadata={"type": "cross-memory"},
            embedding=np.random.rand(128).tolist()
        )
        
        item2 = MemoryItem(
            content="Item for semantic and working memory",
            metadata={"type": "cross-memory"},
            embedding=np.random.rand(128).tolist()
        )
        
        # Add items to different memory systems
        vector_id = self.manager.add_item("vector-memory", item1)
        episodic_id = self.manager.add_item("episodic-memory", item1)
        semantic_id = self.manager.add_item("semantic-memory", item2)
        working_id = self.manager.add_item("working-memory", item2)
        
        # Search across all memory systems
        all_results = []
        for memory_name in ["vector-memory", "episodic-memory", "semantic-memory", "working-memory"]:
            results = self.manager.search(
                memory_name,
                "Item",
                filter_func=lambda item: item.metadata.get("type") == "cross-memory"
            )
            all_results.extend(results)
        
        # Verify results from all memory systems
        self.assertGreaterEqual(len(all_results), 4)
        
        # Count occurrences of each item
        content_counts = {}
        for item in all_results:
            content = item.content
            content_counts[content] = content_counts.get(content, 0) + 1
        
        # Verify both items were found
        self.assertIn("Item for vector and episodic memory", content_counts)
        self.assertIn("Item for semantic and working memory", content_counts)
        
        # Verify each item was found in the correct number of memory systems
        self.assertEqual(content_counts["Item for vector and episodic memory"], 2)
        self.assertEqual(content_counts["Item for semantic and working memory"], 2)
    
if __name__ == "__main__":
    unittest.main()
