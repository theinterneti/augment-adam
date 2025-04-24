"""FAISS-based episodic memory for the Augment Adam assistant.

This module provides FAISS-based episodic memory functionality."""

import os
import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from augment_adam.core.settings import get_settings
from augment_adam.core.errors import (
    ResourceError, DatabaseError, wrap_error, log_error, ErrorCategory
)
from augment_adam.memory.faiss_memory import FAISSMemory

logger = logging.getLogger(__name__)


class Episode:
    """An episode in episodic memory.

    This class represents an episode in episodic memory, which
    is a record of a past interaction or experience.

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


class FAISSEpisodicMemory:
    """FAISS-based episodic memory for the Augment Adam assistant."""

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "augment_adam_episodes",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """Initialize the episodic memory.

        Args:
            persist_dir: Directory to persist memory data.
            collection_name: Name of the collection.
            embedding_model: Name of the SentenceTransformer model to use for embeddings.
        """
        self.persist_dir = persist_dir or os.path.expanduser(
            "~/.augment_adam/memory/faiss_episodic")

        # Create directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)

        logger.info(
            f"Initializing FAISS episodic memory with persist_dir: {self.persist_dir}")

        # Initialize FAISS memory
        self.memory = FAISSMemory(
            persist_dir=self.persist_dir,
            collection_name=collection_name,
            embedding_model=embedding_model,
        )

        # Store collection name for later use
        self.collection_name = collection_name

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

        Raises:
            ValueError: If the episode content is empty.
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

        # Prepare metadata for storage
        storage_metadata = {
            **episode.metadata,
            "title": episode.title,
            "timestamp": episode.timestamp,
        }

        # Add to FAISS memory
        memory_id = self.memory.add(
            text=content,
            metadata=storage_metadata,
            collection_name=self.collection_name,
            id_prefix=episode.id,
        )

        if not memory_id:
            logger.error(f"Failed to add episode {episode.id} to memory")
            # Use the original ID since the add failed
            return episode

        # Update the episode ID to match the memory ID
        episode.id = memory_id

        logger.info(f"Added episode {episode.id} to memory")
        return episode

    def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get an episode by ID.

        Args:
            episode_id: The ID of the episode to get.

        Returns:
            The episode, or None if not found.
        """
        # Get from FAISS memory
        memory = self.memory.get_by_id(
            memory_id=episode_id,
            collection_name=self.collection_name,
        )

        if not memory:
            logger.warning(f"Episode {episode_id} not found")
            return None

        # Extract episode data
        content = memory.get("text", "")
        title = memory.get("title", f"Episode {episode_id}")
        timestamp = memory.get("timestamp", int(time.time()))

        # Remove known fields from metadata
        metadata = {k: v for k, v in memory.items() if k not in [
            "text", "title", "timestamp"]}

        # Create and return the episode
        episode = Episode(
            content=content,
            title=title,
            timestamp=timestamp,
            metadata=metadata,
            episode_id=episode_id,
        )

        return episode

    def search_episodes(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Episode, float]]:
        """Search for episodes based on a query.

        Args:
            query: The search query.
            n_results: Maximum number of results to return.
            filter_metadata: Filter to apply to the metadata.

        Returns:
            A list of tuples containing the episode and its similarity score.
        """
        if not query:
            logger.warning("Attempted to search with empty query")
            return []

        # Search in FAISS memory
        results = self.memory.retrieve(
            query=query,
            n_results=n_results,
            filter_metadata=filter_metadata,
            collection_name=self.collection_name,
        )

        # Convert to episodes
        episodes = []
        for memory, score in results:
            # Extract episode data
            content = memory.get("text", "")
            title = memory.get("title", "Unknown Episode")
            timestamp = memory.get("timestamp", int(time.time()))
            episode_id = memory.get("id", f"ep_{uuid.uuid4().hex[:8]}")

            # Remove known fields from metadata
            metadata = {k: v for k, v in memory.items() if k not in [
                "text", "title", "timestamp", "id"]}

            # Create the episode
            episode = Episode(
                content=content,
                title=title,
                timestamp=timestamp,
                metadata=metadata,
                episode_id=episode_id,
            )

            episodes.append((episode, score))

        return episodes

    def get_recent_episodes(
        self,
        n: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Episode]:
        """Get the most recent episodes.

        Args:
            n: Maximum number of episodes to return.
            filter_metadata: Filter to apply to the metadata.

        Returns:
            A list of episodes.
        """
        try:
            # Get all episodes
            all_episodes = []
            
            # Get all memory IDs
            memory_ids = self.memory.ids.get(self.collection_name, [])
            
            # Get metadata for each ID
            for memory_id in memory_ids:
                memory = self.memory.get_by_id(
                    memory_id=memory_id,
                    collection_name=self.collection_name,
                )
                
                if not memory:
                    continue
                
                # Apply metadata filter
                if filter_metadata:
                    skip = False
                    for key, value in filter_metadata.items():
                        if key not in memory or memory[key] != value:
                            skip = True
                            break
                    if skip:
                        continue
                
                # Extract episode data
                content = memory.get("text", "")
                title = memory.get("title", f"Episode {memory_id}")
                timestamp = memory.get("timestamp", 0)
                
                # Remove known fields from metadata
                metadata = {k: v for k, v in memory.items() if k not in [
                    "text", "title", "timestamp"]}
                
                # Create the episode
                episode = Episode(
                    content=content,
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=memory_id,
                )
                
                all_episodes.append(episode)
            
            # Sort by timestamp (newest first)
            all_episodes.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Return the most recent n episodes
            return all_episodes[:n]
        except Exception as e:
            # Handle errors
            error = wrap_error(
                e,
                message="Failed to get recent episodes",
                category=ErrorCategory.DATABASE,
                details={
                    "n": n,
                    "filter_metadata": filter_metadata,
                },
            )
            log_error(error, logger=logger)
            return []

    def get_episodes_in_timerange(
        self,
        start_time: int,
        end_time: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Episode]:
        """Get episodes in a time range.

        Args:
            start_time: Start timestamp (inclusive).
            end_time: End timestamp (inclusive).
            filter_metadata: Filter to apply to the metadata.

        Returns:
            A list of episodes.
        """
        try:
            # Get all episodes
            all_episodes = []
            
            # Get all memory IDs
            memory_ids = self.memory.ids.get(self.collection_name, [])
            
            # Get metadata for each ID
            for memory_id in memory_ids:
                memory = self.memory.get_by_id(
                    memory_id=memory_id,
                    collection_name=self.collection_name,
                )
                
                if not memory:
                    continue
                
                # Check timestamp
                timestamp = memory.get("timestamp", 0)
                if timestamp < start_time or timestamp > end_time:
                    continue
                
                # Apply metadata filter
                if filter_metadata:
                    skip = False
                    for key, value in filter_metadata.items():
                        if key not in memory or memory[key] != value:
                            skip = True
                            break
                    if skip:
                        continue
                
                # Extract episode data
                content = memory.get("text", "")
                title = memory.get("title", f"Episode {memory_id}")
                
                # Remove known fields from metadata
                metadata = {k: v for k, v in memory.items() if k not in [
                    "text", "title", "timestamp"]}
                
                # Create the episode
                episode = Episode(
                    content=content,
                    title=title,
                    timestamp=timestamp,
                    metadata=metadata,
                    episode_id=memory_id,
                )
                
                all_episodes.append(episode)
            
            # Sort by timestamp
            all_episodes.sort(key=lambda e: e.timestamp)
            
            return all_episodes
        except Exception as e:
            # Handle errors
            error = wrap_error(
                e,
                message="Failed to get episodes in time range",
                category=ErrorCategory.DATABASE,
                details={
                    "start_time": start_time,
                    "end_time": end_time,
                    "filter_metadata": filter_metadata,
                },
            )
            log_error(error, logger=logger)
            return []

    def delete_episode(self, episode_id: str) -> bool:
        """Delete an episode by ID.

        Args:
            episode_id: The ID of the episode to delete.

        Returns:
            True if the episode was deleted, False otherwise.
        """
        # Delete from FAISS memory
        result = self.memory.delete(
            memory_id=episode_id,
            collection_name=self.collection_name,
        )

        if result:
            logger.info(f"Deleted episode {episode_id}")
        else:
            logger.warning(f"Failed to delete episode {episode_id}")

        return result

    def clear(self) -> bool:
        """Clear all episodes from memory.

        Returns:
            True if the memory was cleared, False otherwise.
        """
        # Clear FAISS memory
        result = self.memory.clear(
            collection_name=self.collection_name,
        )

        if result:
            logger.info("Cleared all episodes from memory")
        else:
            logger.warning("Failed to clear episodes from memory")

        return result
