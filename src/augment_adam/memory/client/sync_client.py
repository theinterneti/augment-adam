"""
Synchronous wrapper for the memory client.

This module provides a synchronous wrapper for the memory client.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from augment_adam.memory.client.memory_client import MemoryClient, ClientType

# Set up logging
logger = logging.getLogger(__name__)


class SyncMemoryClient:
    """Synchronous wrapper for the memory client.

    This class provides a synchronous interface to the memory client.
    """

    def __init__(self, client: MemoryClient):
        """Initialize the client.

        Args:
            client: The asynchronous memory client to wrap
        """
        self.client = client
        self._loop = None

    @staticmethod
    def create(client_type: ClientType, *args, **kwargs) -> 'SyncMemoryClient':
        """Create a synchronous memory client of the specified type.
        
        Args:
            client_type: Type of client to create
            *args: Positional arguments to pass to the client constructor
            **kwargs: Keyword arguments to pass to the client constructor
            
        Returns:
            A synchronous memory client instance
            
        Raises:
            ImportError: If the required dependencies are not installed
            ValueError: If the client type is invalid
        """
        async_client = MemoryClient.create(client_type, *args, **kwargs)
        return SyncMemoryClient(async_client)

    def _run_async(self, coro):
        """Run an asynchronous coroutine in a synchronous context.

        Args:
            coro: The coroutine to run

        Returns:
            The result of the coroutine
        """
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

        return self._loop.run_until_complete(coro)

    def connect(self) -> bool:
        """Connect to the memory service.

        Returns:
            True if the connection was successful, False otherwise
        """
        return self._run_async(self.client.connect())

    def disconnect(self) -> None:
        """Disconnect from the memory service."""
        self._run_async(self.client.disconnect())

    def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a new memory.

        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory

        Returns:
            The created memory with ID
        """
        return self._run_async(self.client.add_memory(text, metadata))

    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a memory by ID.

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            The memory with the specified ID
        """
        return self._run_async(self.client.get_memory(memory_id))

    def list_memories(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all memories.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip

        Returns:
            List of memories
        """
        return self._run_async(self.client.list_memories(limit, offset))

    def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories by query.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of memories matching the query
        """
        return self._run_async(self.client.search_memories(query, limit))

    def update_memory(self, memory_id: str, text: Optional[str] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update a memory.

        Args:
            memory_id: ID of the memory to update
            text: New text content for the memory
            metadata: New metadata for the memory

        Returns:
            The updated memory
        """
        return self._run_async(self.client.update_memory(memory_id, text, metadata))

    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            Success message
        """
        return self._run_async(self.client.delete_memory(memory_id))

    def __enter__(self):
        """Enter the context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        self.disconnect()
