"""
MCP client for the memory service.

This module provides a client for interacting with the memory service via MCP.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple

from augment_adam.memory.client.memory_client import MemoryClient

# Set up logging
logger = logging.getLogger(__name__)


class MemoryMCPClient(MemoryClient):
    """MCP client for the memory service.

    This class provides a client for interacting with the memory service via MCP.
    """

    def __init__(self, mcp_url: str):
        """Initialize the client.

        Args:
            mcp_url: URL of the MCP server
        """
        self.mcp_url = mcp_url
        self.client = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to the MCP server.

        Returns:
            True if the connection was successful, False otherwise
        """
        if self._connected:
            return True

        try:
            # Import here to avoid circular imports and allow the client to work
            # even if MCP dependencies are not installed
            from mcp.client import Client
            from mcp.client.transports import FastMCPTransport

            self.client = Client(
                transport=FastMCPTransport(self.mcp_url),
                timeout=30
            )
            await self.client.connect()
            
            # Test connection by listing tools
            tools = await self.client.list_tools()
            logger.info(f"Connected to MCP server at {self.mcp_url}")
            logger.debug(f"Available tools: {tools}")
            
            self._connected = True
            return True
        except ImportError:
            logger.error("MCP dependencies not installed. Please install 'mcp' package.")
            raise
        except Exception as e:
            logger.exception(f"Error connecting to MCP server: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.client:
            await self.client.disconnect()
            self.client = None
        self._connected = False
        logger.info("Disconnected from MCP server")

    async def _call_tool(self, name: str, **kwargs) -> Any:
        """Call a tool on the MCP server.

        Args:
            name: Name of the tool to call
            **kwargs: Tool parameters

        Returns:
            Tool result

        Raises:
            Exception: If the tool call fails
        """
        if not self.client:
            raise Exception("Not connected to MCP server")

        try:
            result = await self.client.call(name, **kwargs)
            return result
        except Exception as e:
            logger.exception(f"Error calling tool '{name}': {e}")
            raise

    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a new memory.

        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory

        Returns:
            The created memory with ID
        """
        return await self._call_tool(
            "add_memory",
            text=text,
            metadata=metadata or {}
        )

    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a memory by ID.

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            The memory with the specified ID
        """
        return await self._call_tool(
            "get_memory",
            memory_id=memory_id
        )

    async def list_memories(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all memories.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip

        Returns:
            List of memories
        """
        return await self._call_tool(
            "list_memories",
            limit=limit,
            offset=offset
        )

    async def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories by query.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of memories matching the query
        """
        return await self._call_tool(
            "search_memories",
            query=query,
            limit=limit
        )

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
        params = {"memory_id": memory_id}
        if text is not None:
            params["text"] = text
        if metadata is not None:
            params["metadata"] = metadata

        return await self._call_tool("update_memory", **params)

    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            Success message
        """
        return await self._call_tool(
            "delete_memory",
            memory_id=memory_id
        )
