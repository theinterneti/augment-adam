"""
Unit tests for the MCP Context Engine.

This module contains tests for the MCP Context Engine functionality, including
tool registration and context retrieval.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, call
from fastapi import FastAPI
from fastapi.testclient import TestClient

from augment_adam.context_engine.mcp import create_mcp_context_engine, MCPContextEngine

@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    return FastAPI()

@pytest.fixture
def mcp_context_engine(app):
    """Create an MCP Context Engine for testing."""
    with patch("augment_adam.context_engine.mcp.create_mcp_server") as mock_create_mcp_server:
        mock_mcp_server = MagicMock()
        mock_create_mcp_server.return_value = mock_mcp_server
        engine = create_mcp_context_engine(app, api_key="test-api-key")
        return engine

@pytest.fixture
def client(app, mcp_context_engine):
    """Create a test client for the FastAPI app."""
    return TestClient(app)

class TestMCPContextEngine:
    """Tests for the MCP Context Engine."""

    def test_create_mcp_context_engine(self, app):
        """Test creating an MCP Context Engine."""
        with patch("augment_adam.context_engine.mcp.create_mcp_server") as mock_create_mcp_server:
            mock_mcp_server = MagicMock()
            mock_create_mcp_server.return_value = mock_mcp_server
            engine = create_mcp_context_engine(app, api_key="test-api-key")

            assert isinstance(engine, MCPContextEngine)
            assert engine.app == app
            assert engine.api_key == "test-api-key"
            assert engine.router.prefix == "/api"
            assert engine.mcp_server == mock_mcp_server

            # Check that the MCP server was created and mounted
            mock_create_mcp_server.assert_called_once_with(app)

            # Check that tools were registered
            assert mock_mcp_server.register_tool.call_count > 0

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/health", headers={"X-API-Key": "test-api-key"})
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_health_check_invalid_api_key(self, client):
        """Test the health check endpoint with an invalid API key."""
        response = client.get("/api/health", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 401

    def test_store_vector(self, client):
        """Test the store_vector endpoint."""
        response = client.post(
            "/api/vector/store",
            json={
                "text": "def hello_world():\n    print('Hello, world!')",
                "metadata": {
                    "file_path": "test.py",
                    "language": "python"
                },
                "tier": "hot"
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200

        result = response.json()
        assert "vector_id" in result
        assert result["status"] == "success"

    def test_search_vectors(self, client):
        """Test the search_vectors endpoint."""
        response = client.post(
            "/api/vector/search",
            json={
                "query": "function that prints hello world",
                "k": 10,
                "include_metadata": True
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200

        result = response.json()
        assert "results" in result
        assert "query_time_ms" in result
        assert "total_results" in result

    def test_index_code(self, client):
        """Test the index_code endpoint."""
        response = client.post(
            "/api/code/index",
            json={
                "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
                "file_path": "factorial.py",
                "language": "python",
                "tier": "hot"
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200

        result = response.json()
        assert "vector_id" in result
        assert result["status"] == "success"

    def test_create_relationship(self, client):
        """Test the create_relationship endpoint."""
        response = client.post(
            "/api/graph/relationship",
            json={
                "from_id": "vec_123",
                "to_id": "vec_456",
                "relationship_type": "RELATED_TO",
                "properties": {
                    "weight": 0.8
                }
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["status"] == "success"

    def test_get_related_vectors(self, client):
        """Test the get_related_vectors endpoint."""
        response = client.post(
            "/api/graph/related",
            json={
                "vector_id": "vec_123",
                "relationship_type": "RELATED_TO",
                "max_depth": 1
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200

        result = response.json()
        assert "vectors" in result
        assert "total" in result

    def test_mcp_tools(self, client):
        """Test the MCP tools endpoint."""
        response = client.get("/mcp/tools")
        assert response.status_code == 200

        tools = response.json()
        assert len(tools) == 5

        tool_names = [tool["name"] for tool in tools]
        assert "vector_store" in tool_names
        assert "vector_search" in tool_names
        assert "code_index" in tool_names
        assert "create_relationship" in tool_names
        assert "get_related_vectors" in tool_names

    def test_mcp_call_vector_store(self, client):
        """Test calling the vector_store tool via MCP."""
        response = client.post(
            "/mcp/call",
            json={
                "name": "vector_store",
                "parameters": {
                    "text": "def hello_world():\n    print('Hello, world!')",
                    "metadata": {
                        "file_path": "test.py",
                        "language": "python"
                    },
                    "tier": "hot"
                }
            }
        )
        assert response.status_code == 200

        result = response.json()
        assert "result" in result
        assert "vector_id" in result["result"]
        assert result["result"]["status"] == "success"

    def test_mcp_call_vector_search(self, client):
        """Test calling the vector_search tool via MCP."""
        response = client.post(
            "/mcp/call",
            json={
                "name": "vector_search",
                "parameters": {
                    "query": "function that prints hello world",
                    "k": 10,
                    "include_metadata": True
                }
            }
        )
        assert response.status_code == 200

        result = response.json()
        assert "result" in result
        assert "results" in result["result"]
        assert "query_time_ms" in result["result"]
        assert "total_results" in result["result"]

    def test_mcp_tools_registration(self, app):
        """Test that MCP tools are registered."""
        with patch("augment_adam.context_engine.mcp.create_mcp_server") as mock_create_mcp_server:
            mock_mcp_server = MagicMock()
            mock_create_mcp_server.return_value = mock_mcp_server
            engine = create_mcp_context_engine(app, api_key="test-api-key")

            # Check that tools were registered
            tool_calls = [call[0][0] for call in mock_mcp_server.register_tool.call_args_list]
            assert "vector_search" in tool_calls
            assert "file_search" in tool_calls
            assert "symbol_search" in tool_calls
            assert "echo" in tool_calls
