"""
Unit tests for base.

This module contains unit tests for the base module.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock

from augment_adam.memory.core.base import *

class TestMemory(unittest.TestCase):
    """Tests for the Memory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        # Create a concrete implementation of Memory for testing
        class TestMemoryImpl(Memory):
            def __init__(self, name="test_memory", memory_type=MemoryType.VECTOR):
                super().__init__(name=name, memory_type=memory_type)
                
            def search(self, query, limit=10):
                # Simple implementation for testing
                return list(self.items.values())[:limit]
        
        self.instance = TestMemoryImpl()

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test___init___basic(self):
        """Test basic functionality of __init__."""
        # Arrange
        name = "test_name"
        memory_type = MemoryType.VECTOR

        # Act
        instance = Memory(name=name, memory_type=memory_type)

        # Assert
        self.assertIsInstance(instance, Memory)

    def test_add_item_basic(self):
        """Test basic functionality of add_item."""
        # Arrange
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        expected_result = MagicMock()

        # Act
        result = self.instance.add_item(item_id, content, metadata)

        # Assert
        # Verify the result
        self.assertEqual(item_id, result)
        self.assertIn(item_id, self.instance.items)

    def test_get_item_basic(self):
        """Test basic functionality of get_item."""
        # Arrange
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        self.instance.add_item(item_id, content, metadata)

        # Act
        result = self.instance.get_item(item_id)

        # Assert
        # Verify the result
        self.assertEqual(content, result.content)
        self.assertEqual(metadata, result.metadata)

    def test_update_item_basic(self):
        """Test basic functionality of update_item."""
        # Arrange
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        self.instance.add_item(item_id, content, metadata)
        
        new_content = "new_content"
        new_metadata = {"key": "new_value"}

        # Act
        result = self.instance.update_item(item_id, new_content, new_metadata)

        # Assert
        # Verify the result
        self.assertEqual(item_id, result)
        self.assertEqual(new_content, self.instance.get_item(item_id).content)
        self.assertEqual(new_metadata, self.instance.get_item(item_id).metadata)

    def test_remove_item_basic(self):
        """Test basic functionality of remove_item."""
        # Arrange
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        self.instance.add_item(item_id, content, metadata)

        # Act
        result = self.instance.remove_item(item_id)

        # Assert
        # Verify the result
        self.assertEqual(item_id, result)
        self.assertNotIn(item_id, self.instance.items)

    def test_search_basic(self):
        """Test basic functionality of search."""
        # Arrange
        query = "test_query"
        limit = 10

        # Act
        result = self.instance.search(query, limit=limit)

        # Assert
        # Verify the result
        self.assertIsInstance(result, list)

    def test_to_dict_basic(self):
        """Test basic functionality of to_dict."""
        # Arrange
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        self.instance.add_item(item_id, content, metadata)

        # Act
        result = self.instance.to_dict()

        # Assert
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("memory_type", result)
        self.assertIn("items", result)

class TestMemoryManager(unittest.TestCase):
    """Tests for the MemoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.instance = MemoryManager()
        
        # Create a test memory
        class TestMemoryImpl(Memory):
            def __init__(self, name="test_memory", memory_type=MemoryType.VECTOR):
                super().__init__(name=name, memory_type=memory_type)
                
            def search(self, query, limit=10):
                # Simple implementation for testing
                return list(self.items.values())[:limit]
        
        self.test_memory = TestMemoryImpl()

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test___init___basic(self):
        """Test basic functionality of __init__."""
        # Arrange

        # Act
        instance = MemoryManager()

        # Assert
        self.assertIsInstance(instance, MemoryManager)

    def test_register_memory_basic(self):
        """Test basic functionality of register_memory."""
        # Arrange
        memory = self.test_memory

        # Act
        self.instance.register_memory(memory)

        # Assert
        # Verify the method behavior
        self.assertIn(memory.name, self.instance.memories)
        self.assertEqual(memory, self.instance.memories[memory.name])

    def test_unregister_memory_basic(self):
        """Test basic functionality of unregister_memory."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)

        # Act
        result = self.instance.unregister_memory(memory.name)

        # Assert
        # Verify the result
        self.assertEqual(memory, result)
        self.assertNotIn(memory.name, self.instance.memories)

    def test_get_memory_basic(self):
        """Test basic functionality of get_memory."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)

        # Act
        result = self.instance.get_memory(memory.name)

        # Assert
        # Verify the result
        self.assertEqual(memory, result)

    def test_get_memories_by_type_basic(self):
        """Test basic functionality of get_memories_by_type."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)

        # Act
        result = self.instance.get_memories_by_type(memory.memory_type)

        # Assert
        # Verify the result
        self.assertIn(memory, result)

    def test_get_all_memories_basic(self):
        """Test basic functionality of get_all_memories."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)

        # Act
        result = self.instance.get_all_memories()

        # Assert
        # Verify the result
        self.assertIn(memory.name, result)
        self.assertEqual(memory, result[memory.name])

    def test_add_item_basic(self):
        """Test basic functionality of add_item."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)
        
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}

        # Act
        result = self.instance.add_item(memory.name, item_id, content, metadata)

        # Assert
        # Verify the result
        self.assertEqual(item_id, result)
        self.assertIn(item_id, memory.items)

    def test_get_item_basic(self):
        """Test basic functionality of get_item."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)
        
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        memory.add_item(item_id, content, metadata)

        # Act
        result = self.instance.get_item(memory.name, item_id)

        # Assert
        # Verify the result
        self.assertEqual(content, result.content)
        self.assertEqual(metadata, result.metadata)

    def test_update_item_basic(self):
        """Test basic functionality of update_item."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)
        
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        memory.add_item(item_id, content, metadata)
        
        new_content = "new_content"
        new_metadata = {"key": "new_value"}

        # Act
        result = self.instance.update_item(memory.name, item_id, new_content, new_metadata)

        # Assert
        # Verify the result
        self.assertEqual(item_id, result)
        self.assertEqual(new_content, memory.get_item(item_id).content)
        self.assertEqual(new_metadata, memory.get_item(item_id).metadata)

    def test_remove_item_basic(self):
        """Test basic functionality of remove_item."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)
        
        item_id = "test_id"
        content = "test_content"
        metadata = {"key": "value"}
        memory.add_item(item_id, content, metadata)

        # Act
        result = self.instance.remove_item(memory.name, item_id)

        # Assert
        # Verify the result
        self.assertEqual(item_id, result)
        self.assertNotIn(item_id, memory.items)

    def test_search_basic(self):
        """Test basic functionality of search."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)
        
        query = "test_query"
        limit = 10

        # Act
        result = self.instance.search(memory.name, query, limit=limit)

        # Assert
        # Verify the result
        self.assertIsInstance(result, list)

    def test_search_all_basic(self):
        """Test basic functionality of search_all."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)
        
        query = "test_query"
        limit = 10

        # Act
        result = self.instance.search_all(query, limit=limit)

        # Assert
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertIn(memory.name, result)

    def test_set_metadata_basic(self):
        """Test basic functionality of set_metadata."""
        # Arrange
        key = "test_key"
        value = "test_value"

        # Act
        self.instance.set_metadata(key, value)

        # Assert
        # Verify the method behavior
        self.assertIn(key, self.instance.metadata)
        self.assertEqual(value, self.instance.metadata[key])

    def test_get_metadata_basic(self):
        """Test basic functionality of get_metadata."""
        # Arrange
        key = "test_key"
        value = "test_value"
        self.instance.set_metadata(key, value)

        # Act
        result = self.instance.get_metadata(key)

        # Assert
        # Verify the result
        self.assertEqual(value, result)

    def test_to_dict_basic(self):
        """Test basic functionality of to_dict."""
        # Arrange
        memory = self.test_memory
        self.instance.register_memory(memory)

        # Act
        result = self.instance.to_dict()

        # Assert
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertIn("memories", result)
        self.assertIn("metadata", result)

if __name__ == '__main__':
    unittest.main()
