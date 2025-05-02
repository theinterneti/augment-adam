"""
REST API client for the memory service.

This module provides a client for interacting with the memory service via REST API.
"""

import logging
import aiohttp
from typing import Any, Dict, List, Optional, Union

from augment_adam.memory.client.memory_client import MemoryClient

# Set up logging
logger = logging.getLogger(__name__)


class MemoryRESTClient(MemoryClient):
    """REST API client for the memory service.

    This class provides a client for interacting with the memory service via REST API.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the client.

        Args:
            base_url: Base URL of the memory service API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to the memory service.

        Returns:
            True if the connection was successful, False otherwise
        """
        if self._connected:
            return True

        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Test connection by making a simple request
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    logger.info(f"Connected to memory service at {self.base_url}")
                    self._connected = True
                    return True
                else:
                    logger.error(f"Failed to connect to memory service: {response.status}")
                    return False
        except Exception as e:
            logger.exception(f"Error connecting to memory service: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from the memory service."""
        if self.session:
            await self.session.close()
            self.session = None
        self._connected = False
        logger.info("Disconnected from memory service")

    async def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the memory service.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data

        Raises:
            Exception: If the request fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Request failed: {response.status} - {error_text}")
                    raise Exception(f"Request failed: {response.status} - {error_text}")
                
                return await response.json()
        except Exception as e:
            logger.exception(f"Error making request: {e}")
            raise

    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a new memory.

        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory

        Returns:
            The created memory with ID
        """
        data = {"text": text}
        if metadata:
            data["metadata"] = metadata

        return await self._request("POST", "/memories", data)

    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a memory by ID.

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            The memory with the specified ID
        """
        return await self._request("GET", f"/memories/{memory_id}")

    async def list_memories(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all memories.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip

        Returns:
            List of memories
        """
        return await self._request("GET", f"/memories?limit={limit}&offset={offset}")

    async def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories by query.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of memories matching the query
        """
        return await self._request("GET", f"/memories/search?query={query}&limit={limit}")

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
        data = {}
        if text is not None:
            data["text"] = text
        if metadata is not None:
            data["metadata"] = metadata

        return await self._request("PUT", f"/memories/{memory_id}", data)

    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            Success message
        """
        return await self._request("DELETE", f"/memories/{memory_id}")
