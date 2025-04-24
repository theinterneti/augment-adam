"""Base memory system for Augment Adam.

This module contains the base memory system interface for Augment Adam.
All memory systems should inherit from the BaseMemory class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseMemory(ABC):
    """Base memory system interface.

    This class defines the interface for memory systems in Augment Adam.
    All memory systems should inherit from this class and implement its methods.
    """

    @abstractmethod
    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add text to memory.

        Args:
            text: The text to add to memory.
            metadata: Additional metadata for the memory entry.
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant entries.

        Args:
            query: The search query.
            limit: The maximum number of results to return.

        Returns:
            A list of memory entries matching the query.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory entries."""
        pass
