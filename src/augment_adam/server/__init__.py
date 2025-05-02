"""
Server module for Augment Adam.

This module provides server implementations for Augment Adam, including
the MCP server for VS Code integration.
"""

from augment_adam.server.mcp_server import MCPServer, create_mcp_server
from augment_adam.server.mcp_client import MCPClient

__all__ = ["MCPServer", "create_mcp_server", "MCPClient"]