"""
Unit tests for the MCP client implementation.

This module contains tests for the MCP client functionality, including
connection, tool listing, and tool calling.
"""

import pytest
import pytest_asyncio
import json
import aiohttp
from unittest.mock import patch, MagicMock, AsyncMock

from augment_adam.server.mcp_client import MCPClient

@pytest_asyncio.fixture
async def mock_response():
    """Create a mock response for aiohttp."""
    mock = MagicMock()
    mock.status = 200
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None

    # Make json() a coroutine
    async def async_json():
        return mock.json.return_value

    mock.json = async_json
    return mock

@pytest.mark.asyncio
async def test_connect(mock_response):
    """Test the connect method."""
    mock_response.json.return_value = {"status": "connected"}

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with MCPClient("http://localhost:8080/mcp") as client:
            result = await client.connect()
            assert result is True

@pytest.mark.asyncio
async def test_connect_failure(mock_response):
    """Test the connect method with a failure."""
    mock_response.status = 500

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with MCPClient("http://localhost:8080/mcp") as client:
            result = await client.connect()
            assert result is False

@pytest.mark.asyncio
async def test_get_tools(mock_response):
    """Test the get_tools method."""
    mock_response.json.return_value = [
        {
            "name": "echo",
            "description": "Echo a message back",
            "parameters": {"message": {"type": "string", "description": "Message to echo"}},
            "returns": {"message": {"type": "string", "description": "Echoed message"}}
        }
    ]

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with MCPClient("http://localhost:8080/mcp") as client:
            tools = await client.get_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "echo"

@pytest.mark.asyncio
async def test_call_tool(mock_response):
    """Test the call_tool method."""
    mock_response.json.return_value = {"result": {"message": "Hello, world!"}}

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        async with MCPClient("http://localhost:8080/mcp") as client:
            result = await client.call_tool("echo", {"message": "Hello, world!"})
            assert result["message"] == "Hello, world!"

@pytest.mark.asyncio
async def test_call_tool_error(mock_response):
    """Test the call_tool method with an error."""
    mock_response.json.return_value = {"result": None, "error": "Tool not found"}

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        async with MCPClient("http://localhost:8080/mcp") as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool("nonexistent", {})
            assert "Tool not found" in str(excinfo.value)

@pytest.mark.asyncio
async def test_call_tool_http_error(mock_response):
    """Test the call_tool method with an HTTP error."""
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        async with MCPClient("http://localhost:8080/mcp") as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool("echo", {"message": "Hello, world!"})
            assert "500" in str(excinfo.value)

@pytest.mark.asyncio
async def test_connection_exception():
    """Test the connect method with a connection exception."""
    with patch("aiohttp.ClientSession.get", side_effect=aiohttp.ClientError("Connection error")):
        async with MCPClient("http://localhost:8080/mcp") as client:
            result = await client.connect()
            assert result is False

@pytest.mark.asyncio
async def test_call_tool_connection_exception():
    """Test the call_tool method with a connection exception."""
    with patch("aiohttp.ClientSession.post", side_effect=aiohttp.ClientError("Connection error")):
        async with MCPClient("http://localhost:8080/mcp") as client:
            with pytest.raises(Exception) as excinfo:
                await client.call_tool("echo", {"message": "Hello, world!"})
            assert "Connection error" in str(excinfo.value)
