"""Context Memory Implementation.

This module provides the context memory for agents.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)


class ContextMemory:
    """Context Memory.

    This class manages the context memory for agents.

    Attributes:
        name: Name of the context memory
        max_size: Maximum size of the context memory
        items: Items in the context memory
    """

    def __init__(self, name: str, max_size: int = 1000):
        """Initialize the Context Memory.

        Args:
            name: Name of the context memory
            max_size: Maximum size of the context memory
        """
        self.name = name
        self.max_size = max_size
        self.items = []

        logger.info(f"Initialized Context Memory '{name}' with max size {max_size}")

    def add(self, item: Any) -> None:
        """Add an item to the context memory.

        Args:
            item: Item to add
        """
        self.items.append(item)

        # Trim if necessary
        if len(self.items) > self.max_size:
            self.items = self.items[-self.max_size :]

    def get(self, n: Optional[int] = None) -> List[Any]:
        """Get items from the context memory.

        Args:
            n: Number of items to get (None for all)

        Returns:
            List of items
        """
        if n is None:
            return self.items
        else:
            return self.items[-n:]

    def clear(self) -> None:
        """Clear the context memory."""
        self.items = []

    def get_size(self) -> int:
        """Get the size of the context memory.

        Returns:
            Size of the context memory
        """
        return len(self.items)

    def get_info(self) -> Dict[str, Any]:
        """Get information about the context memory.

        Returns:
            Information about the context memory
        """
        return {
            "name": self.name,
            "max_size": self.max_size,
            "current_size": len(self.items),
        }
