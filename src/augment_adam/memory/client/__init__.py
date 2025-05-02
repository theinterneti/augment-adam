"""
Memory client package for Augment Adam.

This package provides client implementations for interacting with the memory service
via both REST API and MCP (Model Context Protocol).
"""

from augment_adam.memory.client.memory_client import MemoryClient, ClientType
from augment_adam.memory.client.rest_client import MemoryRESTClient
from augment_adam.memory.client.mcp_client import MemoryMCPClient
from augment_adam.memory.client.sync_client import SyncMemoryClient

__all__ = [
    "MemoryClient",
    "ClientType",
    "MemoryRESTClient",
    "MemoryMCPClient",
    "SyncMemoryClient",
]
