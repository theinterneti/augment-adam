"""Episodic Memory Implementation.

This module provides the episodic memory for agents.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """Episode in episodic memory.
    
    Attributes:
        id: Unique identifier for the episode
        content: Content of the episode
        title: Title of the episode
        timestamp: Timestamp when the episode was created
        metadata: Additional metadata for the episode
    """
    
    content: str
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    timestamp: float = field(default_factory=time.time)
    
    def __str__(self) -> str:
        """Get a string representation of the episode.
        
        Returns:
            String representation of the episode
        """
        title = self.title or "Untitled Episode"
        return f"{title} ({self.id}): {self.content[:50]}..."


class EpisodicMemory:
    """Episodic memory for agents.
    
    This class manages the storage and retrieval of episodes,
    which are records of past interactions and experiences.
    
    Attributes:
        name: Name of the episodic memory
        max_size: Maximum size of the episodic memory
        episodes: List of episodes in the memory
    """
    
    def __init__(
        self,
        name: str,
        max_size: int = 100
    ):
        """Initialize the episodic memory.
        
        Args:
            name: Name of the episodic memory
            max_size: Maximum size of the episodic memory
        """
        self.name = name
        self.max_size = max_size
        self.episodes = []
        
        logger.info(f"Initialized Episodic Memory '{name}' with max size {max_size}")
    
    def add_episode(
        self,
        content: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Episode:
        """Add an episode to the memory.
        
        Args:
            content: Content of the episode
            title: Title of the episode
            metadata: Additional metadata for the episode
            
        Returns:
            The added episode
            
        Raises:
            ValueError: If the episode content is empty
        """
        if not content:
            logger.warning("Attempted to add empty content to episodic memory")
            raise ValueError("Episode content cannot be empty")
        
        # Create the episode
        episode = Episode(
            content=content,
            title=title,
            metadata=metadata or {}
        )
        
        # Add to episodes
        self.episodes.append(episode)
        
        # Trim if necessary
        if len(self.episodes) > self.max_size:
            self.episodes = self.episodes[-self.max_size:]
        
        logger.info(f"Added episode with ID: {episode.id}")
        return episode
    
    def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get an episode by ID.
        
        Args:
            episode_id: ID of the episode to get
            
        Returns:
            The episode or None if not found
        """
        for episode in self.episodes:
            if episode.id == episode_id:
                return episode
        
        logger.warning(f"Episode with ID '{episode_id}' not found")
        return None
    
    def search_episodes(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Episode, float]]:
        """Search for episodes by content similarity.
        
        Args:
            query: Query to search for
            n_results: Maximum number of results to return
            filter_metadata: Metadata to filter by
            
        Returns:
            List of tuples containing episodes and their similarity scores
        """
        # Simple keyword matching for now
        # In a real implementation, this would use vector similarity search
        results = []
        
        for episode in self.episodes:
            # Check metadata filter if provided
            if filter_metadata:
                match = True
                for key, value in filter_metadata.items():
                    if key not in episode.metadata or episode.metadata[key] != value:
                        match = False
                        break
                
                if not match:
                    continue
            
            # Calculate simple similarity score
            query_words = set(query.lower().split())
            content_words = set(episode.content.lower().split())
            
            if not query_words:
                continue
            
            # Jaccard similarity
            intersection = len(query_words.intersection(content_words))
            union = len(query_words.union(content_words))
            
            if union == 0:
                similarity = 0.0
            else:
                similarity = intersection / union
            
            if similarity > 0:
                results.append((episode, similarity))
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top n results
        return results[:n_results]
    
    def delete_episode(self, episode_id: str) -> bool:
        """Delete an episode by ID.
        
        Args:
            episode_id: ID of the episode to delete
            
        Returns:
            True if deleted, False otherwise
        """
        for i, episode in enumerate(self.episodes):
            if episode.id == episode_id:
                del self.episodes[i]
                logger.info(f"Deleted episode with ID: {episode_id}")
                return True
        
        logger.warning(f"Episode with ID '{episode_id}' not found for deletion")
        return False
    
    def clear(self) -> None:
        """Clear all episodes from the memory."""
        self.episodes = []
        logger.info(f"Cleared all episodes from episodic memory '{self.name}'")
    
    def get_recent_episodes(self, n: int = 5) -> List[Episode]:
        """Get the most recent episodes.
        
        Args:
            n: Number of episodes to get
            
        Returns:
            List of recent episodes
        """
        return self.episodes[-n:]
    
    def get_size(self) -> int:
        """Get the size of the episodic memory.
        
        Returns:
            Size of the episodic memory
        """
        return len(self.episodes)
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the episodic memory.
        
        Returns:
            Information about the episodic memory
        """
        return {
            "name": self.name,
            "max_size": self.max_size,
            "current_size": len(self.episodes)
        }
