"""Tests for the episodic memory module.

This module contains tests for the episodic memory functionality.

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

from dukat.memory.episodic import Episode, EpisodicMemory


def test_episode_init():
    """Test that an episode initializes correctly."""
    # Create an episode with minimal arguments
    episode = Episode(content="This is a test episode")
    
    assert episode.content == "This is a test episode"
    assert episode.id.startswith("ep_")
    assert episode.title.startswith("Episode ep_")
    assert isinstance(episode.timestamp, int)
    assert episode.metadata == {}
    
    # Create an episode with all arguments
    timestamp = int(time.time())
    metadata = {"key": "value"}
    episode_id = f"ep_{uuid.uuid4().hex[:8]}"
    
    episode = Episode(
        content="This is another test episode",
        title="Test Episode",
        timestamp=timestamp,
        metadata=metadata,
        episode_id=episode_id,
    )
    
    assert episode.content == "This is another test episode"
    assert episode.id == episode_id
    assert episode.title == "Test Episode"
    assert episode.timestamp == timestamp
    assert episode.metadata == metadata


def test_episode_to_dict():
    """Test that an episode converts to a dictionary correctly."""
    timestamp = int(time.time())
    metadata = {"key": "value"}
    episode_id = f"ep_{uuid.uuid4().hex[:8]}"
    
    episode = Episode(
        content="This is a test episode",
        title="Test Episode",
        timestamp=timestamp,
        metadata=metadata,
        episode_id=episode_id,
    )
    
    data = episode.to_dict()
    
    assert data["content"] == "This is a test episode"
    assert data["id"] == episode_id
    assert data["title"] == "Test Episode"
    assert data["timestamp"] == timestamp
    assert data["metadata"] == metadata


def test_episode_from_dict():
    """Test that an episode is created from a dictionary correctly."""
    timestamp = int(time.time())
    metadata = {"key": "value"}
    episode_id = f"ep_{uuid.uuid4().hex[:8]}"
    
    data = {
        "content": "This is a test episode",
        "id": episode_id,
        "title": "Test Episode",
        "timestamp": timestamp,
        "metadata": metadata,
    }
    
    episode = Episode.from_dict(data)
    
    assert episode.content == "This is a test episode"
    assert episode.id == episode_id
    assert episode.title == "Test Episode"
    assert episode.timestamp == timestamp
    assert episode.metadata == metadata


def test_episode_str():
    """Test that an episode converts to a string correctly."""
    episode = Episode(
        content="This is a test episode with a long content that should be truncated",
        title="Test Episode",
    )
    
    assert str(episode) == f"Test Episode ({episode.id}): This is a test episode with a long content that should..."


# Mock ChromaDB for testing
@pytest.fixture
def mock_chroma_collection():
    """Create a mock ChromaDB collection."""
    mock_collection = MagicMock()
    
    # Mock add method
    mock_collection.add.return_value = None
    
    # Mock get method
    mock_collection.get.return_value = {
        "ids": ["ep_12345678"],
        "documents": ["This is a test episode"],
        "metadatas": [{"title": "Test Episode", "timestamp": int(time.time()), "key": "value"}],
    }
    
    # Mock query method
    mock_collection.query.return_value = {
        "ids": [["ep_12345678"]],
        "documents": [["This is a test episode"]],
        "metadatas": [[{"title": "Test Episode", "timestamp": int(time.time()), "key": "value"}]],
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


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_init(mock_client_class, mock_chroma_client):
    """Test that episodic memory initializes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create episodic memory
        memory = EpisodicMemory(persist_dir=temp_dir)
        
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
            name="dukat_episodes",
            metadata={"description": "Episodic memory collection for Dukat"},
        )
        
        # Check that the collection was stored
        assert memory.collection == mock_chroma_client.get_or_create_collection.return_value


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_add_episode(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory adds episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Add an episode
    episode = memory.add_episode(
        content="This is a test episode",
        title="Test Episode",
        metadata={"key": "value"},
    )
    
    # Check that the episode was created correctly
    assert episode.content == "This is a test episode"
    assert episode.title == "Test Episode"
    assert "key" in episode.metadata
    assert episode.metadata["key"] == "value"
    
    # Check that the episode was added to the collection
    mock_chroma_collection.add.assert_called_once()
    args, kwargs = mock_chroma_collection.add.call_args
    
    assert kwargs["documents"] == ["This is a test episode"]
    assert kwargs["ids"] == [episode.id]
    assert kwargs["metadatas"][0]["title"] == "Test Episode"
    assert "timestamp" in kwargs["metadatas"][0]
    assert kwargs["metadatas"][0]["key"] == "value"
    
    # Test adding an episode with empty content
    with pytest.raises(ValueError):
        memory.add_episode(content="")


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_get_episode(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory retrieves episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Get an episode
    episode = memory.get_episode("ep_12345678")
    
    # Check that the episode was retrieved correctly
    assert episode is not None
    assert episode.id == "ep_12345678"
    assert episode.content == "This is a test episode"
    assert episode.title == "Test Episode"
    assert "key" in episode.metadata
    assert episode.metadata["key"] == "value"
    
    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        ids=["ep_12345678"],
        include=["documents", "metadatas"],
    )
    
    # Test getting a non-existent episode
    mock_chroma_collection.get.return_value = {"ids": [], "documents": [], "metadatas": []}
    episode = memory.get_episode("nonexistent")
    assert episode is None


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_search_episodes(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory searches episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Search for episodes
    episodes = memory.search_episodes("test query")
    
    # Check that the episodes were retrieved correctly
    assert len(episodes) == 1
    episode, score = episodes[0]
    assert episode.id == "ep_12345678"
    assert episode.content == "This is a test episode"
    assert episode.title == "Test Episode"
    assert "key" in episode.metadata
    assert episode.metadata["key"] == "value"
    assert score == 0.5
    
    # Check that the collection was queried correctly
    mock_chroma_collection.query.assert_called_once_with(
        query_texts=["test query"],
        n_results=5,
        where=None,
        include=["documents", "metadatas", "distances"],
    )
    
    # Test searching with filters
    memory.search_episodes("test query", n_results=10, filter_metadata={"category": "test"})
    mock_chroma_collection.query.assert_called_with(
        query_texts=["test query"],
        n_results=10,
        where={"category": "test"},
        include=["documents", "metadatas", "distances"],
    )


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_get_recent_episodes(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory retrieves recent episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Set up the get method to return multiple episodes
    timestamp1 = int(time.time()) - 100
    timestamp2 = int(time.time())
    mock_chroma_collection.get.return_value = {
        "ids": ["ep_12345678", "ep_87654321"],
        "documents": ["This is an old episode", "This is a new episode"],
        "metadatas": [
            {"title": "Old Episode", "timestamp": timestamp1, "key": "value1"},
            {"title": "New Episode", "timestamp": timestamp2, "key": "value2"},
        ],
    }
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Get recent episodes
    episodes = memory.get_recent_episodes(n=2)
    
    # Check that the episodes were retrieved correctly
    assert len(episodes) == 2
    assert episodes[0].id == "ep_87654321"  # Newest first
    assert episodes[0].content == "This is a new episode"
    assert episodes[0].title == "New Episode"
    assert episodes[0].timestamp == timestamp2
    assert episodes[0].metadata["key"] == "value2"
    
    assert episodes[1].id == "ep_12345678"
    assert episodes[1].content == "This is an old episode"
    assert episodes[1].title == "Old Episode"
    assert episodes[1].timestamp == timestamp1
    assert episodes[1].metadata["key"] == "value1"
    
    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where=None,
        include=["documents", "metadatas", "ids"],
    )
    
    # Test getting recent episodes with filters
    memory.get_recent_episodes(n=1, filter_metadata={"category": "test"})
    mock_chroma_collection.get.assert_called_with(
        where={"category": "test"},
        include=["documents", "metadatas", "ids"],
    )


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_delete_episode(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory deletes episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Delete an episode
    result = memory.delete_episode("ep_12345678")
    
    # Check that the episode was deleted correctly
    assert result is True
    
    # Check that the collection was queried correctly
    mock_chroma_collection.delete.assert_called_once_with(
        ids=["ep_12345678"],
    )


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_update_episode(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory updates episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Update an episode
    result = memory.update_episode(
        episode_id="ep_12345678",
        content="Updated content",
        title="Updated Title",
        metadata={"new_key": "new_value"},
    )
    
    # Check that the episode was updated correctly
    assert result is True
    
    # Check that the collection was queried correctly
    mock_chroma_collection.update.assert_called_once()
    args, kwargs = mock_chroma_collection.update.call_args
    
    assert kwargs["documents"] == ["Updated content"]
    assert kwargs["ids"] == ["ep_12345678"]
    assert kwargs["metadatas"][0]["title"] == "Updated Title"
    assert "timestamp" in kwargs["metadatas"][0]
    assert kwargs["metadatas"][0]["key"] == "value"
    assert kwargs["metadatas"][0]["new_key"] == "new_value"
    
    # Test updating a non-existent episode
    mock_chroma_collection.get.return_value = {"ids": [], "documents": [], "metadatas": []}
    result = memory.update_episode("nonexistent", content="Updated content")
    assert result is False


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_clear(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory clears episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Clear all episodes
    result = memory.clear()
    
    # Check that the episodes were cleared correctly
    assert result is True
    
    # Check that the collection was queried correctly
    mock_chroma_collection.delete.assert_called_once_with(
        where={},
    )


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_count_episodes(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory counts episodes correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Set up the get method to return multiple episodes
    mock_chroma_collection.get.return_value = {
        "ids": ["ep_12345678", "ep_87654321"],
        "documents": ["This is an episode", "This is another episode"],
        "metadatas": [
            {"title": "Episode 1", "timestamp": int(time.time()), "key": "value1"},
            {"title": "Episode 2", "timestamp": int(time.time()), "key": "value2"},
        ],
    }
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Count episodes
    count = memory.count_episodes()
    
    # Check that the episodes were counted correctly
    assert count == 2
    
    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where=None,
        include=["ids"],
    )
    
    # Test counting episodes with filters
    memory.count_episodes(filter_metadata={"category": "test"})
    mock_chroma_collection.get.assert_called_with(
        where={"category": "test"},
        include=["ids"],
    )


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_get_episode_by_title(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory retrieves episodes by title correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Get an episode by title (exact match)
    episode = memory.get_episode_by_title("Test Episode", exact_match=True)
    
    # Check that the episode was retrieved correctly
    assert episode is not None
    assert episode.id == "ep_12345678"
    assert episode.content == "This is a test episode"
    assert episode.title == "Test Episode"
    
    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where={"title": "Test Episode"},
        include=["documents", "metadatas", "ids"],
    )
    
    # Get an episode by title (fuzzy match)
    episode = memory.get_episode_by_title("Test")
    
    # Check that the episode was retrieved correctly
    assert episode is not None
    assert episode.id == "ep_12345678"
    assert episode.content == "This is a test episode"
    assert episode.title == "Test Episode"
    
    # Check that the collection was queried correctly
    mock_chroma_collection.query.assert_called_once_with(
        query_texts=["Test"],
        n_results=1,
        include=["documents", "metadatas", "ids"],
    )
    
    # Test getting a non-existent episode by title
    mock_chroma_collection.get.return_value = {"ids": [], "documents": [], "metadatas": []}
    mock_chroma_collection.query.return_value = {"ids": [[]], "documents": [[]], "metadatas": [[]]}
    episode = memory.get_episode_by_title("Nonexistent", exact_match=True)
    assert episode is None


@patch("dukat.memory.episodic.chromadb.PersistentClient")
def test_episodic_memory_get_episodes_in_timerange(mock_client_class, mock_chroma_client, mock_chroma_collection):
    """Test that episodic memory retrieves episodes in a time range correctly."""
    # Set up the mock
    mock_client_class.return_value = mock_chroma_client
    
    # Set up the get method to return multiple episodes
    timestamp1 = 1000
    timestamp2 = 2000
    mock_chroma_collection.get.return_value = {
        "ids": ["ep_12345678", "ep_87654321"],
        "documents": ["This is an old episode", "This is a new episode"],
        "metadatas": [
            {"title": "Old Episode", "timestamp": timestamp1, "key": "value1"},
            {"title": "New Episode", "timestamp": timestamp2, "key": "value2"},
        ],
    }
    
    # Create episodic memory
    memory = EpisodicMemory()
    
    # Get episodes in a time range
    episodes = memory.get_episodes_in_timerange(500, 2500)
    
    # Check that the episodes were retrieved correctly
    assert len(episodes) == 2
    assert episodes[0].id == "ep_12345678"  # Sorted by timestamp
    assert episodes[0].content == "This is an old episode"
    assert episodes[0].title == "Old Episode"
    assert episodes[0].timestamp == timestamp1
    
    assert episodes[1].id == "ep_87654321"
    assert episodes[1].content == "This is a new episode"
    assert episodes[1].title == "New Episode"
    assert episodes[1].timestamp == timestamp2
    
    # Check that the collection was queried correctly
    mock_chroma_collection.get.assert_called_once_with(
        where={"timestamp": {"$gte": 500, "$lte": 2500}},
        include=["documents", "metadatas", "ids"],
    )
    
    # Test getting episodes in a time range with filters
    memory.get_episodes_in_timerange(500, 2500, filter_metadata={"category": "test"})
    mock_chroma_collection.get.assert_called_with(
        where={"timestamp": {"$gte": 500, "$lte": 2500}, "category": "test"},
        include=["documents", "metadatas", "ids"],
    )
