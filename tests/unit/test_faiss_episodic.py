"""Unit tests for the FAISS-based episodic memory.

This module contains unit tests for the FAISS-based episodic memory,
testing the core functionality of the FAISSEpisodicMemory class.

Version: 0.1.0
Created: 2025-04-24
"""

import os
import time
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import pytest

from dukat.memory.faiss_episodic import FAISSEpisodicMemory, Episode


class TestFAISSEpisodicMemory(unittest.TestCase):
    """Test the FAISSEpisodicMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.persist_dir = os.path.join(self.temp_dir.name, "faiss_episodic")

        # Create a real FAISS episodic memory instance for testing
        self.memory = FAISSEpisodicMemory(
            persist_dir=self.persist_dir,
            collection_name="test_episodes",
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def test_init(self):
        """Test that FAISSEpisodicMemory initializes correctly."""
        # Check that the memory was initialized correctly
        self.assertEqual(self.memory.persist_dir, self.persist_dir)
        self.assertEqual(self.memory.collection_name, "test_episodes")
        self.assertIsNotNone(self.memory.memory)

    def test_add_episode(self):
        """Test adding an episode."""
        # Add an episode
        episode = self.memory.add_episode(
            content="This is a test episode",
            title="Test Episode",
            metadata={"type": "conversation", "tags": ["test", "example"]},
        )

        # Check that the episode was added
        self.assertIsNotNone(episode)
        self.assertTrue(episode.id.startswith("ep_"))
        self.assertEqual(episode.title, "Test Episode")
        self.assertEqual(episode.content, "This is a test episode")
        self.assertEqual(episode.metadata["type"], "conversation")
        self.assertEqual(episode.metadata["tags"], ["test", "example"])

    def test_get_episode(self):
        """Test getting an episode by ID."""
        # Add an episode
        episode = self.memory.add_episode(
            content="This is a test episode",
            title="Test Episode",
            metadata={"type": "conversation"},
        )

        # Get the episode by ID
        retrieved_episode = self.memory.get_episode(episode.id)

        # Check that the episode was retrieved
        self.assertIsNotNone(retrieved_episode)
        self.assertEqual(retrieved_episode.id, episode.id)
        self.assertEqual(retrieved_episode.title, "Test Episode")
        self.assertEqual(retrieved_episode.content, "This is a test episode")
        self.assertEqual(retrieved_episode.metadata["type"], "conversation")

    def test_search_episodes(self):
        """Test searching for episodes."""
        # Add some episodes
        self.memory.add_episode(
            content="Python is a programming language",
            title="Python Programming",
            metadata={"topic": "programming", "language": "python"},
        )
        self.memory.add_episode(
            content="JavaScript is a programming language",
            title="JavaScript Programming",
            metadata={"topic": "programming", "language": "javascript"},
        )
        self.memory.add_episode(
            content="The weather is nice today",
            title="Weather Report",
            metadata={"topic": "weather"},
        )

        # Search for episodes
        results = self.memory.search_episodes(
            query="programming language",
            n_results=10,
        )

        # Check that the episodes were found
        self.assertEqual(len(results), 2)
        titles = [episode.title for episode, _ in results]
        self.assertIn("Python Programming", titles)
        self.assertIn("JavaScript Programming", titles)

        # Search with filter
        results = self.memory.search_episodes(
            query="programming language",
            n_results=10,
            filter_metadata={"language": "python"},
        )

        # Check that only Python episodes were found
        self.assertEqual(len(results), 1)
        episode, _ = results[0]
        self.assertEqual(episode.title, "Python Programming")

    def test_get_recent_episodes(self):
        """Test getting recent episodes."""
        # Add episodes with different timestamps
        old_timestamp = int(time.time()) - 100
        new_timestamp = int(time.time())

        # Add an old episode
        old_episode = Episode(
            content="This is an old episode",
            title="Old Episode",
            timestamp=old_timestamp,
            metadata={"type": "conversation"},
        )
        self.memory.memory.add(
            text=old_episode.content,
            metadata={
                "title": old_episode.title,
                "timestamp": old_episode.timestamp,
                "type": "conversation",
            },
            collection_name=self.memory.collection_name,
            id_prefix=old_episode.id,
        )

        # Add a new episode
        new_episode = Episode(
            content="This is a new episode",
            title="New Episode",
            timestamp=new_timestamp,
            metadata={"type": "conversation"},
        )
        self.memory.memory.add(
            text=new_episode.content,
            metadata={
                "title": new_episode.title,
                "timestamp": new_episode.timestamp,
                "type": "conversation",
            },
            collection_name=self.memory.collection_name,
            id_prefix=new_episode.id,
        )

        # Get recent episodes
        episodes = self.memory.get_recent_episodes(n=2)

        # Check that the episodes were retrieved in the correct order
        self.assertEqual(len(episodes), 2)
        self.assertEqual(episodes[0].title, "New Episode")  # Newest first
        self.assertEqual(episodes[1].title, "Old Episode")

        # Get recent episodes with filter
        episodes = self.memory.get_recent_episodes(
            n=2,
            filter_metadata={"type": "conversation"},
        )

        # Check that the episodes were retrieved with the filter
        self.assertEqual(len(episodes), 2)

    def test_get_episodes_in_timerange(self):
        """Test getting episodes in a time range."""
        # Add episodes with different timestamps
        timestamp1 = 1000
        timestamp2 = 2000
        timestamp3 = 3000

        # Add episodes
        episode1 = Episode(
            content="Episode at time 1000",
            title="Episode 1",
            timestamp=timestamp1,
            metadata={"type": "conversation"},
        )
        self.memory.memory.add(
            text=episode1.content,
            metadata={
                "title": episode1.title,
                "timestamp": episode1.timestamp,
                "type": "conversation",
            },
            collection_name=self.memory.collection_name,
            id_prefix=episode1.id,
        )

        episode2 = Episode(
            content="Episode at time 2000",
            title="Episode 2",
            timestamp=timestamp2,
            metadata={"type": "conversation"},
        )
        self.memory.memory.add(
            text=episode2.content,
            metadata={
                "title": episode2.title,
                "timestamp": episode2.timestamp,
                "type": "conversation",
            },
            collection_name=self.memory.collection_name,
            id_prefix=episode2.id,
        )

        episode3 = Episode(
            content="Episode at time 3000",
            title="Episode 3",
            timestamp=timestamp3,
            metadata={"type": "note"},
        )
        self.memory.memory.add(
            text=episode3.content,
            metadata={
                "title": episode3.title,
                "timestamp": episode3.timestamp,
                "type": "note",
            },
            collection_name=self.memory.collection_name,
            id_prefix=episode3.id,
        )

        # Get episodes in a time range
        episodes = self.memory.get_episodes_in_timerange(
            start_time=1500,
            end_time=2500,
        )

        # Check that the correct episodes were retrieved
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].title, "Episode 2")

        # Get episodes in a time range with filter
        episodes = self.memory.get_episodes_in_timerange(
            start_time=500,
            end_time=3500,
            filter_metadata={"type": "conversation"},
        )

        # Check that the correct episodes were retrieved
        self.assertEqual(len(episodes), 2)
        titles = [episode.title for episode in episodes]
        self.assertIn("Episode 1", titles)
        self.assertIn("Episode 2", titles)

    def test_delete_episode(self):
        """Test deleting an episode."""
        # Add an episode
        episode = self.memory.add_episode(
            content="This is a test episode",
            title="Test Episode",
            metadata={"type": "conversation"},
        )

        # Delete the episode
        result = self.memory.delete_episode(episode.id)

        # Check that the episode was deleted
        self.assertTrue(result)

        # Try to get the deleted episode
        retrieved_episode = self.memory.get_episode(episode.id)

        # Check that the episode is gone
        self.assertIsNone(retrieved_episode)

    def test_clear(self):
        """Test clearing all episodes."""
        # Add some episodes
        self.memory.add_episode(
            content="Episode 1",
            title="Episode 1",
            metadata={"type": "conversation"},
        )
        self.memory.add_episode(
            content="Episode 2",
            title="Episode 2",
            metadata={"type": "conversation"},
        )

        # Clear all episodes
        result = self.memory.clear()

        # Check that the episodes were cleared
        self.assertTrue(result)

        # Try to search for episodes
        results = self.memory.search_episodes(
            query="episode",
            n_results=10,
        )

        # Check that no episodes were found
        self.assertEqual(len(results), 0)

    def test_add_empty_content(self):
        """Test adding an episode with empty content."""
        # Try to add an episode with empty content
        with self.assertRaises(ValueError):
            self.memory.add_episode(
                content="",
                title="Empty Episode",
            )

    def test_episode_to_dict(self):
        """Test converting an episode to a dictionary."""
        # Create an episode
        episode = Episode(
            content="This is a test episode",
            title="Test Episode",
            timestamp=1000,
            metadata={"type": "conversation"},
            episode_id="ep_12345678",
        )

        # Convert to dictionary
        data = episode.to_dict()

        # Check the dictionary
        self.assertEqual(data["id"], "ep_12345678")
        self.assertEqual(data["title"], "Test Episode")
        self.assertEqual(data["content"], "This is a test episode")
        self.assertEqual(data["timestamp"], 1000)
        self.assertEqual(data["metadata"]["type"], "conversation")

    def test_episode_from_dict(self):
        """Test creating an episode from a dictionary."""
        # Create a dictionary
        data = {
            "id": "ep_12345678",
            "title": "Test Episode",
            "content": "This is a test episode",
            "timestamp": 1000,
            "metadata": {"type": "conversation"},
        }

        # Create an episode from the dictionary
        episode = Episode.from_dict(data)

        # Check the episode
        self.assertEqual(episode.id, "ep_12345678")
        self.assertEqual(episode.title, "Test Episode")
        self.assertEqual(episode.content, "This is a test episode")
        self.assertEqual(episode.timestamp, 1000)
        self.assertEqual(episode.metadata["type"], "conversation")

    def test_episode_str(self):
        """Test the string representation of an episode."""
        # Create an episode
        episode = Episode(
            content="This is a test episode with a very long content that should be truncated",
            title="Test Episode",
            episode_id="ep_12345678",
        )

        # Get the string representation
        string = str(episode)

        # Check the string
        self.assertEqual(
            string, "Test Episode (ep_12345678): This is a test episode with a very long content that...")


if __name__ == "__main__":
    unittest.main()
