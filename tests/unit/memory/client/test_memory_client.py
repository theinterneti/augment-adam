"""
Unit tests for the memory client.

This module contains unit tests for the memory client.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.client import MemoryClient, ClientType
from augment_adam.memory.client.rest_client import MemoryRESTClient
from augment_adam.memory.client.mcp_client import MemoryMCPClient


class TestMemoryClient:
    """Tests for the Memory Client."""

    def test_create_rest_client(self):
        """Test creating a REST client."""
        with patch("augment_adam.memory.client.memory_client.MemoryRESTClient") as mock_rest_client:
            client = MemoryClient.create(ClientType.REST, "http://localhost:8000")
            mock_rest_client.assert_called_once_with("http://localhost:8000")
            assert isinstance(client, MemoryRESTClient)

    def test_create_mcp_client(self):
        """Test creating an MCP client."""
        with patch("importlib.util.find_spec", return_value=True), \
             patch("augment_adam.memory.client.memory_client.MemoryMCPClient") as mock_mcp_client:
            client = MemoryClient.create(ClientType.MCP, "http://localhost:8001")
            mock_mcp_client.assert_called_once_with("http://localhost:8001")
            assert isinstance(client, MemoryMCPClient)

    def test_create_mcp_client_missing_deps(self):
        """Test creating an MCP client with missing dependencies."""
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError):
                MemoryClient.create(ClientType.MCP, "http://localhost:8001")

    def test_create_invalid_client_type(self):
        """Test creating a client with an invalid type."""
        with pytest.raises(ValueError):
            MemoryClient.create("invalid_type", "http://localhost:8000")


class TestMemoryRESTClient:
    """Tests for the Memory REST Client."""

    @pytest.fixture
    def rest_client(self):
        """Create a REST client for testing."""
        return MemoryRESTClient("http://localhost:8000", "test_api_key")

    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing."""
        mock = AsyncMock()
        mock.__aenter__.return_value = mock
        mock.status = 200
        mock.json.return_value = {"success": True}
        return mock

    @pytest.mark.asyncio
    async def test_connect(self, rest_client, mock_session):
        """Test connecting to the memory service."""
        with patch("aiohttp.ClientSession.get", return_value=mock_session):
            result = await rest_client.connect()
            assert result is True
            assert rest_client._connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, rest_client, mock_session):
        """Test connecting to the memory service with a failure."""
        mock_session.status = 500
        with patch("aiohttp.ClientSession.get", return_value=mock_session):
            result = await rest_client.connect()
            assert result is False
            assert rest_client._connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, rest_client):
        """Test disconnecting from the memory service."""
        rest_client.session = AsyncMock()
        await rest_client.disconnect()
        rest_client.session.close.assert_called_once()
        assert rest_client._connected is False

    @pytest.mark.asyncio
    async def test_add_memory(self, rest_client, mock_session):
        """Test adding a memory."""
        mock_session.json.return_value = {"memory": {"id": "mem_123", "text": "test"}}
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            result = await rest_client.add_memory("test", {"key": "value"})
            assert result == {"memory": {"id": "mem_123", "text": "test"}}

    @pytest.mark.asyncio
    async def test_get_memory(self, rest_client, mock_session):
        """Test getting a memory."""
        mock_session.json.return_value = {"memory": {"id": "mem_123", "text": "test"}}
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            result = await rest_client.get_memory("mem_123")
            assert result == {"memory": {"id": "mem_123", "text": "test"}}

    @pytest.mark.asyncio
    async def test_list_memories(self, rest_client, mock_session):
        """Test listing memories."""
        mock_session.json.return_value = {"memories": [{"id": "mem_123", "text": "test"}]}
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            result = await rest_client.list_memories(limit=10, offset=0)
            assert result == {"memories": [{"id": "mem_123", "text": "test"}]}

    @pytest.mark.asyncio
    async def test_search_memories(self, rest_client, mock_session):
        """Test searching memories."""
        mock_session.json.return_value = {"results": [{"id": "mem_123", "text": "test"}]}
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            result = await rest_client.search_memories("test", limit=10)
            assert result == {"results": [{"id": "mem_123", "text": "test"}]}

    @pytest.mark.asyncio
    async def test_update_memory(self, rest_client, mock_session):
        """Test updating a memory."""
        mock_session.json.return_value = {"memory": {"id": "mem_123", "text": "updated"}}
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            result = await rest_client.update_memory("mem_123", "updated", {"key": "value"})
            assert result == {"memory": {"id": "mem_123", "text": "updated"}}

    @pytest.mark.asyncio
    async def test_delete_memory(self, rest_client, mock_session):
        """Test deleting a memory."""
        mock_session.json.return_value = {"success": True}
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            result = await rest_client.delete_memory("mem_123")
            assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_request_error(self, rest_client, mock_session):
        """Test handling a request error."""
        mock_session.status = 500
        mock_session.text = AsyncMock(return_value="Internal Server Error")
        with patch("aiohttp.ClientSession.request", return_value=mock_session):
            rest_client.session = AsyncMock()
            with pytest.raises(Exception):
                await rest_client.add_memory("test")


class TestMemoryMCPClient:
    """Tests for the Memory MCP Client."""

    @pytest.fixture
    def mcp_client(self):
        """Create an MCP client for testing."""
        return MemoryMCPClient("http://localhost:8001")

    @pytest.fixture
    def mock_mcp_client(self):
        """Create a mock MCP client for testing."""
        mock = AsyncMock()
        mock.connect = AsyncMock(return_value=None)
        mock.disconnect = AsyncMock(return_value=None)
        mock.list_tools = AsyncMock(return_value=[{"name": "add_memory"}])
        mock.call = AsyncMock(return_value={"memory": {"id": "mem_123", "text": "test"}})
        return mock

    @pytest.mark.asyncio
    async def test_connect(self, mcp_client, mock_mcp_client):
        """Test connecting to the MCP server."""
        with patch("mcp.client.Client", return_value=mock_mcp_client), \
             patch("mcp.client.transports.FastMCPTransport"):
            result = await mcp_client.connect()
            assert result is True
            assert mcp_client._connected is True
            mock_mcp_client.connect.assert_called_once()
            mock_mcp_client.list_tools.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(self, mcp_client, mock_mcp_client):
        """Test disconnecting from the MCP server."""
        mcp_client.client = mock_mcp_client
        await mcp_client.disconnect()
        mock_mcp_client.disconnect.assert_called_once()
        assert mcp_client._connected is False

    @pytest.mark.asyncio
    async def test_add_memory(self, mcp_client, mock_mcp_client):
        """Test adding a memory."""
        mcp_client.client = mock_mcp_client
        mcp_client._connected = True
        result = await mcp_client.add_memory("test", {"key": "value"})
        assert result == {"memory": {"id": "mem_123", "text": "test"}}
        mock_mcp_client.call.assert_called_once_with(
            "add_memory", text="test", metadata={"key": "value"}
        )

    @pytest.mark.asyncio
    async def test_get_memory(self, mcp_client, mock_mcp_client):
        """Test getting a memory."""
        mcp_client.client = mock_mcp_client
        mcp_client._connected = True
        result = await mcp_client.get_memory("mem_123")
        assert result == {"memory": {"id": "mem_123", "text": "test"}}
        mock_mcp_client.call.assert_called_once_with(
            "get_memory", memory_id="mem_123"
        )

    @pytest.mark.asyncio
    async def test_list_memories(self, mcp_client, mock_mcp_client):
        """Test listing memories."""
        mcp_client.client = mock_mcp_client
        mcp_client._connected = True
        result = await mcp_client.list_memories(limit=10, offset=0)
        assert result == {"memory": {"id": "mem_123", "text": "test"}}
        mock_mcp_client.call.assert_called_once_with(
            "list_memories", limit=10, offset=0
        )

    @pytest.mark.asyncio
    async def test_search_memories(self, mcp_client, mock_mcp_client):
        """Test searching memories."""
        mcp_client.client = mock_mcp_client
        mcp_client._connected = True
        result = await mcp_client.search_memories("test", limit=10)
        assert result == {"memory": {"id": "mem_123", "text": "test"}}
        mock_mcp_client.call.assert_called_once_with(
            "search_memories", query="test", limit=10
        )

    @pytest.mark.asyncio
    async def test_update_memory(self, mcp_client, mock_mcp_client):
        """Test updating a memory."""
        mcp_client.client = mock_mcp_client
        mcp_client._connected = True
        result = await mcp_client.update_memory("mem_123", "updated", {"key": "value"})
        assert result == {"memory": {"id": "mem_123", "text": "test"}}
        mock_mcp_client.call.assert_called_once_with(
            "update_memory", memory_id="mem_123", text="updated", metadata={"key": "value"}
        )

    @pytest.mark.asyncio
    async def test_delete_memory(self, mcp_client, mock_mcp_client):
        """Test deleting a memory."""
        mcp_client.client = mock_mcp_client
        mcp_client._connected = True
        result = await mcp_client.delete_memory("mem_123")
        assert result == {"memory": {"id": "mem_123", "text": "test"}}
        mock_mcp_client.call.assert_called_once_with(
            "delete_memory", memory_id="mem_123"
        )

    @pytest.mark.asyncio
    async def test_call_tool_not_connected(self, mcp_client):
        """Test calling a tool when not connected."""
        with pytest.raises(Exception):
            await mcp_client._call_tool("add_memory", text="test")
