"""Unit tests for the MemoryManager class."""

import unittest
from unittest.mock import MagicMock, patch

from augment_adam.ai_agent.memory_integration.memory_manager import MemoryManager


class TestMemoryManager(unittest.TestCase):
    """Tests for the MemoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the memory system
        self.memory = MagicMock()
        
        # Patch the create_memory and get_default_memory functions
        self.create_memory_patch = patch('augment_adam.ai_agent.memory_integration.memory_manager.create_memory')
        self.get_default_memory_patch = patch('augment_adam.ai_agent.memory_integration.memory_manager.get_default_memory')
        
        self.mock_create_memory = self.create_memory_patch.start()
        self.mock_get_default_memory = self.get_default_memory_patch.start()
        
        # Set up the mocks
        self.mock_create_memory.return_value = self.memory
        self.mock_get_default_memory.return_value = self.memory
        
        # Create a memory manager
        self.manager = MemoryManager(
            memory_type="test_memory",
            agent_id="test_agent",
            collection_name="test_collection"
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.create_memory_patch.stop()
        self.get_default_memory_patch.stop()
    
    def test_initialization_with_memory_type(self):
        """Test initialization with a memory type."""
        # Check that create_memory was called
        self.mock_create_memory.assert_called_once_with("test_memory")
        
        # Check that get_default_memory was not called
        self.mock_get_default_memory.assert_not_called()
        
        # Check that the memory manager was initialized correctly
        self.assertEqual(self.manager.memory, self.memory)
        self.assertEqual(self.manager.agent_id, "test_agent")
        self.assertEqual(self.manager.collection_name, "test_collection")
    
    def test_initialization_without_memory_type(self):
        """Test initialization without a memory type."""
        # Reset the mocks
        self.mock_create_memory.reset_mock()
        self.mock_get_default_memory.reset_mock()
        
        # Create a memory manager without a memory type
        manager = MemoryManager(
            agent_id="test_agent",
            collection_name="test_collection"
        )
        
        # Check that create_memory was not called
        self.mock_create_memory.assert_not_called()
        
        # Check that get_default_memory was called
        self.mock_get_default_memory.assert_called_once()
        
        # Check that the memory manager was initialized correctly
        self.assertEqual(manager.memory, self.memory)
        self.assertEqual(manager.agent_id, "test_agent")
        self.assertEqual(manager.collection_name, "test_collection")
    
    def test_initialization_with_generated_agent_id(self):
        """Test initialization with a generated agent ID."""
        # Reset the mocks
        self.mock_create_memory.reset_mock()
        self.mock_get_default_memory.reset_mock()
        
        # Create a memory manager without an agent ID
        manager = MemoryManager(
            memory_type="test_memory",
            collection_name="test_collection"
        )
        
        # Check that the agent ID was generated
        self.assertIsNotNone(manager.agent_id)
        self.assertNotEqual(manager.agent_id, "")
    
    def test_initialization_with_generated_collection_name(self):
        """Test initialization with a generated collection name."""
        # Reset the mocks
        self.mock_create_memory.reset_mock()
        self.mock_get_default_memory.reset_mock()
        
        # Create a memory manager without a collection name
        manager = MemoryManager(
            memory_type="test_memory",
            agent_id="test_agent"
        )
        
        # Check that the collection name was generated
        self.assertEqual(manager.collection_name, "agent_test_agent")
    
    def test_add(self):
        """Test adding a memory."""
        # Set up the mock
        self.memory.add.return_value = "test_memory_id"
        
        # Add a memory
        memory_id = self.manager.add(
            text="Test text",
            metadata={"key": "value"}
        )
        
        # Check that the memory was added
        self.assertEqual(memory_id, "test_memory_id")
        
        # Check that the memory's add method was called
        self.memory.add.assert_called_once_with(
            text="Test text",
            metadata={"key": "value", "agent_id": "test_agent"},
            collection_name="test_collection"
        )
    
    def test_retrieve(self):
        """Test retrieving memories."""
        # Set up the mock
        self.memory.retrieve.return_value = [
            ({"text": "Memory 1"}, 0.9),
            ({"text": "Memory 2"}, 0.8)
        ]
        
        # Retrieve memories
        results = self.manager.retrieve(
            query="Test query",
            n_results=2,
            filter_metadata={"key": "value"}
        )
        
        # Check that the memories were retrieved
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0]["text"], "Memory 1")
        self.assertEqual(results[0][1], 0.9)
        self.assertEqual(results[1][0]["text"], "Memory 2")
        self.assertEqual(results[1][1], 0.8)
        
        # Check that the memory's retrieve method was called
        self.memory.retrieve.assert_called_once_with(
            query="Test query",
            n_results=2,
            filter_metadata={"key": "value", "agent_id": "test_agent"},
            collection_name="test_collection"
        )
    
    def test_update(self):
        """Test updating a memory."""
        # Set up the mock
        self.memory.update.return_value = True
        
        # Update a memory
        success = self.manager.update(
            memory_id="test_memory_id",
            text="New text",
            metadata={"key": "new_value"}
        )
        
        # Check that the memory was updated
        self.assertTrue(success)
        
        # Check that the memory's update method was called
        self.memory.update.assert_called_once_with(
            memory_id="test_memory_id",
            text="New text",
            metadata={"key": "new_value"},
            collection_name="test_collection"
        )
    
    def test_delete(self):
        """Test deleting a memory."""
        # Set up the mock
        self.memory.delete.return_value = True
        
        # Delete a memory
        success = self.manager.delete(memory_id="test_memory_id")
        
        # Check that the memory was deleted
        self.assertTrue(success)
        
        # Check that the memory's delete method was called
        self.memory.delete.assert_called_once_with(
            memory_id="test_memory_id",
            collection_name="test_collection"
        )


if __name__ == '__main__':
    unittest.main()
