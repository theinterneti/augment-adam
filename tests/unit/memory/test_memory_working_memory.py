"""
Unit tests for the Working Memory system.

This module contains tests for the Working Memory system, including memory
storage, retrieval, and management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import MemoryItem, MemoryType
from augment_adam.memory.working.base import WorkingMemory, WorkingMemoryItem


class TestWorkingMemory:
    """Tests for the Working Memory system."""

    @pytest.fixture
    def working_memory(self):
        """Create a WorkingMemory for testing."""
        return WorkingMemory(name="test_working_memory")

    def test_init(self, working_memory):
        """Test initializing a WorkingMemory."""
        assert working_memory.name == "test_working_memory"
        assert working_memory.memory_type == MemoryType.WORKING
        assert working_memory.items == {}
        assert "capacity" in working_memory.metadata
        assert "cleanup_interval" in working_memory.metadata
        assert working_memory.capacity == 0
        assert working_memory.cleanup_interval == 60

    def test_add(self, working_memory):
        """Test adding an item to working memory."""
        # Create an item
        item = WorkingMemoryItem(content="test content")

        # Add the item
        item_id = working_memory.add(item)

        # Check that the item was added
        assert item_id == item.id
        assert item.id in working_memory.items
        assert working_memory.items[item.id] == item
        assert working_memory.items[item.id].importance == 0.5  # Default importance

    def test_add_with_importance(self, working_memory):
        """Test adding an item with importance to working memory."""
        # Create an item with importance
        item = WorkingMemoryItem(content="test content", importance=0.8)

        # Add the item
        item_id = working_memory.add(item)

        # Check that the item was added with the correct importance
        assert item_id == item.id
        assert item.id in working_memory.items
        assert working_memory.items[item.id] == item
        assert working_memory.items[item.id].importance == 0.8

    def test_add_over_capacity(self, working_memory):
        """Test adding items over capacity to working memory."""
        # Set a small capacity
        working_memory.capacity = 2

        # Create items
        item1 = WorkingMemoryItem(content="test content 1", importance=0.5)
        item2 = WorkingMemoryItem(content="test content 2", importance=0.3)
        item3 = WorkingMemoryItem(content="test content 3", importance=0.7)

        # Add the items
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Check that only the most important items were kept
        assert len(working_memory.items) == 2
        assert item1.id in working_memory.items  # Importance 0.5
        assert item3.id in working_memory.items  # Importance 0.7
        assert item2.id not in working_memory.items  # Importance 0.3 (lowest)

    def test_get(self, working_memory):
        """Test getting an item from working memory."""
        # Create and add an item
        item = WorkingMemoryItem(content="test content")
        working_memory.add(item)

        # Get the item
        retrieved_item = working_memory.get(item.id)

        # Check that the correct item was retrieved
        assert retrieved_item == item

    def test_get_nonexistent(self, working_memory):
        """Test getting a nonexistent item from working memory."""
        # Get a nonexistent item
        retrieved_item = working_memory.get("nonexistent")

        # Check that None was returned
        assert retrieved_item is None

    def test_update(self, working_memory):
        """Test updating an item in working memory."""
        # Create and add an item
        item = WorkingMemoryItem(content="test content")
        working_memory.add(item)

        # Update the item
        updated_item = working_memory.update(item.id, content="updated content")

        # Check that the item was updated
        assert updated_item == item
        assert updated_item.content == "updated content"

    def test_update_nonexistent(self, working_memory):
        """Test updating a nonexistent item in working memory."""
        # Update a nonexistent item
        updated_item = working_memory.update("nonexistent", content="updated content")

        # Check that None was returned
        assert updated_item is None

    def test_remove(self, working_memory):
        """Test removing an item from working memory."""
        # Create and add an item
        item = WorkingMemoryItem(content="test content")
        working_memory.add(item)

        # Remove the item
        result = working_memory.remove(item.id)

        # Check that the item was removed
        assert result is True
        assert item.id not in working_memory.items

    def test_remove_nonexistent(self, working_memory):
        """Test removing a nonexistent item from working memory."""
        # Remove a nonexistent item
        result = working_memory.remove("nonexistent")

        # Check that False was returned
        assert result is False

    def test_clear(self, working_memory):
        """Test clearing working memory."""
        # Create and add items
        item1 = WorkingMemoryItem(content="test content 1")
        item2 = WorkingMemoryItem(content="test content 2")
        working_memory.add(item1)
        working_memory.add(item2)

        # Clear the memory
        working_memory.clear()

        # Check that the memory is empty
        assert len(working_memory.items) == 0

    def test_search(self, working_memory):
        """Test searching working memory."""
        # Create and add items
        item1 = WorkingMemoryItem(content="apple banana")
        item2 = WorkingMemoryItem(content="banana cherry")
        item3 = WorkingMemoryItem(content="cherry date")
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Search for "banana"
        results = working_memory.search("banana")

        # Check the results
        assert len(results) == 2
        assert any(item.content == "apple banana" for item in results)
        assert any(item.content == "banana cherry" for item in results)
        assert not any(item.content == "cherry date" for item in results)

    def test_search_with_limit(self, working_memory):
        """Test searching working memory with a limit."""
        # Create and add items
        item1 = WorkingMemoryItem(content="apple banana")
        item2 = WorkingMemoryItem(content="banana cherry")
        item3 = WorkingMemoryItem(content="cherry date")
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Search for "cherry" with a limit of 1
        results = working_memory.search("cherry", limit=1)

        # Check the results
        assert len(results) == 1
        assert results[0].content in ["banana cherry", "cherry date"]

    def test_update_status(self, working_memory):
        """Test updating the status of an item in working memory."""
        # Create and add an item
        item = WorkingMemoryItem(content="test content", status="active")
        working_memory.add(item)

        # Update the status
        updated_item = working_memory.update_status(item.id, "completed")

        # Check that the status was updated
        assert updated_item == item
        assert updated_item.status == "completed"

    def test_update_priority(self, working_memory):
        """Test updating the priority of an item in working memory."""
        # Create and add an item
        item = WorkingMemoryItem(content="test content", priority=5)
        working_memory.add(item)

        # Update the priority
        updated_item = working_memory.update_priority(item.id, 8)

        # Check that the priority was updated
        assert updated_item == item
        assert updated_item.priority == 8

    def test_update_ttl(self, working_memory):
        """Test updating the time-to-live of an item in working memory."""
        # Create and add an item
        item = WorkingMemoryItem(content="test content", ttl=0)
        working_memory.add(item)

        # Update the TTL
        updated_item = working_memory.update_ttl(item.id, 3600)  # 1 hour

        # Check that the TTL was updated
        assert updated_item == item
        assert updated_item.ttl == 3600
        assert updated_item.expires_at is not None

    def test_get_by_task(self, working_memory):
        """Test getting items by task ID."""
        # Create and add items
        item1 = WorkingMemoryItem(content="test content 1", task_id="task1")
        item2 = WorkingMemoryItem(content="test content 2", task_id="task1")
        item3 = WorkingMemoryItem(content="test content 3", task_id="task2")
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Get items by task ID
        items = working_memory.get_by_task("task1")

        # Check the items
        assert len(items) == 2
        assert any(item.id == item1.id for item in items)
        assert any(item.id == item2.id for item in items)
        assert not any(item.id == item3.id for item in items)

    def test_get_by_status(self, working_memory):
        """Test getting items by status."""
        # Create and add items
        item1 = WorkingMemoryItem(content="test content 1", status="active")
        item2 = WorkingMemoryItem(content="test content 2", status="active")
        item3 = WorkingMemoryItem(content="test content 3", status="completed")
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Get items by status
        items = working_memory.get_by_status("active")

        # Check the items
        assert len(items) == 2
        assert any(item.id == item1.id for item in items)
        assert any(item.id == item2.id for item in items)
        assert not any(item.id == item3.id for item in items)

    def test_get_by_priority(self, working_memory):
        """Test getting items by priority range."""
        # Create and add items
        item1 = WorkingMemoryItem(content="test content 1", priority=3)
        item2 = WorkingMemoryItem(content="test content 2", priority=5)
        item3 = WorkingMemoryItem(content="test content 3", priority=8)
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Get items by priority range
        items = working_memory.get_by_priority(min_priority=4, max_priority=7)

        # Check the items
        assert len(items) == 1
        assert items[0].id == item2.id  # Only item2 has priority in range 4-7
