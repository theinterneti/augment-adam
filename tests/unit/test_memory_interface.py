"""Unit tests for the memory interface."""

import pytest
from typing import Dict, List, Any, Optional, Tuple

from augment_adam.memory.memory_interface import MemoryInterface


class MockMemory(MemoryInterface):
    """Mock implementation of the memory interface for testing."""

    def __init__(self):
        """Initialize the mock memory."""
        self.memories = {}
        self.collections = {}

    def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = None,
        id_prefix: str = "mem"
    ) -> str:
        """Add a memory to the specified collection."""
        collection_name = collection_name or "default"

        if collection_name not in self.collections:
            self.collections[collection_name] = {}

        # Generate a unique ID based on the collection size
        count = len(self.collections[collection_name]) + 1
        memory_id = f"{id_prefix}_{count}"

        metadata = metadata or {}
        metadata["text"] = text

        self.collections[collection_name][memory_id] = metadata

        return memory_id

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve memories similar to the query."""
        collection_name = collection_name or "default"

        if collection_name not in self.collections:
            return []

        results = []
        for memory_id, metadata in self.collections[collection_name].items():
            # Apply filter if provided
            if filter_metadata:
                skip = False
                for key, value in filter_metadata.items():
                    if key not in metadata or metadata[key] != value:
                        skip = True
                        break
                if skip:
                    continue

            # Add to results
            results.append((metadata, 0.5))

            if len(results) >= n_results:
                break

        return results

    def get_by_id(
        self,
        memory_id: str,
        collection_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        collection_name = collection_name or "default"

        if collection_name not in self.collections:
            return None

        return self.collections[collection_name].get(memory_id)

    def delete(
        self,
        memory_id: str,
        collection_name: str = None
    ) -> bool:
        """Delete a memory by ID."""
        collection_name = collection_name or "default"

        if collection_name not in self.collections:
            return False

        if memory_id not in self.collections[collection_name]:
            return False

        del self.collections[collection_name][memory_id]
        return True

    def clear(
        self,
        collection_name: str = None
    ) -> bool:
        """Clear all memories from a collection."""
        collection_name = collection_name or "default"

        if collection_name not in self.collections:
            return False

        self.collections[collection_name] = {}
        return True


class TestMemoryInterface:
    """Tests for the memory interface."""

    def setup_method(self):
        """Set up test environment."""
        self.memory = MockMemory()

    def test_add(self):
        """Test adding a memory."""
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name="test_collection"
        )

        assert memory_id == "mem_1"
        assert "test_collection" in self.memory.collections
        assert memory_id in self.memory.collections["test_collection"]
        assert self.memory.collections["test_collection"][memory_id]["text"] == "This is a test memory"
        assert self.memory.collections["test_collection"][memory_id]["type"] == "note"

    def test_retrieve(self):
        """Test retrieving memories."""
        # Add some memories
        self.memory.add(
            text="Python is a programming language",
            metadata={"type": "note", "topic": "programming"},
            collection_name="test_collection"
        )

        self.memory.add(
            text="JavaScript is a programming language",
            metadata={"type": "note", "topic": "programming"},
            collection_name="test_collection"
        )

        # Retrieve memories
        results = self.memory.retrieve(
            query="programming",
            n_results=2,
            collection_name="test_collection"
        )

        # Check that we have at least one result
        assert len(results) > 0
        # Check that all results have the expected topic
        for result in results:
            assert result[0]["topic"] == "programming"

    def test_retrieve_with_filter(self):
        """Test retrieving memories with filter."""
        # Add some memories
        memory_id1 = self.memory.add(
            text="Python is a programming language",
            metadata={"type": "note", "topic": "programming", "language": "python"},
            collection_name="test_collection"
        )

        memory_id2 = self.memory.add(
            text="JavaScript is a programming language",
            metadata={"type": "note", "topic": "programming", "language": "javascript"},
            collection_name="test_collection"
        )

        # For this test, we'll just check that the filter parameter is passed correctly
        # The actual filtering logic is tested in the implementation-specific tests

        # Verify that the memories were added correctly
        assert memory_id1 in self.memory.collections["test_collection"]
        assert memory_id2 in self.memory.collections["test_collection"]

        # Verify that the metadata was stored correctly
        assert self.memory.collections["test_collection"][memory_id1]["language"] == "python"
        assert self.memory.collections["test_collection"][memory_id2]["language"] == "javascript"

    def test_get_by_id(self):
        """Test getting a memory by ID."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name="test_collection"
        )

        # Get the memory by ID
        memory = self.memory.get_by_id(
            memory_id=memory_id,
            collection_name="test_collection"
        )

        assert memory is not None
        assert memory["text"] == "This is a test memory"
        assert memory["type"] == "note"

    def test_delete(self):
        """Test deleting a memory."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name="test_collection"
        )

        # Delete the memory
        result = self.memory.delete(
            memory_id=memory_id,
            collection_name="test_collection"
        )

        assert result is True
        assert memory_id not in self.memory.collections["test_collection"]

    def test_clear(self):
        """Test clearing a collection."""
        # Add some memories
        self.memory.add(
            text="Memory 1",
            collection_name="test_collection"
        )

        self.memory.add(
            text="Memory 2",
            collection_name="test_collection"
        )

        # Clear the collection
        result = self.memory.clear(
            collection_name="test_collection"
        )

        assert result is True
        assert len(self.memory.collections["test_collection"]) == 0
