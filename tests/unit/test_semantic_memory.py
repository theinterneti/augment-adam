"""Tests for the semantic memory module.

This module contains tests for the semantic memory functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import tempfile
import time
import uuid
from unittest.mock import patch, MagicMock

import pytest
import chromadb
import numpy as np

# Ensure compatibility with NumPy 2.0+
if not hasattr(np, 'float_'):
    np.float_ = np.float64

from dukat.memory.semantic import Concept, SemanticMemory


def test_concept_init():
    """Test that a concept initializes correctly."""
    # Create a concept with minimal arguments
    concept = Concept(
        name="Test Concept",
        description="A test concept",
        content="This is a test concept with detailed content",
    )

    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"
    assert concept.id.startswith("con_")
    assert isinstance(concept.timestamp, int)
    assert concept.updated_at == concept.timestamp
    assert concept.metadata == {}

    # Create a concept with all arguments
    timestamp = int(time.time()) - 100
    updated_at = int(time.time())
    metadata = {"key": "value"}
    concept_id = f"con_{uuid.uuid4().hex[:8]}"

    concept = Concept(
        name="Another Test Concept",
        description="Another test concept",
        content="This is another test concept with detailed content",
        timestamp=timestamp,
        updated_at=updated_at,
        metadata=metadata,
        concept_id=concept_id,
    )

    assert concept.name == "Another Test Concept"
    assert concept.description == "Another test concept"
    assert concept.content == "This is another test concept with detailed content"
    assert concept.id == concept_id
    assert concept.timestamp == timestamp
    assert concept.updated_at == updated_at
    assert concept.metadata == metadata


def test_concept_to_dict():
    """Test that a concept converts to a dictionary correctly."""
    timestamp = int(time.time()) - 100
    updated_at = int(time.time())
    metadata = {"key": "value"}
    concept_id = f"con_{uuid.uuid4().hex[:8]}"

    concept = Concept(
        name="Test Concept",
        description="A test concept",
        content="This is a test concept with detailed content",
        timestamp=timestamp,
        updated_at=updated_at,
        metadata=metadata,
        concept_id=concept_id,
    )

    data = concept.to_dict()

    assert data["name"] == "Test Concept"
    assert data["description"] == "A test concept"
    assert data["content"] == "This is a test concept with detailed content"
    assert data["id"] == concept_id
    assert data["timestamp"] == timestamp
    assert data["updated_at"] == updated_at
    assert data["metadata"] == metadata


def test_concept_from_dict():
    """Test that a concept is created from a dictionary correctly."""
    timestamp = int(time.time()) - 100
    updated_at = int(time.time())
    metadata = {"key": "value"}
    concept_id = f"con_{uuid.uuid4().hex[:8]}"

    data = {
        "name": "Test Concept",
        "description": "A test concept",
        "content": "This is a test concept with detailed content",
        "id": concept_id,
        "timestamp": timestamp,
        "updated_at": updated_at,
        "metadata": metadata,
    }

    concept = Concept.from_dict(data)

    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"
    assert concept.id == concept_id
    assert concept.timestamp == timestamp
    assert concept.updated_at == updated_at
    assert concept.metadata == metadata


def test_concept_str():
    """Test that a concept converts to a string correctly."""
    concept = Concept(
        name="Test Concept",
        description="A test concept",
        content="This is a test concept with detailed content",
    )

    assert str(concept) == f"Test Concept ({concept.id}): A test concept"


# Mock ChromaDB for testing
@pytest.fixture
def mock_chroma_collection():
    """Create a mock ChromaDB collection."""
    mock_collection = MagicMock()

    # Mock add method
    mock_collection.add.return_value = None

    # Mock get method
    mock_collection.get.return_value = {
        "ids": ["con_12345678"],
        "documents": ["This is a test concept with detailed content"],
        "metadatas": [{
            "name": "Test Concept",
            "description": "A test concept",
            "timestamp": int(time.time()),
            "updated_at": int(time.time()),
            "key": "value",
        }],
    }

    # Mock query method
    mock_collection.query.return_value = {
        "ids": [["con_12345678"]],
        "documents": [["This is a test concept with detailed content"]],
        "metadatas": [[{
            "name": "Test Concept",
            "description": "A test concept",
            "timestamp": int(time.time()),
            "updated_at": int(time.time()),
            "key": "value",
        }]],
        "distances": [[0.5]],
    }

    # Mock delete method
    mock_collection.delete.return_value = None

    # Mock update method
    mock_collection.update.return_value = None

    return mock_collection


@pytest.fixture
def mock_chroma_client(mock_chroma_collection):
    """Create a mock ChromaDB client."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_chroma_collection
    return mock_client


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_init(mock_client_class, mock_chroma_client):
    """Test that semantic memory initializes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create semantic memory
        memory = SemanticMemory(persist_dir=temp_dir)

        # Check that the directory was created
        assert os.path.exists(temp_dir)

        # Check that the client was initialized correctly
        mock_client_class.assert_called_once_with(
            path=temp_dir,
            settings=pytest.approx(chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )),
        )

        # Check that the collection was created
        mock_chroma_client.get_or_create_collection.assert_called_once_with(
            name="dukat_concepts",
            metadata={"description": "Semantic memory collection for Dukat"},
        )

        # Check that the collection was stored
        assert memory.collection == mock_chroma_client.get_or_create_collection.return_value


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_add_concept(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory adds concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Add a concept
    concept = memory.add_concept(
        name="Test Concept",
        description="A test concept",
        content="This is a test concept with detailed content",
        metadata={"key": "value"},
    )

    # Check that the concept was created correctly
    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"
    assert "key" in concept.metadata
    assert concept.metadata["key"] == "value"

    # Check that the concept was added to the collection
    mock_chroma_collection.add.assert_called_once()
    args, kwargs = mock_chroma_collection.add.call_args

    assert kwargs["documents"] == [
        "This is a test concept with detailed content"]
    assert kwargs["ids"] == [concept.id]
    assert kwargs["metadatas"][0]["name"] == "Test Concept"
    assert kwargs["metadatas"][0]["description"] == "A test concept"
    assert "timestamp" in kwargs["metadatas"][0]
    assert "updated_at" in kwargs["metadatas"][0]
    assert kwargs["metadatas"][0]["key"] == "value"

    # Test adding a concept with empty name
    with pytest.raises(ValueError):
        memory.add_concept(
            name="", description="A test concept", content="Content")

    # Test adding a concept with empty description
    with pytest.raises(ValueError):
        memory.add_concept(name="Test", description="", content="Content")

    # Test adding a concept with empty content
    with pytest.raises(ValueError):
        memory.add_concept(
            name="Test", description="A test concept", content="")


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_get_concept(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory retrieves concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Get a concept
    concept = memory.get_concept("con_12345678")

    # Check that the concept was retrieved correctly
    assert concept is not None
    assert concept.id == "con_12345678"
    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"
    assert "key" in concept.metadata
    assert concept.metadata["key"] == "value"

    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        ids=["con_12345678"],
        include=["documents", "metadatas"],
    )

    # Test getting a non-existent concept
    mock_chroma_collection.get.return_value = {
        "ids": [], "documents": [], "metadatas": []}
    concept = memory.get_concept("nonexistent")
    assert concept is None


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_search_concepts(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory searches concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Search for concepts
    concepts = memory.search_concepts("test query")

    # Check that the concepts were retrieved correctly
    assert len(concepts) == 1
    concept, score = concepts[0]
    assert concept.id == "con_12345678"
    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"
    assert "key" in concept.metadata
    assert concept.metadata["key"] == "value"
    assert score == 0.5

    # Check that the collection was queried correctly
    mock_chroma_collection.query.assert_called_once_with(
        query_texts=["test query"],
        n_results=5,
        where=None,
        include=["documents", "metadatas", "distances"],
    )

    # Test searching with filters
    memory.search_concepts("test query", n_results=10,
                           filter_metadata={"category": "test"})
    mock_chroma_collection.query.assert_called_with(
        query_texts=["test query"],
        n_results=10,
        where={"category": "test"},
        include=["documents", "metadatas", "distances"],
    )


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_get_concept_by_name(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory retrieves concepts by name correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Get a concept by name (exact match)
    concept = memory.get_concept_by_name("Test Concept", exact_match=True)

    # Check that the concept was retrieved correctly
    assert concept is not None
    assert concept.id == "con_12345678"
    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"

    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where={"name": "Test Concept"},
        include=["documents", "metadatas", "ids"],
    )

    # Get a concept by name (fuzzy match)
    concept = memory.get_concept_by_name("Test", exact_match=False)

    # Check that the concept was retrieved correctly
    assert concept is not None
    assert concept.id == "con_12345678"
    assert concept.name == "Test Concept"
    assert concept.description == "A test concept"
    assert concept.content == "This is a test concept with detailed content"

    # Check that the collection was queried correctly
    mock_chroma_collection.query.assert_called_once_with(
        query_texts=["Test"],
        n_results=1,
        include=["documents", "metadatas", "ids"],
    )

    # Test getting a non-existent concept by name
    mock_chroma_collection.get.return_value = {
        "ids": [], "documents": [], "metadatas": []}
    mock_chroma_collection.query.return_value = {
        "ids": [[]], "documents": [[]], "metadatas": [[]]}
    concept = memory.get_concept_by_name("Nonexistent", exact_match=True)
    assert concept is None


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_update_concept(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory updates concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Update a concept
    result = memory.update_concept(
        concept_id="con_12345678",
        name="Updated Concept",
        description="Updated description",
        content="Updated content",
        metadata={"new_key": "new_value"},
    )

    # Check that the concept was updated correctly
    assert result is True

    # Check that the collection was queried correctly
    mock_chroma_collection.update.assert_called_once()
    args, kwargs = mock_chroma_collection.update.call_args

    assert kwargs["documents"] == ["Updated content"]
    assert kwargs["ids"] == ["con_12345678"]
    assert kwargs["metadatas"][0]["name"] == "Updated Concept"
    assert kwargs["metadatas"][0]["description"] == "Updated description"
    assert "timestamp" in kwargs["metadatas"][0]
    assert "updated_at" in kwargs["metadatas"][0]
    assert kwargs["metadatas"][0]["key"] == "value"
    assert kwargs["metadatas"][0]["new_key"] == "new_value"

    # Test updating a non-existent concept
    mock_chroma_collection.get.return_value = {
        "ids": [], "documents": [], "metadatas": []}
    result = memory.update_concept("nonexistent", name="Updated Concept")
    assert result is False


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_delete_concept(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory deletes concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Delete a concept
    result = memory.delete_concept("con_12345678")

    # Check that the concept was deleted correctly
    assert result is True

    # Check that the collection was queried correctly
    mock_chroma_collection.delete.assert_called_once_with(
        ids=["con_12345678"],
    )


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_clear(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory clears concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Create semantic memory
    memory = SemanticMemory()

    # Clear all concepts
    result = memory.clear()

    # Check that the concepts were cleared correctly
    assert result is True

    # Check that the collection was queried correctly
    mock_chroma_collection.delete.assert_called_once_with(
        where={},
    )


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_count_concepts(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory counts concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Set up the get method to return multiple concepts
    mock_chroma_collection.get.return_value = {
        "ids": ["con_12345678", "con_87654321"],
        "documents": ["This is a concept", "This is another concept"],
        "metadatas": [
            {
                "name": "Concept 1",
                "description": "Description 1",
                "timestamp": int(time.time()),
                "updated_at": int(time.time()),
                "key": "value1",
            },
            {
                "name": "Concept 2",
                "description": "Description 2",
                "timestamp": int(time.time()),
                "updated_at": int(time.time()),
                "key": "value2",
            },
        ],
    }

    # Create semantic memory
    memory = SemanticMemory()

    # Count concepts
    count = memory.count_concepts()

    # Check that the concepts were counted correctly
    assert count == 2

    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where=None,
        include=["ids"],
    )

    # Test counting concepts with filters
    memory.count_concepts(filter_metadata={"category": "test"})
    mock_chroma_collection.get.assert_called_with(
        where={"category": "test"},
        include=["ids"],
    )


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_get_all_concepts(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory retrieves all concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Set up the get method to return multiple concepts
    timestamp1 = int(time.time()) - 100
    timestamp2 = int(time.time())
    updated_at1 = timestamp1 + 50
    updated_at2 = timestamp2

    # Define a side effect function to handle different calls
    def get_side_effect(*args, **kwargs):
        # Default response
        response = {
            "ids": ["con_12345678", "con_87654321"],
            "documents": ["This is a concept", "This is another concept"],
            "metadatas": [
                {
                    "name": "Concept B",  # Alphabetically after Concept A
                    "description": "Description B",
                    "timestamp": timestamp1,  # Older
                    "updated_at": updated_at1,  # Older update
                    "key": "value1",
                },
                {
                    "name": "Concept A",  # Alphabetically before Concept B
                    "description": "Description A",
                    "timestamp": timestamp2,  # Newer
                    "updated_at": updated_at2,  # Newer update
                    "key": "value2",
                },
            ],
        }
        return response

    # Set up the mock to use the side effect function
    mock_chroma_collection.get.side_effect = get_side_effect

    # Create semantic memory
    memory = SemanticMemory()

    # Get all concepts (sorted by name, ascending)
    concepts = memory.get_all_concepts(sort_by="name", ascending=True)

    # Check that the concepts were retrieved correctly
    assert len(concepts) == 2

    # Find each concept by name
    concept_a = next((c for c in concepts if c.name == "Concept A"), None)
    concept_b = next((c for c in concepts if c.name == "Concept B"), None)

    assert concept_a is not None
    assert concept_a.description == "Description A"
    assert concept_a.timestamp == timestamp2
    assert concept_a.updated_at == updated_at2

    assert concept_b is not None
    assert concept_b.description == "Description B"
    assert concept_b.timestamp == timestamp1
    assert concept_b.updated_at == updated_at1

    # Get all concepts (sorted by name, descending)
    concepts = memory.get_all_concepts(sort_by="name", ascending=False)

    # Find each concept by name
    concept_a = next((c for c in concepts if c.name == "Concept A"), None)
    concept_b = next((c for c in concepts if c.name == "Concept B"), None)

    assert concept_a is not None
    assert concept_b is not None
    # In descending order, B should come before A
    assert concepts.index(concept_b) < concepts.index(concept_a)

    # Get all concepts (sorted by timestamp, ascending)
    concepts = memory.get_all_concepts(sort_by="timestamp", ascending=True)

    # Check that the concepts were retrieved correctly
    assert len(concepts) == 2
    assert concepts[0].timestamp == timestamp1  # Older
    assert concepts[1].timestamp == timestamp2  # Newer

    # Get all concepts (sorted by updated_at, descending)
    concepts = memory.get_all_concepts(sort_by="updated_at", ascending=False)

    # Check that the concepts were retrieved correctly
    assert len(concepts) == 2
    assert concepts[0].updated_at == updated_at2  # Newer update
    assert concepts[1].updated_at == updated_at1  # Older update

    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_with(
        where=None,
        include=["documents", "metadatas", "ids"],
    )

    # Test getting all concepts with filters
    memory.get_all_concepts(filter_metadata={"category": "test"})
    mock_chroma_collection.get.assert_called_with(
        where={"category": "test"},
        include=["documents", "metadatas", "ids"],
    )


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_get_recently_updated_concepts(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory retrieves recently updated concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Set up the get method to return multiple concepts
    timestamp1 = int(time.time()) - 100
    timestamp2 = int(time.time())
    updated_at1 = timestamp1 + 50
    updated_at2 = timestamp2

    mock_chroma_collection.get.return_value = {
        "ids": ["con_12345678", "con_87654321"],
        "documents": ["This is a concept", "This is another concept"],
        "metadatas": [
            {
                "name": "Concept 1",
                "description": "Description 1",
                "timestamp": timestamp1,
                "updated_at": updated_at1,
                "key": "value1",
            },
            {
                "name": "Concept 2",
                "description": "Description 2",
                "timestamp": timestamp2,
                "updated_at": updated_at2,
                "key": "value2",
            },
        ],
    }

    # Create semantic memory
    memory = SemanticMemory()

    # Get recently updated concepts
    concepts = memory.get_recently_updated_concepts(n=1)

    # Check that the concepts were retrieved correctly
    assert len(concepts) == 1
    assert concepts[0].name == "Concept 2"  # Most recently updated
    assert concepts[0].updated_at == updated_at2

    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where=None,
        include=["documents", "metadatas", "ids"],
    )

    # Test getting recently updated concepts with filters
    memory.get_recently_updated_concepts(
        n=2, filter_metadata={"category": "test"})
    mock_chroma_collection.get.assert_called_with(
        where={"category": "test"},
        include=["documents", "metadatas", "ids"],
    )


@patch("dukat.memory.semantic.chromadb.PersistentClient")
def test_semantic_memory_get_related_concepts(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that semantic memory retrieves related concepts correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client

    # Set up the query method to return multiple concepts
    mock_chroma_collection.query.return_value = {
        "ids": [["con_12345678", "con_87654321"]],
        "documents": [["This is a concept", "This is a related concept"]],
        "metadatas": [[
            {
                "name": "Concept 1",
                "description": "Description 1",
                "timestamp": int(time.time()),
                "updated_at": int(time.time()),
                "key": "value1",
            },
            {
                "name": "Concept 2",
                "description": "Description 2",
                "timestamp": int(time.time()),
                "updated_at": int(time.time()),
                "key": "value2",
            },
        ]],
        # First one is the concept itself (distance 0)
        "distances": [[0.0, 0.5]],
    }

    # Create semantic memory
    memory = SemanticMemory()

    # Get related concepts
    related = memory.get_related_concepts("con_12345678", n_results=1)

    # Check that the related concepts were retrieved correctly
    assert len(related) == 1
    concept, score = related[0]
    assert concept.id == "con_87654321"  # The related concept
    assert concept.name == "Concept 2"
    assert score == 0.5

    # Check that the collection was queried correctly
    # First, it gets the original concept
    mock_chroma_collection.get.assert_called_once_with(
        ids=["con_12345678"],
        include=["documents", "metadatas"],
    )

    # Then, it searches for related concepts
    mock_chroma_collection.query.assert_called_once()
    args, kwargs = mock_chroma_collection.query.call_args

    assert kwargs["query_texts"] == [
        "This is a test concept with detailed content"]
    # n_results + 1 to account for the concept itself
    assert kwargs["n_results"] == 2
