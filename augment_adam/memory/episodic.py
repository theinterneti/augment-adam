"""Episodic memory for the Dukat assistant.

This module provides the episodic memory functionality for
storing and retrieving past interactions and experiences.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from datetime import datetime
import time
import os
import json
from pathlib import Path
import uuid

import chromadb
from chromadb.config import Settings
import numpy as np

# Ensure compatibility with NumPy 2.0+
if not hasattr(np, 'float_'):
    np.float_ = np.float64

logger = logging.getLogger(__name__)


class Episode:
    """An episode in the assistant's memory.

    This class represents an episode, which is a record of
    an interaction or experience.

    Attributes:
        id: The unique identifier for the episode.
        title: A short title for the episode.
        content: The content of the episode.
        timestamp: The timestamp when the episode was created.
        metadata: Additional metadata for the episode.
    """

    def __init__(
        self,
        content: str,
        title: Optional[str] = None,
        timestamp: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        episode_id: Optional[str] = None,
    ):
        """Initialize an episode.

        Args:
            content: The content of the episode.
            title: A short title for the episode.
            timestamp: The timestamp when the episode was created.
            metadata: Additional metadata for the episode.
            episode_id: The unique identifier for the episode.
        """
        self.id = episode_id or f"ep_{uuid.uuid4().hex[:8]}"
        self.title = title or f"Episode {self.id}"
        self.content = content
        self.timestamp = timestamp or int(time.time())
        self.metadata = metadata or {}

        logger.debug(f"Created episode {self.id}: {self.title}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the episode to a dictionary.

        Returns:
            A dictionary representation of the episode.
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        """Create an episode from a dictionary.

        Args:
            data: A dictionary representation of the episode.

        Returns:
            A new Episode instance.
        """
        return cls(
            content=data["content"],
            title=data.get("title"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
            episode_id=data.get("id"),
        )

    def __str__(self) -> str:
        """Get a string representation of the episode.

        Returns:
            A string representation of the episode.
        """
        # Ensure the content is truncated to exactly match the test expectation
        return f"{self.title} ({self.id}): {self.content[:50]}..."


class EpisodicMemory:
    """Episodic memory for the Dukat assistant.

    This class manages the storage and retrieval of episodes,
    which are records of past interactions and experiences.

    Attributes:
        persist_dir: Directory to persist memory data.
        client: ChromaDB client for vector storage.
        collection: ChromaDB collection for episodes.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "augment_adam_episodes",
    ):
        """Initialize the episodic memory.

        Args:
            persist_dir: Directory to persist memory data.
            collection_name: Name of the collection.
        """
        self.persist_dir = persist_dir or os.path.expanduser(
            "~/.augment_adam/memory/episodic")

        # Create directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)

        logger.info(
            f"Initializing episodic memory with persist_dir: {self.persist_dir}")

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Initialize collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Episodic memory collection for Dukat"}
        )

        logger.info(f"Initialized collection: {collection_name}")

    def add_episode(
        self,
        content: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        """Add an episode to the memory.

        Args:
            content: The content of the episode.
            title: A short title for the episode.
            metadata: Additional metadata for the episode.

        Returns:
            The added episode.
        """
        if not content:
            logger.warning("Attempted to add empty content to episodic memory")
            raise ValueError("Episode content cannot be empty")

        # Create the episode
        episode = Episode(
            content=content,
            title=title,
            metadata=metadata or {},
        )

        try:
            # Add the episode to the collection
            self.collection.add(
                documents=[episode.content],
                metadatas=[{
                    "title": episode.title,
                    "timestamp": episode.timestamp,
                    **episode.metadata,
                }],
                ids=[episode.id],
            )

            logger.info(f"Added episode: {episode.id}")
            return episode

        except Exception as e:
            logger.error(f"Error adding episode: {str(e)}")
            raise RuntimeError(f"Error adding episode: {str(e)}")

    def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get an episode by ID.

        Args:
            episode_id: The ID of the episode to retrieve.

        Returns:
            The episode, or None if not found.
        """
        try:
            # Get the episode from the collection
            result = self.collection.get(
                ids=[episode_id],
                include=["documents", "metadatas"],
            )

            if not result["ids"]:
                logger.warning(f"Episode {episode_id} not found")
                return None

            # Create an episode from the result
            metadata = result["metadatas"][0]
            timestamp = metadata.pop("timestamp", None)
            title = metadata.pop("title", None)

            episode = Episode(
                content=result["documents"][0],
                title=title,
                timestamp=timestamp,
                metadata=metadata,
                episode_id=result["ids"][0],
            )

            logger.info(f"Retrieved episode: {episode.id}")
            return episode

        except Exception as e:
            logger.error(f"Error retrieving episode: {str(e)}")
            return None

    def search_episodes(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Episode, float]]:
        """Search for episodes by content.

        Args:
            query: The query to search for.
            n_results: Maximum number of results to return.
            filter_metadata: Metadata filters to apply.

        Returns:
            A list of episodes with their similarity scores.
        """
        try:
            # Search the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"],
            )

            # Create episodes from the results
            episodes = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                timestamp = metadata.pop("timestamp", None)
                title = metadata.pop("title", None)

                episode = Episode(
                    content=doc,
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=results["ids"][0][i],
                )

                distance = results["distances"][0][i] if "distances" in results else 1.0
                episodes.append((episode, distance))

            logger.info(
                f"Found {len(episodes)} episodes for query: {query[:50]}...")
            return episodes

        except Exception as e:
            logger.error(f"Error searching episodes: {str(e)}")
            return []

    def get_recent_episodes(
        self,
        n: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Episode]:
        """Get the most recent episodes.

        Args:
            n: Maximum number of episodes to return.
            filter_metadata: Metadata filters to apply.

        Returns:
            A list of episodes.
        """
        try:
            # Get all episodes
            results = self.collection.get(
                where=filter_metadata,
                include=["documents", "metadatas", "ids"],
            )

            # Create episodes from the results
            episodes = []
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                timestamp = metadata.pop("timestamp", None)
                title = metadata.pop("title", None)

                episode = Episode(
                    content=doc,
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=results["ids"][i],
                )

                episodes.append(episode)

            # Sort by timestamp (newest first)
            episodes.sort(key=lambda e: e.timestamp, reverse=True)

            # Limit the number of episodes
            episodes = episodes[:n]

            logger.info(f"Retrieved {len(episodes)} recent episodes")
            return episodes

        except Exception as e:
            logger.error(f"Error retrieving recent episodes: {str(e)}")
            return []

    def delete_episode(self, episode_id: str) -> bool:
        """Delete an episode.

        Args:
            episode_id: The ID of the episode to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Delete the episode from the collection
            self.collection.delete(
                ids=[episode_id],
            )

            logger.info(f"Deleted episode: {episode_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting episode: {str(e)}")
            return False

    def update_episode(
        self,
        episode_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update an episode.

        Args:
            episode_id: The ID of the episode to update.
            content: The new content for the episode.
            title: The new title for the episode.
            metadata: The new metadata for the episode.

        Returns:
            True if successful, False otherwise.
        """
        # Get the current episode
        episode = self.get_episode(episode_id)
        if episode is None:
            logger.warning(f"Episode {episode_id} not found")
            return False

        # Update the episode
        if content is not None:
            episode.content = content

        if title is not None:
            episode.title = title

        if metadata is not None:
            episode.metadata.update(metadata)

        try:
            # Update the episode in the collection
            self.collection.update(
                documents=[episode.content],
                metadatas=[{
                    "title": episode.title,
                    "timestamp": episode.timestamp,
                    **episode.metadata,
                }],
                ids=[episode.id],
            )

            logger.info(f"Updated episode: {episode.id}")
            return True

        except Exception as e:
            logger.error(f"Error updating episode: {str(e)}")
            return False

    def clear(self) -> bool:
        """Clear all episodes from the memory.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Delete all episodes from the collection
            self.collection.delete(
                where={},
            )

            logger.info("Cleared all episodes")
            return True

        except Exception as e:
            logger.error(f"Error clearing episodes: {str(e)}")
            return False

    def count_episodes(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count the number of episodes.

        Args:
            filter_metadata: Metadata filters to apply.

        Returns:
            The number of episodes.
        """
        try:
            # Get all episodes
            results = self.collection.get(
                where=filter_metadata,
                include=["ids"],
            )

            count = len(results["ids"])
            logger.info(f"Counted {count} episodes")
            return count

        except Exception as e:
            logger.error(f"Error counting episodes: {str(e)}")
            return 0

    def get_episode_by_title(
        self,
        title: str,
        exact_match: bool = False,
    ) -> Optional[Episode]:
        """Get an episode by title.

        Args:
            title: The title to search for.
            exact_match: Whether to require an exact match.

        Returns:
            The episode, or None if not found.
        """
        try:
            # Search for episodes by title
            if exact_match:
                results = self.collection.get(
                    where={"title": title},
                    include=["documents", "metadatas", "ids"],
                )
            else:
                # Use a query to find similar titles
                results = self.collection.query(
                    query_texts=[title],
                    n_results=1,
                    include=["documents", "metadatas", "ids"],
                )

            if not results["ids"]:
                logger.warning(f"No episode found with title: {title}")
                return None

            # Create an episode from the result
            if exact_match:
                # For exact match, the structure is different
                if not results["ids"]:
                    return None

                metadata = results["metadatas"][0]
                timestamp = metadata.pop("timestamp", None)
                title = metadata.pop("title", None)

                episode = Episode(
                    content=results["documents"][0],
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=results["ids"][0],
                )
            else:
                # For fuzzy match, the structure is nested
                if not results["ids"][0]:
                    return None

                metadata = results["metadatas"][0][0]
                timestamp = metadata.pop("timestamp", None)
                title = metadata.pop("title", None)

                episode = Episode(
                    content=results["documents"][0][0],
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=results["ids"][0][0],
                )

            logger.info(f"Retrieved episode by title: {episode.id}")
            return episode

        except Exception as e:
            logger.error(f"Error retrieving episode by title: {str(e)}")
            return None

    def get_episodes_in_timerange(
        self,
        start_time: int,
        end_time: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Episode]:
        """Get episodes within a time range.

        Args:
            start_time: The start timestamp.
            end_time: The end timestamp.
            filter_metadata: Additional metadata filters to apply.

        Returns:
            A list of episodes.
        """
        try:
            # Prepare the filter
            time_filter = {
                "timestamp": {
                    "$gte": start_time,
                    "$lte": end_time,
                }
            }

            # Combine with additional filters
            if filter_metadata:
                combined_filter = {**time_filter, **filter_metadata}
            else:
                combined_filter = time_filter

            # Get episodes in the time range
            results = self.collection.get(
                where=combined_filter,
                include=["documents", "metadatas", "ids"],
            )

            # Create episodes from the results
            episodes = []
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                timestamp = metadata.pop("timestamp", None)
                title = metadata.pop("title", None)

                episode = Episode(
                    content=doc,
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=results["ids"][i],
                )

                episodes.append(episode)

            # Sort by timestamp
            episodes.sort(key=lambda e: e.timestamp)

            logger.info(f"Retrieved {len(episodes)} episodes in time range")
            return episodes

        except Exception as e:
            logger.error(f"Error retrieving episodes in time range: {str(e)}")
            return []
