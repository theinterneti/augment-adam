"""
Base memory client interface for Augment Adam.

This module defines the base interface for memory clients in Augment Adam.
All memory clients should inherit from the MemoryClient class.
"""

import logging
import importlib.util
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union, Type

# Set up logging
logger = logging.getLogger(__name__)


class ClientType(Enum):
    """Type of memory client."""
    REST = auto()
    MCP = auto()


class MemoryClient(ABC):
    """Base memory client interface.

    This class defines the interface for memory clients in Augment Adam.
    All memory clients should inherit from this class and implement its methods.
    """

    @abstractmethod
    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a new memory.

        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory

        Returns:
            The created memory with ID
        """
        pass

    @abstractmethod
    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a memory by ID.

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            The memory with the specified ID
        """
        pass

    @abstractmethod
    async def list_memories(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all memories.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip

        Returns:
            List of memories
        """
        pass

    @abstractmethod
    async def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories by query.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of memories matching the query
        """
        pass

    @abstractmethod
    async def update_memory(self, memory_id: str, text: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update a memory.

        Args:
            memory_id: ID of the memory to update
            text: New text content for the memory
            metadata: New metadata for the memory

        Returns:
            The updated memory
        """
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            Success message
        """
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the memory service.

        Returns:
            True if the connection was successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the memory service."""
        pass

    async def __aenter__(self):
        """Enter the async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        await self.disconnect()

    @staticmethod
    def create(client_type: ClientType, *args, **kwargs) -> 'MemoryClient':
        """Create a memory client of the specified type.

        Args:
            client_type: Type of client to create
            *args: Positional arguments to pass to the client constructor
            **kwargs: Keyword arguments to pass to the client constructor

        Returns:
            A memory client instance

        Raises:
            ImportError: If the required dependencies are not installed
            ValueError: If the client type is invalid
        """
        if client_type == ClientType.REST:
            from augment_adam.memory.client.rest_client import MemoryRESTClient
            return MemoryRESTClient(*args, **kwargs)
        elif client_type == ClientType.MCP:
            # Check if MCP dependencies are installed
            if not importlib.util.find_spec("mcp"):
                raise ImportError(
                    "MCP dependencies not installed. Please install 'mcp' package."
                )
            from augment_adam.memory.client.mcp_client import MemoryMCPClient
            return MemoryMCPClient(*args, **kwargs)
        else:
            raise ValueError(f"Invalid client type: {client_type}")
