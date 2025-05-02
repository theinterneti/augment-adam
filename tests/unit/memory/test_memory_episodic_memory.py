"""
Unit tests for the Episodic Memory system.

This module contains tests for the Episodic Memory system, including memory
storage, retrieval, and management of episodes and events.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import datetime

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.episodic.base import EpisodicMemory, Episode, Event


class TestEpisodicMemory:
    """Tests for the Episodic Memory system."""

    @pytest.fixture
    def episodic_memory(self):
        """Create an EpisodicMemory for testing."""
        return EpisodicMemory(name="test_episodic_memory")

    @pytest.fixture
    def sample_event(self):
        """Create a sample Event for testing."""
        return Event(content="test event content", metadata={"source": "user"})

    @pytest.fixture
    def sample_episode(self):
        """Create a sample Episode for testing."""
        episode = Episode(content="test episode content", metadata={"topic": "test"})
        episode.add_event(Event(content="event 1", metadata={"source": "user"}))
        episode.add_event(Event(content="event 2", metadata={"source": "assistant"}))
        return episode

    def test_init(self, episodic_memory):
        """Test initializing an EpisodicMemory."""
        assert episodic_memory.name == "test_episodic_memory"
        assert episodic_memory.memory_type == MemoryType.EPISODIC
        assert episodic_memory.items == {}

    def test_event_init(self, sample_event):
        """Test initializing an Event."""
        assert sample_event.content == "test event content"
        assert sample_event.metadata == {"source": "user"}
        assert sample_event.id is not None
        assert sample_event.timestamp is not None
        assert sample_event.embedding is None

    def test_episode_init(self):
        """Test initializing an Episode."""
        episode = Episode(content="test episode content", metadata={"topic": "test"})
        assert episode.content == "test episode content"
        assert episode.metadata == {"topic": "test"}
        assert episode.id is not None
        assert episode.created_at is not None
        assert episode.updated_at is not None
        assert episode.events == []
        assert episode.start_time is None
        assert episode.end_time is None

    def test_add_episode(self, episodic_memory, sample_episode):
        """Test adding an episode to episodic memory."""
        # Add the episode
        episode_id = episodic_memory.add(sample_episode)

        # Check that the episode was added
        assert episode_id == sample_episode.id
        assert sample_episode.id in episodic_memory.items
        assert episodic_memory.items[sample_episode.id] == sample_episode

    def test_get_episode(self, episodic_memory, sample_episode):
        """Test getting an episode from episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Get the episode
        retrieved_episode = episodic_memory.get(sample_episode.id)

        # Check that the correct episode was retrieved
        assert retrieved_episode == sample_episode

    def test_get_nonexistent_episode(self, episodic_memory):
        """Test getting a nonexistent episode from episodic memory."""
        # Get a nonexistent episode
        retrieved_episode = episodic_memory.get("nonexistent")

        # Check that None was returned
        assert retrieved_episode is None

    def test_update_episode(self, episodic_memory, sample_episode):
        """Test updating an episode in episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Update the episode
        updated_episode = episodic_memory.update(
            sample_episode.id, content="updated content"
        )

        # Check that the episode was updated
        assert updated_episode == sample_episode
        assert updated_episode.content == "updated content"

    def test_update_nonexistent_episode(self, episodic_memory):
        """Test updating a nonexistent episode in episodic memory."""
        # Update a nonexistent episode
        updated_episode = episodic_memory.update(
            "nonexistent", content="updated content"
        )

        # Check that None was returned
        assert updated_episode is None

    def test_remove_episode(self, episodic_memory, sample_episode):
        """Test removing an episode from episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Remove the episode
        result = episodic_memory.remove(sample_episode.id)

        # Check that the episode was removed
        assert result is True
        assert sample_episode.id not in episodic_memory.items

    def test_remove_nonexistent_episode(self, episodic_memory):
        """Test removing a nonexistent episode from episodic memory."""
        # Remove a nonexistent episode
        result = episodic_memory.remove("nonexistent")

        # Check that False was returned
        assert result is False

    def test_clear_episodes(self, episodic_memory, sample_episode):
        """Test clearing all episodes from episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Clear the memory
        episodic_memory.clear()

        # Check that the memory is empty
        assert len(episodic_memory.items) == 0

    def test_add_event_to_episode(self, episodic_memory, sample_episode, sample_event):
        """Test adding an event to an episode in episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Add the event to the episode
        event_id = episodic_memory.add_event(sample_episode.id, sample_event)

        # Check that the event was added
        assert event_id == sample_event.id
        assert any(event.id == sample_event.id for event in sample_episode.events)

    def test_add_event_to_nonexistent_episode(self, episodic_memory, sample_event):
        """Test adding an event to a nonexistent episode in episodic memory."""
        # Add the event to a nonexistent episode
        event_id = episodic_memory.add_event("nonexistent", sample_event)

        # Check that None was returned
        assert event_id is None

    def test_get_event(self, episodic_memory, sample_episode):
        """Test getting an event from an episode in episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Get the first event
        event_id = sample_episode.events[0].id
        retrieved_event = episodic_memory.get_event(sample_episode.id, event_id)

        # Check that the correct event was retrieved
        assert retrieved_event.id == event_id
        assert retrieved_event.content == "event 1"

    def test_get_nonexistent_event(self, episodic_memory, sample_episode):
        """Test getting a nonexistent event from an episode in episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Get a nonexistent event
        retrieved_event = episodic_memory.get_event(sample_episode.id, "nonexistent")

        # Check that None was returned
        assert retrieved_event is None

    def test_get_event_from_nonexistent_episode(self, episodic_memory):
        """Test getting an event from a nonexistent episode in episodic memory."""
        # Get an event from a nonexistent episode
        retrieved_event = episodic_memory.get_event("nonexistent", "nonexistent")

        # Check that None was returned
        assert retrieved_event is None

    def test_remove_event(self, episodic_memory, sample_episode):
        """Test removing an event from an episode in episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Get the first event ID
        event_id = sample_episode.events[0].id

        # Remove the event
        result = episodic_memory.remove_event(sample_episode.id, event_id)

        # Check that the event was removed
        assert result is True
        assert not any(event.id == event_id for event in sample_episode.events)

    def test_remove_nonexistent_event(self, episodic_memory, sample_episode):
        """Test removing a nonexistent event from an episode in episodic memory."""
        # Add the episode
        episodic_memory.add(sample_episode)

        # Remove a nonexistent event
        result = episodic_memory.remove_event(sample_episode.id, "nonexistent")

        # Check that False was returned
        assert result is False

    def test_remove_event_from_nonexistent_episode(self, episodic_memory):
        """Test removing an event from a nonexistent episode in episodic memory."""
        # Remove an event from a nonexistent episode
        result = episodic_memory.remove_event("nonexistent", "nonexistent")

        # Check that False was returned
        assert result is False

    def test_get_events_in_range(self, episodic_memory):
        """Test getting events in a time range from an episode in episodic memory."""
        # Create an episode with events at different times
        episode = Episode(content="test episode content")
        
        # Create events with specific timestamps
        event1 = Event(content="event 1")
        event1.timestamp = "2023-01-01T00:00:00"
        
        event2 = Event(content="event 2")
        event2.timestamp = "2023-01-02T00:00:00"
        
        event3 = Event(content="event 3")
        event3.timestamp = "2023-01-03T00:00:00"
        
        # Add events to the episode
        episode.add_event(event1)
        episode.add_event(event2)
        episode.add_event(event3)
        
        # Add the episode to memory
        episodic_memory.add(episode)
        
        # Get events in a time range
        events = episodic_memory.get_events_in_range(
            episode.id,
            start_time="2023-01-01T12:00:00",
            end_time="2023-01-02T12:00:00"
        )
        
        # Check that only event2 is in the range
        assert len(events) == 1
        assert events[0].content == "event 2"

    def test_get_events_in_range_no_start(self, episodic_memory):
        """Test getting events in a time range with no start time."""
        # Create an episode with events at different times
        episode = Episode(content="test episode content")
        
        # Create events with specific timestamps
        event1 = Event(content="event 1")
        event1.timestamp = "2023-01-01T00:00:00"
        
        event2 = Event(content="event 2")
        event2.timestamp = "2023-01-02T00:00:00"
        
        # Add events to the episode
        episode.add_event(event1)
        episode.add_event(event2)
        
        # Add the episode to memory
        episodic_memory.add(episode)
        
        # Get events with no start time
        events = episodic_memory.get_events_in_range(
            episode.id,
            end_time="2023-01-01T12:00:00"
        )
        
        # Check that only event1 is in the range
        assert len(events) == 1
        assert events[0].content == "event 1"

    def test_get_events_in_range_no_end(self, episodic_memory):
        """Test getting events in a time range with no end time."""
        # Create an episode with events at different times
        episode = Episode(content="test episode content")
        
        # Create events with specific timestamps
        event1 = Event(content="event 1")
        event1.timestamp = "2023-01-01T00:00:00"
        
        event2 = Event(content="event 2")
        event2.timestamp = "2023-01-02T00:00:00"
        
        # Add events to the episode
        episode.add_event(event1)
        episode.add_event(event2)
        
        # Add the episode to memory
        episodic_memory.add(episode)
        
        # Get events with no end time
        events = episodic_memory.get_events_in_range(
            episode.id,
            start_time="2023-01-01T12:00:00"
        )
        
        # Check that only event2 is in the range
        assert len(events) == 1
        assert events[0].content == "event 2"

    def test_get_events_in_range_nonexistent_episode(self, episodic_memory):
        """Test getting events in a time range from a nonexistent episode."""
        # Get events from a nonexistent episode
        events = episodic_memory.get_events_in_range(
            "nonexistent",
            start_time="2023-01-01T00:00:00",
            end_time="2023-01-02T00:00:00"
        )
        
        # Check that an empty list was returned
        assert events == []

    def test_episode_to_dict(self, sample_episode):
        """Test converting an episode to a dictionary."""
        # Convert the episode to a dictionary
        episode_dict = sample_episode.to_dict()
        
        # Check the dictionary
        assert episode_dict["id"] == sample_episode.id
        assert episode_dict["content"] == "test episode content"
        assert episode_dict["metadata"] == {"topic": "test"}
        assert "created_at" in episode_dict
        assert "updated_at" in episode_dict
        assert "events" in episode_dict
        assert len(episode_dict["events"]) == 2

    def test_episode_from_dict(self):
        """Test creating an episode from a dictionary."""
        # Create a dictionary
        episode_dict = {
            "id": "test_id",
            "content": "test content",
            "metadata": {"topic": "test"},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "events": [
                {
                    "id": "event1",
                    "content": "event 1",
                    "timestamp": "2023-01-01T00:00:00",
                    "metadata": {"source": "user"}
                },
                {
                    "id": "event2",
                    "content": "event 2",
                    "timestamp": "2023-01-01T00:00:00",
                    "metadata": {"source": "assistant"}
                }
            ],
            "start_time": "2023-01-01T00:00:00",
            "end_time": "2023-01-01T00:00:00"
        }
        
        # Create an episode from the dictionary
        episode = Episode.from_dict(episode_dict)
        
        # Check the episode
        assert episode.id == "test_id"
        assert episode.content == "test content"
        assert episode.metadata == {"topic": "test"}
        assert episode.created_at == "2023-01-01T00:00:00"
        assert episode.updated_at == "2023-01-01T00:00:00"
        assert len(episode.events) == 2
        assert episode.events[0].id == "event1"
        assert episode.events[1].id == "event2"
        assert episode.start_time == "2023-01-01T00:00:00"
        assert episode.end_time == "2023-01-01T00:00:00"

    def test_event_to_dict(self, sample_event):
        """Test converting an event to a dictionary."""
        # Convert the event to a dictionary
        event_dict = sample_event.to_dict()
        
        # Check the dictionary
        assert event_dict["id"] == sample_event.id
        assert event_dict["content"] == "test event content"
        assert event_dict["metadata"] == {"source": "user"}
        assert "timestamp" in event_dict

    def test_event_from_dict(self):
        """Test creating an event from a dictionary."""
        # Create a dictionary
        event_dict = {
            "id": "test_id",
            "content": "test content",
            "timestamp": "2023-01-01T00:00:00",
            "metadata": {"source": "user"},
            "embedding": [0.1, 0.2, 0.3]
        }
        
        # Create an event from the dictionary
        event = Event.from_dict(event_dict)
        
        # Check the event
        assert event.id == "test_id"
        assert event.content == "test content"
        assert event.timestamp == "2023-01-01T00:00:00"
        assert event.metadata == {"source": "user"}
        assert event.embedding == [0.1, 0.2, 0.3]

    def test_episodic_memory_to_dict(self, episodic_memory, sample_episode):
        """Test converting an episodic memory to a dictionary."""
        # Add the episode
        episodic_memory.add(sample_episode)
        
        # Convert the memory to a dictionary
        memory_dict = episodic_memory.to_dict()
        
        # Check the dictionary
        assert memory_dict["name"] == "test_episodic_memory"
        assert memory_dict["memory_type"] == "EPISODIC"
        assert "items" in memory_dict
        assert sample_episode.id in memory_dict["items"]

    def test_episodic_memory_from_dict(self):
        """Test creating an episodic memory from a dictionary."""
        # Create a dictionary
        memory_dict = {
            "name": "test_memory",
            "memory_type": "EPISODIC",
            "items": {
                "episode1": {
                    "id": "episode1",
                    "content": "test content",
                    "metadata": {"topic": "test"},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "events": [
                        {
                            "id": "event1",
                            "content": "event 1",
                            "timestamp": "2023-01-01T00:00:00",
                            "metadata": {"source": "user"}
                        }
                    ],
                    "start_time": "2023-01-01T00:00:00",
                    "end_time": "2023-01-01T00:00:00"
                }
            },
            "metadata": {"test": "value"}
        }
        
        # Create a memory from the dictionary
        memory = EpisodicMemory.from_dict(memory_dict)
        
        # Check the memory
        assert memory.name == "test_memory"
        assert memory.memory_type == MemoryType.EPISODIC
        assert len(memory.items) == 1
        assert "episode1" in memory.items
        assert memory.items["episode1"].content == "test content"
        assert memory.metadata == {"test": "value"}
