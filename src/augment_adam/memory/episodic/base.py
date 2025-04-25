"""
Base classes for episodic memory system.

This module provides the base classes for the episodic memory system,
including the EpisodicMemory class, Episode class, and Event class.
"""

import uuid
import datetime
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType


@dataclass
class Event:
    """
    Event in an episodic memory.
    
    This class represents an event in an episodic memory, including its content,
    timestamp, and other attributes.
    
    Attributes:
        id: Unique identifier for the event.
        content: The content of the event.
        timestamp: When the event occurred.
        metadata: Additional metadata for the event.
        embedding: Vector embedding for the event (if applicable).
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dictionary representation of the event.
        """
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Create an event from a dictionary.
        
        Args:
            data: Dictionary representation of the event.
            
        Returns:
            Event.
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content"),
            timestamp=data.get("timestamp", datetime.datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


@dataclass
class Episode(MemoryItem):
    """
    Episode in an episodic memory.
    
    This class represents an episode in an episodic memory, including its events,
    metadata, and other attributes.
    
    Attributes:
        id: Unique identifier for the episode.
        content: The content of the episode.
        metadata: Additional metadata for the episode.
        created_at: When the episode was created.
        updated_at: When the episode was last updated.
        expires_at: When the episode expires (if applicable).
        importance: Importance score for the episode (0-1).
        embedding: Vector embedding for the episode (if applicable).
        events: List of events in the episode.
        start_time: When the episode started.
        end_time: When the episode ended.
    
    TODO(Issue #6): Add support for episode versioning
    TODO(Issue #6): Implement episode validation
    """
    
    events: List[Event] = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Initialize the episode with timestamps."""
        super().__post_init__()
        
        # Set start and end times based on events
        if self.events and not self.start_time:
            self.start_time = min(event.timestamp for event in self.events)
        
        if self.events and not self.end_time:
            self.end_time = max(event.timestamp for event in self.events)
    
    def add_event(self, event: Event) -> str:
        """
        Add an event to the episode.
        
        Args:
            event: The event to add.
            
        Returns:
            The ID of the added event.
        """
        self.events.append(event)
        
        # Update start and end times
        if not self.start_time or event.timestamp < self.start_time:
            self.start_time = event.timestamp
        
        if not self.end_time or event.timestamp > self.end_time:
            self.end_time = event.timestamp
        
        # Update the episode's updated_at timestamp
        self.updated_at = datetime.datetime.now().isoformat()
        
        return event.id
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """
        Get an event from the episode by ID.
        
        Args:
            event_id: The ID of the event to get.
            
        Returns:
            The event, or None if it doesn't exist.
        """
        for event in self.events:
            if event.id == event_id:
                return event
        
        return None
    
    def remove_event(self, event_id: str) -> bool:
        """
        Remove an event from the episode.
        
        Args:
            event_id: The ID of the event to remove.
            
        Returns:
            True if the event was removed, False otherwise.
        """
        for i, event in enumerate(self.events):
            if event.id == event_id:
                del self.events[i]
                
                # Update start and end times
                if self.events:
                    self.start_time = min(event.timestamp for event in self.events)
                    self.end_time = max(event.timestamp for event in self.events)
                else:
                    self.start_time = None
                    self.end_time = None
                
                # Update the episode's updated_at timestamp
                self.updated_at = datetime.datetime.now().isoformat()
                
                return True
        
        return False
    
    def get_events_in_range(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Event]:
        """
        Get events in a time range.
        
        Args:
            start_time: The start of the time range (inclusive).
            end_time: The end of the time range (inclusive).
            
        Returns:
            List of events in the time range.
        """
        events = []
        
        for event in self.events:
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            events.append(event)
        
        return events
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the episode to a dictionary.
        
        Returns:
            Dictionary representation of the episode.
        """
        data = super().to_dict()
        data["events"] = [event.to_dict() for event in self.events]
        data["start_time"] = self.start_time
        data["end_time"] = self.end_time
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """
        Create an episode from a dictionary.
        
        Args:
            data: Dictionary representation of the episode.
            
        Returns:
            Episode.
        """
        episode = super().from_dict(data)
        
        # Add events
        episode.events = [Event.from_dict(event_data) for event_data in data.get("events", [])]
        episode.start_time = data.get("start_time")
        episode.end_time = data.get("end_time")
        
        return episode


T = TypeVar('T', bound=Episode)


@tag("memory.episodic")
class EpisodicMemory(Memory[T]):
    """
    Episodic memory system.
    
    This class implements an episodic memory system for storing and retrieving
    temporal sequences of events.
    
    Attributes:
        name: The name of the memory system.
        items: Dictionary of episodes in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the episodic memory system.
        
        Args:
            name: The name of the memory system.
        """
        super().__init__(name, MemoryType.EPISODIC)
    
    def add_event(self, episode_id: str, event: Event) -> Optional[str]:
        """
        Add an event to an episode.
        
        Args:
            episode_id: The ID of the episode.
            event: The event to add.
            
        Returns:
            The ID of the added event, or None if the episode doesn't exist.
        """
        episode = self.get(episode_id)
        if episode is None:
            return None
        
        return episode.add_event(event)
    
    def get_event(self, episode_id: str, event_id: str) -> Optional[Event]:
        """
        Get an event from an episode.
        
        Args:
            episode_id: The ID of the episode.
            event_id: The ID of the event.
            
        Returns:
            The event, or None if the episode or event doesn't exist.
        """
        episode = self.get(episode_id)
        if episode is None:
            return None
        
        return episode.get_event(event_id)
    
    def remove_event(self, episode_id: str, event_id: str) -> bool:
        """
        Remove an event from an episode.
        
        Args:
            episode_id: The ID of the episode.
            event_id: The ID of the event.
            
        Returns:
            True if the event was removed, False otherwise.
        """
        episode = self.get(episode_id)
        if episode is None:
            return False
        
        return episode.remove_event(event_id)
    
    def get_events_in_range(self, episode_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Event]:
        """
        Get events in a time range from an episode.
        
        Args:
            episode_id: The ID of the episode.
            start_time: The start of the time range (inclusive).
            end_time: The end of the time range (inclusive).
            
        Returns:
            List of events in the time range, or an empty list if the episode doesn't exist.
        """
        episode = self.get(episode_id)
        if episode is None:
            return []
        
        return episode.get_events_in_range(start_time, end_time)
    
    def get_episodes_in_range(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[T]:
        """
        Get episodes in a time range.
        
        Args:
            start_time: The start of the time range (inclusive).
            end_time: The end of the time range (inclusive).
            
        Returns:
            List of episodes in the time range.
        """
        episodes = []
        
        for episode in self.items.values():
            # If the episode has no start or end time, skip it
            if not episode.start_time or not episode.end_time:
                continue
            
            # If the episode ends before the start time, skip it
            if start_time and episode.end_time < start_time:
                continue
            
            # If the episode starts after the end time, skip it
            if end_time and episode.start_time > end_time:
                continue
            
            episodes.append(episode)
        
        return episodes
    
    def search(self, query: Any, limit: int = 10) -> List[T]:
        """
        Search for episodes in memory.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of episodes that match the query.
        """
        # If the query is a string, search for episodes with matching content
        if isinstance(query, str):
            results = []
            
            for episode in self.items.values():
                # Check if the episode content contains the query
                if episode.content and isinstance(episode.content, str) and query.lower() in episode.content.lower():
                    results.append(episode)
                    continue
                
                # Check if any event content contains the query
                for event in episode.events:
                    if event.content and isinstance(event.content, str) and query.lower() in event.content.lower():
                        results.append(episode)
                        break
            
            return results[:limit]
        
        # If the query is a dictionary with a time range, search for episodes in that range
        elif isinstance(query, dict) and ("start_time" in query or "end_time" in query):
            return self.get_episodes_in_range(query.get("start_time"), query.get("end_time"))[:limit]
        
        # Otherwise, use the default search
        return super().search(query, limit)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the episodic memory system to a dictionary.
        
        Returns:
            Dictionary representation of the episodic memory system.
        """
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpisodicMemory':
        """
        Create an episodic memory system from a dictionary.
        
        Args:
            data: Dictionary representation of the episodic memory system.
            
        Returns:
            Episodic memory system.
        """
        memory = cls(name=data.get("name", ""))
        memory.metadata = data.get("metadata", {})
        
        for item_data in data.get("items", {}).values():
            item = Episode.from_dict(item_data)
            memory.add(item)
        
        return memory
