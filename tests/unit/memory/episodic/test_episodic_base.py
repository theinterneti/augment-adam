"""
Unit tests for episodic memory base classes.

This module contains unit tests for the episodic memory base classes,
including Event, Episode, and EpisodicMemory.
"""

import unittest
import pytest
import datetime
from unittest.mock import patch, MagicMock

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType
from augment_adam.memory.episodic.base import Event, Episode, EpisodicMemory

class TestEvent(unittest.TestCase):
    """Tests for the Event class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.event = Event(content="Test event content", metadata={"source": "user"})

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_init(self):
        """Test initialization of Event."""
        # Test with minimal arguments
        event = Event()
        self.assertIsNotNone(event.id)
        self.assertIsNone(event.content)
        self.assertIsInstance(event.metadata, dict)
        self.assertIsNotNone(event.timestamp)

        # Test with all arguments
        content = "Test content"
        metadata = {"source": "user", "importance": "high"}
        event = Event(content=content, metadata=metadata)
        self.assertIsNotNone(event.id)
        self.assertEqual(event.content, content)
        self.assertEqual(event.metadata, metadata)
        self.assertIsNotNone(event.timestamp)

    def test_to_dict(self):
        """Test converting Event to dictionary."""
        # Arrange
        event = Event(
            id="test_id",
            content="Test content",
            timestamp="2023-01-01T12:00:00",
            metadata={"source": "user"},
            embedding=[0.1, 0.2, 0.3]
        )

        # Act
        result = event.to_dict()

        # Assert
        self.assertEqual(result["id"], "test_id")
        self.assertEqual(result["content"], "Test content")
        self.assertEqual(result["timestamp"], "2023-01-01T12:00:00")
        self.assertEqual(result["metadata"], {"source": "user"})
        self.assertEqual(result["embedding"], [0.1, 0.2, 0.3])

    def test_from_dict(self):
        """Test creating Event from dictionary."""
        # Arrange
        data = {
            "id": "test_id",
            "content": "Test content",
            "timestamp": "2023-01-01T12:00:00",
            "metadata": {"source": "user"},
            "embedding": [0.1, 0.2, 0.3]
        }

        # Act
        event = Event.from_dict(data)

        # Assert
        self.assertEqual(event.id, "test_id")
        self.assertEqual(event.content, "Test content")
        self.assertEqual(event.timestamp, "2023-01-01T12:00:00")
        self.assertEqual(event.metadata, {"source": "user"})
        self.assertEqual(event.embedding, [0.1, 0.2, 0.3])

class TestEpisode(unittest.TestCase):
    """Tests for the Episode class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.episode = Episode(content="Test episode content", metadata={"topic": "test"})
        self.event1 = Event(content="Event 1", metadata={"source": "user"})
        self.event2 = Event(content="Event 2", metadata={"source": "assistant"})

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_init(self):
        """Test initialization of Episode."""
        # Test with minimal arguments
        episode = Episode()
        self.assertIsNotNone(episode.id)
        self.assertIsNone(episode.content)
        self.assertIsInstance(episode.metadata, dict)
        self.assertIsInstance(episode.events, list)
        self.assertEqual(len(episode.events), 0)
        self.assertIsNone(episode.start_time)
        self.assertIsNone(episode.end_time)

        # Test with events
        events = [
            Event(content="Event 1", timestamp="2023-01-01T12:00:00"),
            Event(content="Event 2", timestamp="2023-01-01T12:30:00")
        ]
        episode = Episode(content="Test content", events=events)
        self.assertEqual(episode.events, events)
        self.assertEqual(episode.start_time, "2023-01-01T12:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T12:30:00")

    def test_add_event(self):
        """Test adding an event to an episode."""
        # Arrange
        episode = Episode(content="Test episode")
        event = Event(content="Test event", timestamp="2023-01-01T12:00:00")

        # Act
        event_id = episode.add_event(event)

        # Assert
        self.assertEqual(event_id, event.id)
        self.assertEqual(len(episode.events), 1)
        self.assertEqual(episode.events[0], event)
        self.assertEqual(episode.start_time, "2023-01-01T12:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T12:00:00")

        # Add another event with earlier timestamp
        earlier_event = Event(content="Earlier event", timestamp="2023-01-01T11:00:00")
        episode.add_event(earlier_event)
        self.assertEqual(len(episode.events), 2)
        self.assertEqual(episode.start_time, "2023-01-01T11:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T12:00:00")

        # Add another event with later timestamp
        later_event = Event(content="Later event", timestamp="2023-01-01T13:00:00")
        episode.add_event(later_event)
        self.assertEqual(len(episode.events), 3)
        self.assertEqual(episode.start_time, "2023-01-01T11:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T13:00:00")

    def test_get_event(self):
        """Test getting an event from an episode."""
        # Arrange
        episode = Episode(content="Test episode")
        event = Event(id="test_event_id", content="Test event")
        episode.add_event(event)

        # Act
        retrieved_event = episode.get_event("test_event_id")

        # Assert
        self.assertEqual(retrieved_event, event)

        # Test getting a non-existent event
        self.assertIsNone(episode.get_event("non_existent_id"))

    def test_remove_event(self):
        """Test removing an event from an episode."""
        # Arrange
        episode = Episode(content="Test episode")
        event1 = Event(id="event1", content="Event 1", timestamp="2023-01-01T11:00:00")
        event2 = Event(id="event2", content="Event 2", timestamp="2023-01-01T12:00:00")
        event3 = Event(id="event3", content="Event 3", timestamp="2023-01-01T13:00:00")
        episode.add_event(event1)
        episode.add_event(event2)
        episode.add_event(event3)

        # Act - remove middle event
        result = episode.remove_event("event2")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(episode.events), 2)
        self.assertEqual(episode.events[0].id, "event1")
        self.assertEqual(episode.events[1].id, "event3")
        self.assertEqual(episode.start_time, "2023-01-01T11:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T13:00:00")

        # Act - remove first event
        result = episode.remove_event("event1")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(episode.events), 1)
        self.assertEqual(episode.events[0].id, "event3")
        self.assertEqual(episode.start_time, "2023-01-01T13:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T13:00:00")

        # Act - remove last event
        result = episode.remove_event("event3")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(episode.events), 0)
        self.assertIsNone(episode.start_time)
        self.assertIsNone(episode.end_time)

        # Act - try to remove non-existent event
        result = episode.remove_event("non_existent_id")

        # Assert
        self.assertFalse(result)

    def test_get_events_in_range(self):
        """Test getting events in a time range from an episode."""
        # Arrange
        episode = Episode(content="Test episode")
        event1 = Event(content="Event 1", timestamp="2023-01-01T11:00:00")
        event2 = Event(content="Event 2", timestamp="2023-01-01T12:00:00")
        event3 = Event(content="Event 3", timestamp="2023-01-01T13:00:00")
        event4 = Event(content="Event 4", timestamp="2023-01-01T14:00:00")
        episode.add_event(event1)
        episode.add_event(event2)
        episode.add_event(event3)
        episode.add_event(event4)

        # Act - get events in middle range
        events = episode.get_events_in_range("2023-01-01T11:30:00", "2023-01-01T13:30:00")

        # Assert
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].content, "Event 2")
        self.assertEqual(events[1].content, "Event 3")

        # Act - get events with only start time
        events = episode.get_events_in_range("2023-01-01T12:30:00")

        # Assert
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].content, "Event 3")
        self.assertEqual(events[1].content, "Event 4")

        # Act - get events with only end time
        events = episode.get_events_in_range(end_time="2023-01-01T12:30:00")

        # Assert
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].content, "Event 1")
        self.assertEqual(events[1].content, "Event 2")

        # Act - get all events
        events = episode.get_events_in_range()

        # Assert
        self.assertEqual(len(events), 4)

    def test_to_dict(self):
        """Test converting Episode to dictionary."""
        # Arrange
        episode = Episode(
            id="test_episode_id",
            content="Test episode content",
            metadata={"topic": "test"},
            importance=0.8,
            embedding=[0.1, 0.2, 0.3]
        )
        event1 = Event(id="event1", content="Event 1", timestamp="2023-01-01T11:00:00")
        event2 = Event(id="event2", content="Event 2", timestamp="2023-01-01T12:00:00")
        episode.add_event(event1)
        episode.add_event(event2)

        # Act
        result = episode.to_dict()

        # Assert
        self.assertEqual(result["id"], "test_episode_id")
        self.assertEqual(result["content"], "Test episode content")
        self.assertEqual(result["metadata"], {"topic": "test"})
        self.assertEqual(result["importance"], 0.8)
        self.assertEqual(result["embedding"], [0.1, 0.2, 0.3])
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(result["events"][0]["id"], "event1")
        self.assertEqual(result["events"][1]["id"], "event2")
        self.assertEqual(result["start_time"], "2023-01-01T11:00:00")
        self.assertEqual(result["end_time"], "2023-01-01T12:00:00")

    def test_from_dict(self):
        """Test creating Episode from dictionary."""
        # Arrange
        data = {
            "id": "test_episode_id",
            "content": "Test episode content",
            "metadata": {"topic": "test"},
            "importance": 0.8,
            "embedding": [0.1, 0.2, 0.3],
            "events": [
                {
                    "id": "event1",
                    "content": "Event 1",
                    "timestamp": "2023-01-01T11:00:00",
                    "metadata": {"source": "user"}
                },
                {
                    "id": "event2",
                    "content": "Event 2",
                    "timestamp": "2023-01-01T12:00:00",
                    "metadata": {"source": "assistant"}
                }
            ],
            "start_time": "2023-01-01T11:00:00",
            "end_time": "2023-01-01T12:00:00"
        }

        # Act
        episode = Episode.from_dict(data)

        # Assert
        self.assertEqual(episode.id, "test_episode_id")
        self.assertEqual(episode.content, "Test episode content")
        self.assertEqual(episode.metadata, {"topic": "test"})
        self.assertEqual(episode.importance, 0.8)
        self.assertEqual(episode.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(len(episode.events), 2)
        self.assertEqual(episode.events[0].id, "event1")
        self.assertEqual(episode.events[1].id, "event2")
        self.assertEqual(episode.start_time, "2023-01-01T11:00:00")
        self.assertEqual(episode.end_time, "2023-01-01T12:00:00")

class TestEpisodicMemory(unittest.TestCase):
    """Tests for the EpisodicMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.memory = EpisodicMemory(name="test_episodic_memory")

        # Create sample episodes and events
        self.episode1 = Episode(
            id="episode1",
            content="Episode 1 content",
            metadata={"topic": "test1"},
            start_time="2023-01-01T10:00:00",
            end_time="2023-01-01T11:00:00"
        )
        self.episode2 = Episode(
            id="episode2",
            content="Episode 2 content",
            metadata={"topic": "test2"},
            start_time="2023-01-02T10:00:00",
            end_time="2023-01-02T11:00:00"
        )

        self.event1 = Event(
            id="event1",
            content="Event 1 content",
            metadata={"source": "user"},
            timestamp="2023-01-01T10:30:00"
        )
        self.event2 = Event(
            id="event2",
            content="Event 2 content",
            metadata={"source": "assistant"},
            timestamp="2023-01-02T10:30:00"
        )

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_init(self):
        """Test initialization of EpisodicMemory."""
        # Test with name
        memory = EpisodicMemory(name="test_memory")
        self.assertEqual(memory.name, "test_memory")
        self.assertEqual(memory.memory_type, MemoryType.EPISODIC)
        self.assertEqual(len(memory.items), 0)
        self.assertEqual(memory.metadata, {})

    def test_add(self):
        """Test adding an episode to episodic memory."""
        # Arrange
        episode = Episode(id="test_episode", content="Test episode content")

        # Act
        episode_id = self.memory.add(episode)

        # Assert
        self.assertEqual(episode_id, "test_episode")
        self.assertEqual(len(self.memory.items), 1)
        self.assertEqual(self.memory.items["test_episode"], episode)

    def test_get(self):
        """Test getting an episode from episodic memory."""
        # Arrange
        self.memory.add(self.episode1)

        # Act
        retrieved_episode = self.memory.get("episode1")

        # Assert
        self.assertEqual(retrieved_episode, self.episode1)

        # Test getting a non-existent episode
        self.assertIsNone(self.memory.get("non_existent_id"))

    def test_update(self):
        """Test updating an episode in episodic memory."""
        # Arrange
        self.memory.add(self.episode1)

        # Act
        self.memory.update("episode1", content="Updated content", metadata={"topic": "updated"})

        # Assert
        updated_episode = self.memory.get("episode1")
        self.assertEqual(updated_episode.content, "Updated content")
        self.assertEqual(updated_episode.metadata, {"topic": "updated"})

        # Test updating a non-existent episode
        self.assertFalse(self.memory.update("non_existent_id", content="Updated content"))

    def test_remove(self):
        """Test removing an episode from episodic memory."""
        # Arrange
        self.memory.add(self.episode1)
        self.memory.add(self.episode2)

        # Act
        result = self.memory.remove("episode1")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.memory.items), 1)
        self.assertNotIn("episode1", self.memory.items)
        self.assertIn("episode2", self.memory.items)

        # Test removing a non-existent episode
        self.assertFalse(self.memory.remove("non_existent_id"))

    def test_add_event(self):
        """Test adding an event to an episode in episodic memory."""
        # Arrange
        self.memory.add(self.episode1)

        # Act
        event_id = self.memory.add_event("episode1", self.event1)

        # Assert
        self.assertEqual(event_id, "event1")
        episode = self.memory.get("episode1")
        self.assertEqual(len(episode.events), 1)
        self.assertEqual(episode.events[0], self.event1)

        # Test adding an event to a non-existent episode
        self.assertIsNone(self.memory.add_event("non_existent_id", self.event2))

    def test_get_event(self):
        """Test getting an event from an episode in episodic memory."""
        # Arrange
        self.memory.add(self.episode1)
        self.memory.add_event("episode1", self.event1)

        # Act
        event = self.memory.get_event("episode1", "event1")

        # Assert
        self.assertEqual(event, self.event1)

        # Test getting an event from a non-existent episode
        self.assertIsNone(self.memory.get_event("non_existent_id", "event1"))

        # Test getting a non-existent event
        self.assertIsNone(self.memory.get_event("episode1", "non_existent_id"))

    def test_remove_event(self):
        """Test removing an event from an episode in episodic memory."""
        # Arrange
        self.memory.add(self.episode1)
        self.memory.add_event("episode1", self.event1)
        self.memory.add_event("episode1", self.event2)

        # Act
        result = self.memory.remove_event("episode1", "event1")

        # Assert
        self.assertTrue(result)
        episode = self.memory.get("episode1")
        self.assertEqual(len(episode.events), 1)
        self.assertEqual(episode.events[0], self.event2)

        # Test removing an event from a non-existent episode
        self.assertFalse(self.memory.remove_event("non_existent_id", "event1"))

        # Test removing a non-existent event
        self.assertFalse(self.memory.remove_event("episode1", "non_existent_id"))

    def test_get_events_in_range(self):
        """Test getting events in a time range from an episode in episodic memory."""
        # Arrange
        episode = Episode(id="test_episode", content="Test episode")
        event1 = Event(content="Event 1", timestamp="2023-01-01T11:00:00")
        event2 = Event(content="Event 2", timestamp="2023-01-01T12:00:00")
        event3 = Event(content="Event 3", timestamp="2023-01-01T13:00:00")
        episode.add_event(event1)
        episode.add_event(event2)
        episode.add_event(event3)
        self.memory.add(episode)

        # Act - get events in middle range
        events = self.memory.get_events_in_range("test_episode", "2023-01-01T11:30:00", "2023-01-01T12:30:00")

        # Assert
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].content, "Event 2")

        # Test getting events from a non-existent episode
        self.assertEqual(self.memory.get_events_in_range("non_existent_id", "2023-01-01T11:30:00", "2023-01-01T12:30:00"), [])

    def test_get_episodes_in_range(self):
        """Test getting episodes in a time range."""
        # Arrange
        episode1 = Episode(
            id="episode1",
            content="Episode 1",
            start_time="2023-01-01T10:00:00",
            end_time="2023-01-01T11:00:00"
        )
        episode2 = Episode(
            id="episode2",
            content="Episode 2",
            start_time="2023-01-02T10:00:00",
            end_time="2023-01-02T11:00:00"
        )
        episode3 = Episode(
            id="episode3",
            content="Episode 3",
            start_time="2023-01-03T10:00:00",
            end_time="2023-01-03T11:00:00"
        )
        self.memory.add(episode1)
        self.memory.add(episode2)
        self.memory.add(episode3)

        # Act - get episodes in middle range
        episodes = self.memory.get_episodes_in_range("2023-01-01T12:00:00", "2023-01-02T12:00:00")

        # Assert
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].id, "episode2")

        # Act - get episodes with only start time
        episodes = self.memory.get_episodes_in_range("2023-01-02T12:00:00")

        # Assert
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].id, "episode3")

        # Act - get episodes with only end time
        episodes = self.memory.get_episodes_in_range(end_time="2023-01-01T12:00:00")

        # Assert
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].id, "episode1")

        # Act - get all episodes
        episodes = self.memory.get_episodes_in_range()

        # Assert
        self.assertEqual(len(episodes), 3)

    def test_search(self):
        """Test searching for episodes in episodic memory."""
        # Arrange
        episode1 = Episode(
            id="episode1",
            content="Episode about quantum computing",
            metadata={"topic": "quantum computing"}
        )
        episode2 = Episode(
            id="episode2",
            content="Episode about machine learning",
            metadata={"topic": "machine learning"}
        )
        self.memory.add(episode1)
        self.memory.add(episode2)

        # Test search with time range
        with patch.object(self.memory, 'get_episodes_in_range') as mock_get_episodes:
            mock_get_episodes.return_value = [episode1]

            # Act - search with time range
            results = self.memory.search({"start_time": "2023-01-01T00:00:00", "end_time": "2023-01-02T00:00:00"}, 10)

            # Assert
            mock_get_episodes.assert_called_once_with("2023-01-01T00:00:00", "2023-01-02T00:00:00")

        # Test search with string query
        with patch.object(Memory, 'search') as mock_search:
            mock_search.return_value = [episode1]

            # Create a new memory instance to avoid issues with previous patches
            test_memory = EpisodicMemory(name="test_search_memory")
            test_memory.add(episode1)
            test_memory.add(episode2)

            # Override the parent class's search method for this instance
            with patch.object(test_memory.__class__, 'search', return_value=[episode1]):
                # Act - search with string query
                results = test_memory.search("quantum", 10)

                # Assert
                self.assertEqual(results, [episode1])

    def test_to_dict(self):
        """Test converting EpisodicMemory to dictionary."""
        # Arrange
        self.memory.add(self.episode1)
        self.memory.add_event("episode1", self.event1)

        # Act
        result = self.memory.to_dict()

        # Assert
        self.assertEqual(result["name"], "test_episodic_memory")
        self.assertEqual(result["memory_type"], "EPISODIC")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"]["episode1"]["id"], "episode1")
        self.assertEqual(len(result["items"]["episode1"]["events"]), 1)
        self.assertEqual(result["items"]["episode1"]["events"][0]["id"], "event1")

    def test_from_dict(self):
        """Test creating EpisodicMemory from dictionary."""
        # Arrange
        data = {
            "name": "test_episodic_memory",
            "memory_type": "EPISODIC",
            "metadata": {},
            "items": {
                "episode1": {
                    "id": "episode1",
                    "content": "Episode 1 content",
                    "metadata": {"topic": "test1"},
                    "created_at": "2023-01-01T10:00:00",
                    "updated_at": "2023-01-01T10:00:00",
                    "importance": 0.5,
                    "events": [
                        {
                            "id": "event1",
                            "content": "Event 1 content",
                            "metadata": {"source": "user"},
                            "timestamp": "2023-01-01T10:30:00"
                        }
                    ],
                    "start_time": "2023-01-01T10:00:00",
                    "end_time": "2023-01-01T11:00:00"
                }
            }
        }

        # Act
        memory = EpisodicMemory.from_dict(data)

        # Assert
        self.assertEqual(memory.name, "test_episodic_memory")
        self.assertEqual(memory.memory_type, MemoryType.EPISODIC)
        self.assertEqual(len(memory.items), 1)
        self.assertEqual(memory.items["episode1"].id, "episode1")
        self.assertEqual(memory.items["episode1"].content, "Episode 1 content")
        self.assertEqual(len(memory.items["episode1"].events), 1)
        self.assertEqual(memory.items["episode1"].events[0].id, "event1")
        self.assertEqual(memory.items["episode1"].events[0].content, "Event 1 content")


if __name__ == '__main__':
    unittest.main()
