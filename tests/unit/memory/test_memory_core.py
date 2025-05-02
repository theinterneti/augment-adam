"""
Unit tests for the Memory core functionality.

This module contains tests for the core functionality of the Memory system,
including memory storage, retrieval, and management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType, MemoryManager


class TestMemory:
    """Tests for the Memory system."""

    def test_memory_item_init(self):
        """Test initializing a MemoryItem."""
        item = MemoryItem(
            content="test content",
            metadata={"source": "test", "timestamp": 123456789},
            embedding=[0.1, 0.2, 0.3]
        )

        assert item.content == "test content"
        assert item.metadata == {"source": "test", "timestamp": 123456789}
        assert item.embedding == [0.1, 0.2, 0.3]
        assert item.id is not None

    def test_memory_item_to_dict(self):
        """Test converting a MemoryItem to a dictionary."""
        item = MemoryItem(
            content="test content",
            metadata={"source": "test", "timestamp": 123456789},
            embedding=[0.1, 0.2, 0.3],
            id="test_id"
        )

        item_dict = item.to_dict()
        assert item_dict["content"] == "test content"
        assert item_dict["metadata"] == {"source": "test", "timestamp": 123456789}
        assert item_dict["embedding"] == [0.1, 0.2, 0.3]
        assert item_dict["id"] == "test_id"

    def test_memory_item_from_dict(self):
        """Test creating a MemoryItem from a dictionary."""
        data = {
            "id": "test_id",
            "content": "test content",
            "metadata": {"source": "test", "timestamp": 123456789},
            "embedding": [0.1, 0.2, 0.3],
            "importance": 0.8
        }

        item = MemoryItem.from_dict(data)
        assert item.id == "test_id"
        assert item.content == "test content"
        assert item.metadata == {"source": "test", "timestamp": 123456789}
        assert item.embedding == [0.1, 0.2, 0.3]
        assert item.importance == 0.8

    def test_memory_item_update(self):
        """Test updating a MemoryItem."""
        item = MemoryItem(
            content="test content",
            metadata={"source": "test"}
        )

        item.update(content="updated content", metadata={"key": "value"})

        assert item.content == "updated content"
        assert item.metadata == {"source": "test", "key": "value"}

    def test_memory_item_is_expired(self):
        """Test checking if a MemoryItem is expired."""
        import datetime

        # Create an item that expires in the past
        past = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        expired_item = MemoryItem(expires_at=past)

        # Create an item that expires in the future
        future = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        not_expired_item = MemoryItem(expires_at=future)

        # Create an item with no expiration
        no_expiration_item = MemoryItem()

        assert expired_item.is_expired() is True
        assert not_expired_item.is_expired() is False
        assert no_expiration_item.is_expired() is False

    # Create a concrete implementation of Memory for testing
    class TestMemoryImpl(Memory):
        def __init__(self):
            super().__init__(name="test_memory", memory_type=MemoryType.VECTOR)

        def search(self, query, limit=10):
            # Simple implementation for testing
            return list(self.items.values())[:limit]

    def test_memory_init(self):
        """Test initializing a Memory."""
        memory = self.TestMemoryImpl()

        assert memory.name == "test_memory"
        assert memory.memory_type == MemoryType.VECTOR
        assert memory.items == {}
        assert memory.metadata == {}

    def test_add(self):
        """Test adding an item to memory."""
        memory = self.TestMemoryImpl()
        item = MemoryItem(content="test content")

        item_id = memory.add(item)

        assert item_id == item.id
        assert item.id in memory.items
        assert memory.items[item.id] == item

    def test_get(self):
        """Test getting an item from memory."""
        memory = self.TestMemoryImpl()
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)

        retrieved_item = memory.get("test_id")

        assert retrieved_item == item

    def test_get_nonexistent(self):
        """Test getting a nonexistent item from memory."""
        memory = self.TestMemoryImpl()

        retrieved_item = memory.get("nonexistent")

        assert retrieved_item is None

    def test_update(self):
        """Test updating an item in memory."""
        memory = self.TestMemoryImpl()
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)

        updated_item = memory.update("test_id", content="updated content")

        assert updated_item == item
        assert updated_item.content == "updated content"

    def test_update_nonexistent(self):
        """Test updating a nonexistent item in memory."""
        memory = self.TestMemoryImpl()

        updated_item = memory.update("nonexistent", content="updated content")

        assert updated_item is None

    def test_remove(self):
        """Test removing an item from memory."""
        memory = self.TestMemoryImpl()
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)

        result = memory.remove("test_id")

        assert result is True
        assert "test_id" not in memory.items

    def test_remove_nonexistent(self):
        """Test removing a nonexistent item from memory."""
        memory = self.TestMemoryImpl()

        result = memory.remove("nonexistent")

        assert result is False

    def test_clear(self):
        """Test clearing memory."""
        memory = self.TestMemoryImpl()
        memory.add(MemoryItem(content="test content 1"))
        memory.add(MemoryItem(content="test content 2"))

        memory.clear()

        assert len(memory.items) == 0

    def test_get_all(self):
        """Test getting all items from memory."""
        memory = self.TestMemoryImpl()
        item1 = MemoryItem(content="test content 1")
        item2 = MemoryItem(content="test content 2")
        memory.add(item1)
        memory.add(item2)

        items = memory.get_all()

        assert len(items) == 2
        assert item1 in items
        assert item2 in items

    def test_count(self):
        """Test counting items in memory."""
        memory = self.TestMemoryImpl()
        memory.add(MemoryItem(content="test content 1"))
        memory.add(MemoryItem(content="test content 2"))

        count = memory.count()

        assert count == 2

    def test_filter(self):
        """Test filtering items in memory."""
        memory = self.TestMemoryImpl()
        item1 = MemoryItem(content="test content 1", metadata={"source": "test1"})
        item2 = MemoryItem(content="test content 2", metadata={"source": "test2"})
        memory.add(item1)
        memory.add(item2)

        filtered_items = memory.filter(lambda item: item.metadata.get("source") == "test1")

        assert len(filtered_items) == 1
        assert item1 in filtered_items
        assert item2 not in filtered_items

    def test_set_get_metadata(self):
        """Test setting and getting metadata."""
        memory = self.TestMemoryImpl()

        memory.set_metadata("key", "value")

        assert memory.get_metadata("key") == "value"
        assert memory.get_metadata("nonexistent") is None
        assert memory.get_metadata("nonexistent", "default") == "default"

    def test_search(self):
        """Test searching memory."""
        memory = self.TestMemoryImpl()
        item1 = MemoryItem(content="test content 1")
        item2 = MemoryItem(content="test content 2")
        memory.add(item1)
        memory.add(item2)

        results = memory.search("test query")

        assert len(results) == 2
        assert item1 in results
        assert item2 in results

    def test_to_dict(self):
        """Test converting a Memory to a dictionary."""
        memory = self.TestMemoryImpl()
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)
        memory.set_metadata("key", "value")

        memory_dict = memory.to_dict()

        assert memory_dict["name"] == "test_memory"
        assert memory_dict["memory_type"] == "VECTOR"
        assert "test_id" in memory_dict["items"]
        assert memory_dict["items"]["test_id"]["content"] == "test content"
        assert memory_dict["metadata"] == {"key": "value"}


class TestMemoryManager:
    """Tests for the Memory Manager."""

    # Create a concrete implementation of Memory for testing
    class TestMemoryImpl(Memory):
        def __init__(self, name="test_memory"):
            super().__init__(name=name, memory_type=MemoryType.VECTOR)

        def search(self, query, limit=10):
            # Simple implementation for testing
            return list(self.items.values())[:limit]

    def test_memory_manager_init(self):
        """Test initializing a MemoryManager."""
        manager = MemoryManager()

        assert manager.memories == {}
        assert manager.metadata == {}

    def test_register_memory(self):
        """Test registering a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()

        manager.register_memory(memory)

        assert memory.name in manager.memories
        assert manager.memories[memory.name] == memory

    def test_unregister_memory(self):
        """Test unregistering a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)

        result = manager.unregister_memory(memory.name)

        assert result is True
        assert memory.name not in manager.memories

    def test_unregister_memory_nonexistent(self):
        """Test unregistering a nonexistent memory system."""
        manager = MemoryManager()

        result = manager.unregister_memory("nonexistent")

        assert result is False

    def test_get_memory(self):
        """Test getting a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)

        retrieved_memory = manager.get_memory(memory.name)

        assert retrieved_memory == memory

    def test_get_memory_nonexistent(self):
        """Test getting a nonexistent memory system."""
        manager = MemoryManager()

        retrieved_memory = manager.get_memory("nonexistent")

        assert retrieved_memory is None

    def test_get_memories_by_type(self):
        """Test getting memory systems by type."""
        manager = MemoryManager()
        memory1 = self.TestMemoryImpl(name="memory1")
        memory2 = self.TestMemoryImpl(name="memory2")
        manager.register_memory(memory1)
        manager.register_memory(memory2)

        memories = manager.get_memories_by_type(MemoryType.VECTOR)

        assert len(memories) == 2
        assert memory1 in memories
        assert memory2 in memories

    def test_get_all_memories(self):
        """Test getting all memory systems."""
        manager = MemoryManager()
        memory1 = self.TestMemoryImpl(name="memory1")
        memory2 = self.TestMemoryImpl(name="memory2")
        manager.register_memory(memory1)
        manager.register_memory(memory2)

        memories = manager.get_all_memories()

        assert len(memories) == 2
        assert memory1 in memories
        assert memory2 in memories

    def test_add_item(self):
        """Test adding an item to a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)
        item = MemoryItem(content="test content")

        item_id = manager.add_item(memory.name, item)

        assert item_id == item.id
        assert item.id in memory.items
        assert memory.items[item.id] == item

    def test_add_item_nonexistent_memory(self):
        """Test adding an item to a nonexistent memory system."""
        manager = MemoryManager()
        item = MemoryItem(content="test content")

        item_id = manager.add_item("nonexistent", item)

        assert item_id is None

    def test_get_item(self):
        """Test getting an item from a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)

        retrieved_item = manager.get_item(memory.name, item.id)

        assert retrieved_item == item

    def test_get_item_nonexistent_memory(self):
        """Test getting an item from a nonexistent memory system."""
        manager = MemoryManager()

        retrieved_item = manager.get_item("nonexistent", "test_id")

        assert retrieved_item is None

    def test_update_item(self):
        """Test updating an item in a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)

        updated_item = manager.update_item(memory.name, item.id, content="updated content")

        assert updated_item == item
        assert updated_item.content == "updated content"

    def test_update_item_nonexistent_memory(self):
        """Test updating an item in a nonexistent memory system."""
        manager = MemoryManager()

        updated_item = manager.update_item("nonexistent", "test_id", content="updated content")

        assert updated_item is None

    def test_remove_item(self):
        """Test removing an item from a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)
        item = MemoryItem(content="test content", id="test_id")
        memory.add(item)

        result = manager.remove_item(memory.name, item.id)

        assert result is True
        assert item.id not in memory.items

    def test_remove_item_nonexistent_memory(self):
        """Test removing an item from a nonexistent memory system."""
        manager = MemoryManager()

        result = manager.remove_item("nonexistent", "test_id")

        assert result is False

    def test_search(self):
        """Test searching a memory system."""
        manager = MemoryManager()
        memory = self.TestMemoryImpl()
        manager.register_memory(memory)
        item1 = MemoryItem(content="test content 1")
        item2 = MemoryItem(content="test content 2")
        memory.add(item1)
        memory.add(item2)

        results = manager.search(memory.name, "test query")

        assert len(results) == 2
        assert item1 in results
        assert item2 in results

    def test_search_nonexistent_memory(self):
        """Test searching a nonexistent memory system."""
        manager = MemoryManager()

        results = manager.search("nonexistent", "test query")

        assert results == []
