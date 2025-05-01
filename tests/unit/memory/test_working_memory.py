"""
Unit tests for the Working Memory system.

This module contains tests for the Working Memory system, including memory
storage, retrieval, and management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import MemoryItem, MemoryType
from augment_adam.memory.working.working_memory import WorkingMemory


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
        assert working_memory.metadata == {}
        assert working_memory.capacity == 100
        assert working_memory.decay_rate == 0.1
        assert working_memory.activation_threshold == 0.2

    def test_add(self, working_memory):
        """Test adding an item to working memory."""
        # Create an item
        item = MemoryItem(content="test content")

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
        item = MemoryItem(content="test content", importance=0.8)

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
        item1 = MemoryItem(content="test content 1", importance=0.5)
        item2 = MemoryItem(content="test content 2", importance=0.3)
        item3 = MemoryItem(content="test content 3", importance=0.7)

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
        item = MemoryItem(content="test content")
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
        item = MemoryItem(content="test content")
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
        item = MemoryItem(content="test content")
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
        item1 = MemoryItem(content="test content 1")
        item2 = MemoryItem(content="test content 2")
        working_memory.add(item1)
        working_memory.add(item2)

        # Clear the memory
        working_memory.clear()

        # Check that the memory is empty
        assert len(working_memory.items) == 0

    def test_search(self, working_memory):
        """Test searching working memory."""
        # Create and add items
        item1 = MemoryItem(content="apple banana")
        item2 = MemoryItem(content="banana cherry")
        item3 = MemoryItem(content="cherry date")
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
        item1 = MemoryItem(content="apple banana")
        item2 = MemoryItem(content="banana cherry")
        item3 = MemoryItem(content="cherry date")
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Search for "cherry" with a limit of 1
        results = working_memory.search("cherry", limit=1)

        # Check the results
        assert len(results) == 1
        assert results[0].content in ["banana cherry", "cherry date"]

    def test_decay(self, working_memory):
        """Test memory decay in working memory."""
        # Create and add items
        item1 = MemoryItem(content="test content 1", importance=0.5)
        item2 = MemoryItem(content="test content 2", importance=0.3)
        working_memory.add(item1)
        working_memory.add(item2)

        # Apply decay
        working_memory.decay()

        # Check that the importance values were reduced
        assert working_memory.items[item1.id].importance == 0.5 - working_memory.decay_rate
        assert working_memory.items[item2.id].importance == 0.3 - working_memory.decay_rate

    def test_decay_below_threshold(self, working_memory):
        """Test memory decay below threshold in working memory."""
        # Set a high decay rate
        working_memory.decay_rate = 0.3

        # Create and add items
        item1 = MemoryItem(content="test content 1", importance=0.5)
        item2 = MemoryItem(content="test content 2", importance=0.3)
        working_memory.add(item1)
        working_memory.add(item2)

        # Apply decay
        working_memory.decay()

        # Check that item1 was kept (importance = 0.5 - 0.3 = 0.2, which is at the threshold)
        assert item1.id in working_memory.items
        assert working_memory.items[item1.id].importance == 0.2

        # Check that item2 was removed (importance = 0.3 - 0.3 = 0.0, which is below the threshold)
        assert item2.id not in working_memory.items

    def test_activate(self, working_memory):
        """Test activating an item in working memory."""
        # Create and add an item
        item = MemoryItem(content="test content", importance=0.5)
        working_memory.add(item)

        # Activate the item
        working_memory.activate(item.id, 0.2)

        # Check that the importance was increased
        assert working_memory.items[item.id].importance == 0.7  # 0.5 + 0.2

    def test_activate_nonexistent(self, working_memory):
        """Test activating a nonexistent item in working memory."""
        # Activate a nonexistent item
        result = working_memory.activate("nonexistent", 0.2)

        # Check that False was returned
        assert result is False

    def test_get_most_important(self, working_memory):
        """Test getting the most important items from working memory."""
        # Create and add items
        item1 = MemoryItem(content="test content 1", importance=0.5)
        item2 = MemoryItem(content="test content 2", importance=0.3)
        item3 = MemoryItem(content="test content 3", importance=0.7)
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Get the most important items
        items = working_memory.get_most_important(2)

        # Check the items
        assert len(items) == 2
        assert items[0].importance == 0.7  # item3
        assert items[1].importance == 0.5  # item1

    def test_get_least_important(self, working_memory):
        """Test getting the least important items from working memory."""
        # Create and add items
        item1 = MemoryItem(content="test content 1", importance=0.5)
        item2 = MemoryItem(content="test content 2", importance=0.3)
        item3 = MemoryItem(content="test content 3", importance=0.7)
        working_memory.add(item1)
        working_memory.add(item2)
        working_memory.add(item3)

        # Get the least important items
        items = working_memory.get_least_important(2)

        # Check the items
        assert len(items) == 2
        assert items[0].importance == 0.3  # item2
        assert items[1].importance == 0.5  # item1
