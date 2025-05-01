"""
Unit tests for the Memory core functionality.

This module contains tests for the core functionality of the Memory system,
including memory storage, retrieval, and management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import Memory, MemoryItem, MemoryQuery, MemoryResult


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
    
    def test_memory_query_init(self):
        """Test initializing a MemoryQuery."""
        query = MemoryQuery(
            query="test query",
            max_results=10,
            filters={"source": "test"},
            include_metadata=True
        )
        
        assert query.query == "test query"
        assert query.max_results == 10
        assert query.filters == {"source": "test"}
        assert query.include_metadata is True
    
    def test_memory_result_init(self):
        """Test initializing a MemoryResult."""
        result = MemoryResult(
            item=MemoryItem(content="test content"),
            score=0.95
        )
        
        assert result.item.content == "test content"
        assert result.score == 0.95
    
    def test_memory_result_to_dict(self):
        """Test converting a MemoryResult to a dictionary."""
        result = MemoryResult(
            item=MemoryItem(
                content="test content",
                metadata={"source": "test"},
                id="test_id"
            ),
            score=0.95
        )
        
        result_dict = result.to_dict()
        assert result_dict["item"]["content"] == "test content"
        assert result_dict["item"]["metadata"] == {"source": "test"}
        assert result_dict["item"]["id"] == "test_id"
        assert result_dict["score"] == 0.95
    
    def test_memory_init(self):
        """Test initializing a Memory."""
        memory = Memory()
        
        assert memory.name == "base_memory"
        assert memory.items == {}
    
    def test_add_item(self):
        """Test adding an item to memory."""
        memory = Memory()
        item = MemoryItem(content="test content")
        
        memory.add_item(item)
        
        assert item.id in memory.items
        assert memory.items[item.id] == item
    
    def test_get_item(self):
        """Test getting an item from memory."""
        memory = Memory()
        item = MemoryItem(content="test content", id="test_id")
        memory.add_item(item)
        
        retrieved_item = memory.get_item("test_id")
        
        assert retrieved_item == item
    
    def test_get_item_nonexistent(self):
        """Test getting a nonexistent item from memory."""
        memory = Memory()
        
        retrieved_item = memory.get_item("nonexistent")
        
        assert retrieved_item is None
    
    def test_remove_item(self):
        """Test removing an item from memory."""
        memory = Memory()
        item = MemoryItem(content="test content", id="test_id")
        memory.add_item(item)
        
        memory.remove_item("test_id")
        
        assert "test_id" not in memory.items
    
    def test_remove_item_nonexistent(self):
        """Test removing a nonexistent item from memory."""
        memory = Memory()
        
        # Should not raise an exception
        memory.remove_item("nonexistent")
    
    def test_clear(self):
        """Test clearing memory."""
        memory = Memory()
        memory.add_item(MemoryItem(content="test content 1"))
        memory.add_item(MemoryItem(content="test content 2"))
        
        memory.clear()
        
        assert len(memory.items) == 0
    
    def test_get_all_items(self):
        """Test getting all items from memory."""
        memory = Memory()
        item1 = MemoryItem(content="test content 1")
        item2 = MemoryItem(content="test content 2")
        memory.add_item(item1)
        memory.add_item(item2)
        
        items = memory.get_all_items()
        
        assert len(items) == 2
        assert item1 in items
        assert item2 in items
    
    def test_search(self):
        """Test searching memory."""
        memory = Memory()
        
        # The base Memory class doesn't implement search
        with pytest.raises(NotImplementedError):
            memory.search("test query")
    
    def test_update_item(self):
        """Test updating an item in memory."""
        memory = Memory()
        item = MemoryItem(content="test content", id="test_id")
        memory.add_item(item)
        
        updated_item = MemoryItem(content="updated content", id="test_id")
        memory.update_item(updated_item)
        
        assert memory.items["test_id"].content == "updated content"
    
    def test_update_item_nonexistent(self):
        """Test updating a nonexistent item in memory."""
        memory = Memory()
        item = MemoryItem(content="test content", id="test_id")
        
        # Should add the item if it doesn't exist
        memory.update_item(item)
        
        assert "test_id" in memory.items
        assert memory.items["test_id"] == item
    
    def test_count(self):
        """Test counting items in memory."""
        memory = Memory()
        memory.add_item(MemoryItem(content="test content 1"))
        memory.add_item(MemoryItem(content="test content 2"))
        
        count = memory.count()
        
        assert count == 2
    
    def test_filter_items(self):
        """Test filtering items in memory."""
        memory = Memory()
        item1 = MemoryItem(content="test content 1", metadata={"source": "test1"})
        item2 = MemoryItem(content="test content 2", metadata={"source": "test2"})
        memory.add_item(item1)
        memory.add_item(item2)
        
        filtered_items = memory.filter_items({"source": "test1"})
        
        assert len(filtered_items) == 1
        assert item1 in filtered_items
        assert item2 not in filtered_items
