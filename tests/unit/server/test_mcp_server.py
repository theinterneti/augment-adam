"""
Unit tests for the MCP server implementation.

This module contains tests for the MCP server functionality, including
tool registration, tool calling, and error handling.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from augment_adam.server.mcp_server import create_mcp_server, MCPServer, MCPTool, MCPToolRequest, MCPToolResponse

@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    return FastAPI()

@pytest.fixture
def mcp_server(app):
    """Create an MCP server for testing."""
    return create_mcp_server(app)

@pytest.fixture
def client(app, mcp_server):
    """Create a test client for the FastAPI app."""
    # Register a test tool
    async def echo_tool(message: str):
        return {"message": message}

    mcp_server.register_tool(
        name="echo",
        func=echo_tool,
        description="Echo a message back",
        parameters={"message": {"type": "string", "description": "Message to echo"}},
        returns={"message": {"type": "string", "description": "Echoed message"}}
    )

    return TestClient(app)

class TestMCPServer:
    """Tests for the MCP server."""

    def test_create_mcp_server(self, app):
        """Test creating an MCP server."""
        server = create_mcp_server(app)
        assert isinstance(server, MCPServer)
        assert server.app == app
        assert server.router.prefix == "/mcp"
        assert server.tools == {}
        assert server.tool_descriptions == {}

    def test_register_tool(self, mcp_server):
        """Test registering a tool with the MCP server."""
        # Define a simple tool function
        async def echo(message: str):
            return {"message": message}

        # Register the tool
        mcp_server.register_tool(
            name="echo",
            func=echo,
            description="Echo a message back",
            parameters={"message": {"type": "string", "description": "Message to echo"}},
            returns={"message": {"type": "string", "description": "Echoed message"}}
        )

        # Check that the tool was registered
        assert "echo" in mcp_server.tools
        assert mcp_server.tools["echo"] == echo
        assert "echo" in mcp_server.tool_descriptions
        tool = mcp_server.tool_descriptions["echo"]
        assert tool.name == "echo"
        assert tool.description == "Echo a message back"
        assert tool.parameters == {"message": {"type": "string", "description": "Message to echo"}}
        assert tool.returns == {"message": {"type": "string", "description": "Echoed message"}}

    def test_get_tools(self, client):
        """Test getting the list of available tools."""
        response = client.get("/mcp/tools")
        assert response.status_code == 200

        tools = response.json()
        assert len(tools) == 1
        assert tools[0]["name"] == "echo"
        assert tools[0]["description"] == "Echo a message back"
        assert "message" in tools[0]["parameters"]

    def test_call_tool(self, client):
        """Test calling a tool."""
        response = client.post(
            "/mcp/call",
            json={"name": "echo", "parameters": {"message": "Hello, world!"}}
        )
        assert response.status_code == 200

        result = response.json()
        assert "result" in result
        assert result["result"]["message"] == "Hello, world!"

    def test_call_nonexistent_tool(self, client):
        """Test calling a tool that doesn't exist."""
        response = client.post(
            "/mcp/call",
            json={"name": "nonexistent", "parameters": {}}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_call_tool_with_error(self, client, mcp_server):
        """Test calling a tool that raises an error."""
        # Register a tool that raises an error
        async def error_tool():
            raise ValueError("Test error")

        mcp_server.register_tool(
            name="error_tool",
            func=error_tool,
            description="A tool that raises an error",
            parameters={},
            returns={}
        )

        # Call the tool
        response = client.post(
            "/mcp/call",
            json={"name": "error_tool", "parameters": {}}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is None
        assert "Test error" in result["error"]

    def test_check_connection(self, client):
        """Test the connection check endpoint."""
        response = client.get("/mcp/connection")
        assert response.status_code == 200
        assert response.json()["status"] == "connected"
