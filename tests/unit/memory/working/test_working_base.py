"""
Unit tests for base.

This module contains unit tests for the base module.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType
from augment_adam.memory.working.base import *

class TestWorkingMemoryItem(unittest.TestCase):
    """Tests for the WorkingMemoryItem class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.instance = WorkingMemoryItem(
            content="Test content",
            metadata={"key": "value"},
            ttl=3600  # 1 hour TTL
        )

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_init(self):
        """Test initialization of WorkingMemoryItem."""
        # Verify the instance was created correctly
        self.assertEqual(self.instance.content, "Test content")
        self.assertEqual(self.instance.metadata["key"], "value")
        self.assertEqual(self.instance.ttl, 3600)
        self.assertIsNotNone(self.instance.id)
        self.assertIsNotNone(self.instance.created_at)
        self.assertIsNotNone(self.instance.updated_at)

    def test_is_expired_not_expired(self):
        """Test is_expired when item is not expired."""
        # Item with 1 hour TTL should not be expired
        self.assertFalse(self.instance.is_expired())

    def test_is_expired_expired(self):
        """Test is_expired when item is expired."""
        # Create an item with an expiration date in the past
        import datetime
        past_time = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        expired_item = WorkingMemoryItem(
            content="Expired content",
            ttl=1,  # TTL must be > 0 for expires_at to be checked
            expires_at=past_time  # Set expires_at directly to a past time
        )
        self.assertTrue(expired_item.is_expired())

    def test_is_expired_no_ttl(self):
        """Test is_expired when item has no TTL."""
        # Create an item with TTL of 0 (should never expire)
        no_ttl_item = WorkingMemoryItem(
            content="No TTL content",
            ttl=0  # TTL of 0 means no expiration
        )
        self.assertFalse(no_ttl_item.is_expired())

    def test_to_dict(self):
        """Test to_dict method."""
        # Get dict representation
        item_dict = self.instance.to_dict()

        # Verify dict contains expected keys and values
        self.assertEqual(item_dict["content"], "Test content")
        self.assertEqual(item_dict["metadata"]["key"], "value")
        self.assertEqual(item_dict["ttl"], 3600)
        self.assertEqual(item_dict["id"], self.instance.id)
        self.assertIn("created_at", item_dict)
        self.assertIn("updated_at", item_dict)

    def test_from_dict(self):
        """Test from_dict method."""
        # Create a dict representation
        data = {
            "id": "test-id-123",
            "content": "Dict content",
            "metadata": {"source": "test"},
            "ttl": 7200,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T01:00:00Z"
        }

        # Create item from dict
        item = WorkingMemoryItem.from_dict(data)

        # Verify item was created correctly
        self.assertEqual(item.id, "test-id-123")
        self.assertEqual(item.content, "Dict content")
        self.assertEqual(item.metadata["source"], "test")
        self.assertEqual(item.ttl, 7200)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)

class TestWorkingMemory(unittest.TestCase):
    """Tests for the WorkingMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.memory = WorkingMemory(name="test_memory", capacity=100, cleanup_interval=60)

        # Add some test items
        self.item1 = WorkingMemoryItem(
            content="Test content 1",
            metadata={"priority": 1, "status": "pending", "task_id": "task-1"}
        )

        self.item2 = WorkingMemoryItem(
            content="Test content 2",
            metadata={"priority": 2, "status": "in_progress", "task_id": "task-2"}
        )

        self.item3 = WorkingMemoryItem(
            content="Test content 3",
            metadata={"priority": 3, "status": "completed", "task_id": "task-3"}
        )

        # Add items to memory
        self.memory.add(self.item1)
        self.memory.add(self.item2)
        self.memory.add(self.item3)

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_init(self):
        """Test initialization of WorkingMemory."""
        memory = WorkingMemory(name="test_init", capacity=50, cleanup_interval=30)

        self.assertEqual(memory.name, "test_init")
        self.assertEqual(memory.capacity, 50)
        self.assertEqual(memory.cleanup_interval, 30)
        self.assertEqual(memory.memory_type, MemoryType.WORKING)
        self.assertEqual(len(memory.items), 0)

    def test_add(self):
        """Test adding items to WorkingMemory."""
        # Create a new memory
        memory = WorkingMemory(name="test_add")

        # Add an item
        item = WorkingMemoryItem(content="Add test")
        result = memory.add(item)

        # Verify the item was added
        self.assertEqual(len(memory.items), 1)
        self.assertIn(item.id, memory.items)
        self.assertEqual(memory.items[item.id], item)
        self.assertEqual(result, item.id)

    def test_add_with_capacity_limit(self):
        """Test adding items when capacity is reached."""
        # Create a memory with capacity of 2
        memory = WorkingMemory(name="test_capacity", capacity=2)

        # Add 3 items (exceeding capacity)
        item1 = WorkingMemoryItem(content="Item 1")
        item2 = WorkingMemoryItem(content="Item 2")
        item3 = WorkingMemoryItem(content="Item 3")

        memory.add(item1)
        memory.add(item2)
        memory.add(item3)

        # Verify only the most recent 2 items are kept
        self.assertEqual(len(memory.items), 2)
        self.assertNotIn(item1.id, memory.items)
        self.assertIn(item2.id, memory.items)
        self.assertIn(item3.id, memory.items)

    def test_get(self):
        """Test getting items from WorkingMemory."""
        # Get an existing item
        result = self.memory.get(self.item2.id)

        # Verify the result
        self.assertEqual(result, self.item2)

        # Try to get a non-existent item
        result = self.memory.get("non-existent-id")

        # Verify the result is None
        self.assertIsNone(result)

    def test_update(self):
        """Test updating items in WorkingMemory."""
        # Update an existing item
        result = self.memory.update(
            self.item1.id,
            content="Updated content",
            metadata={"priority": 5, "status": "updated"}
        )

        # Verify the item was updated
        self.assertEqual(result.content, "Updated content")
        self.assertEqual(result.metadata["priority"], 5)
        self.assertEqual(result.metadata["status"], "updated")
        self.assertEqual(result.metadata["task_id"], "task-1")  # Original metadata preserved

        # Try to update a non-existent item
        result = self.memory.update("non-existent-id", content="Should not update")

        # Verify the result is None
        self.assertIsNone(result)

    def test_delete(self):
        """Test deleting items from WorkingMemory."""
        # Delete an existing item
        result = self.memory.remove(self.item3.id)

        # Verify the item was deleted
        self.assertTrue(result)
        self.assertEqual(len(self.memory.items), 2)
        self.assertNotIn(self.item3.id, self.memory.items)

        # Try to delete a non-existent item
        result = self.memory.remove("non-existent-id")

        # Verify the result is False
        self.assertFalse(result)

    def test_get_all(self):
        """Test getting all items from WorkingMemory."""
        # Get all items
        result = self.memory.get_all()

        # Verify the result
        self.assertEqual(len(result), 3)
        self.assertIn(self.item1, result)
        self.assertIn(self.item2, result)
        self.assertIn(self.item3, result)

    def test_get_by_task(self):
        """Test getting items by task ID."""
        # Set task_id directly on the items
        self.item1.task_id = "task-1"
        self.item2.task_id = "task-2"
        self.item3.task_id = "task-3"

        # Get items for task-2
        result = self.memory.get_by_task("task-2")

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.item2)

        # Try to get items for a non-existent task
        result = self.memory.get_by_task("non-existent-task")

        # Verify the result is an empty list
        self.assertEqual(result, [])

    def test_get_by_status(self):
        """Test getting items by status."""
        # Set status directly on the items
        self.item1.status = "pending"
        self.item2.status = "in_progress"
        self.item3.status = "completed"

        # Get items with status 'in_progress'
        result = self.memory.get_by_status("in_progress")

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.item2)

        # Try to get items with a non-existent status
        result = self.memory.get_by_status("non-existent-status")

        # Verify the result is an empty list
        self.assertEqual(result, [])

    def test_get_by_priority(self):
        """Test getting items by priority range."""
        # Set priority directly on the items
        self.item1.priority = 1
        self.item2.priority = 2
        self.item3.priority = 3

        # Get items with priority between 2 and 3
        result = self.memory.get_by_priority(min_priority=2, max_priority=3)

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertIn(self.item2, result)
        self.assertIn(self.item3, result)

        # Get items with priority greater than 2
        result = self.memory.get_by_priority(min_priority=3)

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.item3)

        # Get items with priority less than 2
        result = self.memory.get_by_priority(max_priority=1)

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.item1)

    def test_update_status(self):
        """Test updating item status."""
        # Update status of an existing item
        result = self.memory.update_status(self.item1.id, "in_review")

        # Verify the status was updated
        self.assertEqual(result.status, "in_review")

        # Try to update status of a non-existent item
        result = self.memory.update_status("non-existent-id", "should-not-update")

        # Verify the result is None
        self.assertIsNone(result)

    def test_update_priority(self):
        """Test updating item priority."""
        # Update priority of an existing item
        result = self.memory.update_priority(self.item1.id, 10)

        # Verify the priority was updated
        self.assertEqual(result.priority, 10)

        # Try to update priority of a non-existent item
        result = self.memory.update_priority("non-existent-id", 100)

        # Verify the result is None
        self.assertIsNone(result)

    def test_update_ttl(self):
        """Test updating item TTL."""
        # Update TTL of an existing item
        result = self.memory.update_ttl(self.item1.id, 7200)

        # Verify the TTL was updated
        self.assertEqual(result.ttl, 7200)

        # Try to update TTL of a non-existent item
        result = self.memory.update_ttl("non-existent-id", 7200)

        # Verify the result is None
        self.assertIsNone(result)

    def test_search(self):
        """Test searching for items."""
        # Search for items containing 'Test content 2'
        result = self.memory.search("Test content 2")

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.item2)

        # Search for items containing 'Test'
        result = self.memory.search("Test")

        # Verify the result (all items should match)
        self.assertEqual(len(result), 3)

        # Search with a limit
        result = self.memory.search("Test", limit=2)

        # Verify the result is limited
        self.assertEqual(len(result), 2)

        # Search for non-existent text
        result = self.memory.search("Non-existent text")

        # Verify the result is an empty list
        self.assertEqual(result, [])

    def test_cleanup_expired(self):
        """Test cleaning up expired items."""
        # Add an expired item
        import datetime
        past_time = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        expired_item = WorkingMemoryItem(
            content="Expired item",
            ttl=1,  # TTL must be > 0 for expires_at to be checked
            expires_at=past_time  # Set expires_at directly to a past time
        )
        self.memory.add(expired_item)

        # Verify the item was added
        self.assertEqual(len(self.memory.items), 4)

        # Run cleanup
        self.memory._cleanup()

        # Verify the expired item was removed
        self.assertEqual(len(self.memory.items), 3)
        self.assertNotIn(expired_item.id, self.memory.items)

    def test_to_dict(self):
        """Test converting WorkingMemory to dict."""
        # Convert to dict
        memory_dict = self.memory.to_dict()

        # Verify the dict contains expected keys and values
        self.assertEqual(memory_dict["name"], "test_memory")
        self.assertEqual(memory_dict["memory_type"], "WORKING")
        self.assertEqual(memory_dict["capacity"], 100)
        self.assertEqual(memory_dict["cleanup_interval"], 60)
        self.assertEqual(len(memory_dict["items"]), 3)

        # Verify items are included
        self.assertIn(self.item1.id, memory_dict["items"])
        self.assertIn(self.item2.id, memory_dict["items"])
        self.assertIn(self.item3.id, memory_dict["items"])

    def test_from_dict(self):
        """Test creating WorkingMemory from dict."""
        # Create a dict representation
        data = {
            "name": "from_dict_memory",
            "memory_type": "WORKING",
            "capacity": 200,
            "cleanup_interval": 120,
            "items": {
                "item-1": {
                    "id": "item-1",
                    "content": "Item 1 content",
                    "text": "Item 1 text",
                    "metadata": {"key": "value"},
                    "ttl": 3600
                },
                "item-2": {
                    "id": "item-2",
                    "content": "Item 2 content",
                    "text": "Item 2 text",
                    "metadata": {"key": "value"},
                    "ttl": 3600
                }
            }
        }

        # Create memory from dict
        memory = WorkingMemory.from_dict(data)

        # Verify memory was created correctly
        self.assertEqual(memory.name, "from_dict_memory")
        self.assertEqual(memory.memory_type, MemoryType.WORKING)
        self.assertEqual(memory.capacity, 200)
        self.assertEqual(memory.cleanup_interval, 120)
        self.assertEqual(len(memory.items), 2)
        self.assertIn("item-1", memory.items)
        self.assertIn("item-2", memory.items)
        self.assertEqual(memory.items["item-1"].content, "Item 1 content")
        self.assertEqual(memory.items["item-2"].content, "Item 2 content")


if __name__ == '__main__':
    unittest.main()
