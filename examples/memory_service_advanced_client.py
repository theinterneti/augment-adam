#!/usr/bin/env python3
"""
Memory Service Advanced Client Example

This script demonstrates how to use the Memory Service with both API and MCP interfaces.
"""

import os
import sys
import json
import argparse
import logging
import requests
import asyncio
from typing import Dict, List, Any, Optional, Union
from fastmcp import Client
from fastmcp.client.transports import FastMCPTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class MemoryServiceAPIClient:
    """Client for the Memory Service REST API."""
    
    def __init__(self, base_url: str):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the Memory Service API
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def add_memory(self, text: str, metadata: dict = None) -> dict:
        """Add a new memory.
        
        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory
        
        Returns:
            The created memory with ID
        """
        url = f"{self.base_url}/memories"
        data = {"text": text, "metadata": metadata or {}}
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_memory(self, memory_id: str) -> dict:
        """Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
        
        Returns:
            The memory with the specified ID
        """
        url = f"{self.base_url}/memories/{memory_id}"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def list_memories(self) -> dict:
        """List all memories.
        
        Returns:
            List of all memories
        """
        url = f"{self.base_url}/memories"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def delete_memory(self, memory_id: str) -> dict:
        """Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
        
        Returns:
            Success message
        """
        url = f"{self.base_url}/memories/{memory_id}"
        
        response = self.session.delete(url)
        response.raise_for_status()
        
        return response.json()

class MemoryServiceMCPClient:
    """Client for the Memory Service MCP interface."""
    
    def __init__(self, mcp_url: str):
        """Initialize the client.
        
        Args:
            mcp_url: URL of the MCP server
        """
        self.mcp_url = mcp_url
        self.client = None
    
    async def connect(self):
        """Connect to the MCP server."""
        self.client = Client(
            transport=FastMCPTransport(self.mcp_url),
            timeout=30
        )
        await self.client.connect()
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.client:
            await self.client.disconnect()
    
    async def add_memory(self, text: str, metadata: dict = None) -> dict:
        """Add a new memory.
        
        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory
        
        Returns:
            The created memory with ID
        """
        result = await self.client.call(
            "add_memory",
            text=text,
            metadata=metadata or {}
        )
        return result
    
    async def get_memory(self, memory_id: str) -> dict:
        """Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
        
        Returns:
            The memory with the specified ID
        """
        result = await self.client.call(
            "get_memory",
            memory_id=memory_id
        )
        return result
    
    async def list_memories(self) -> dict:
        """List all memories.
        
        Returns:
            List of all memories
        """
        result = await self.client.call("list_memories")
        return result
    
    async def delete_memory(self, memory_id: str) -> dict:
        """Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
        
        Returns:
            Success message
        """
        result = await self.client.call(
            "delete_memory",
            memory_id=memory_id
        )
        return result

async def run_mcp_demo(mcp_url: str):
    """Run the MCP demo.
    
    Args:
        mcp_url: URL of the MCP server
    """
    logger.info("=== MCP Client Demo ===")
    
    # Create client
    client = MemoryServiceMCPClient(mcp_url)
    
    try:
        # Connect to the MCP server
        logger.info("Connecting to MCP server...")
        await client.connect()
        
        # Add a memory
        logger.info("Adding a memory via MCP...")
        result = await client.add_memory(
            text="This is a memory from the MCP client",
            metadata={"source": "mcp_client", "importance": 0.9}
        )
        memory_id = result["memory"]["id"]
        logger.info(f"Added memory with ID: {memory_id}")
        
        # Get the memory
        logger.info(f"Getting memory with ID: {memory_id} via MCP...")
        result = await client.get_memory(memory_id)
        logger.info(f"Memory: {json.dumps(result, indent=2)}")
        
        # List all memories
        logger.info("Listing all memories via MCP...")
        result = await client.list_memories()
        logger.info(f"Memories: {json.dumps(result, indent=2)}")
        
        # Delete the memory
        logger.info(f"Deleting memory with ID: {memory_id} via MCP...")
        result = await client.delete_memory(memory_id)
        logger.info(f"Result: {json.dumps(result, indent=2)}")
        
        # List all memories again
        logger.info("Listing all memories after deletion via MCP...")
        result = await client.list_memories()
        logger.info(f"Memories: {json.dumps(result, indent=2)}")
    
    finally:
        # Disconnect from the MCP server
        logger.info("Disconnecting from MCP server...")
        await client.disconnect()

def run_api_demo(api_url: str):
    """Run the API demo.
    
    Args:
        api_url: Base URL of the Memory Service API
    """
    logger.info("=== API Client Demo ===")
    
    # Create client
    client = MemoryServiceAPIClient(api_url)
    
    # Add a memory
    logger.info("Adding a memory via API...")
    result = client.add_memory(
        text="This is a memory from the API client",
        metadata={"source": "api_client", "importance": 0.9}
    )
    memory_id = result["memory"]["id"]
    logger.info(f"Added memory with ID: {memory_id}")
    
    # Get the memory
    logger.info(f"Getting memory with ID: {memory_id} via API...")
    result = client.get_memory(memory_id)
    logger.info(f"Memory: {json.dumps(result, indent=2)}")
    
    # List all memories
    logger.info("Listing all memories via API...")
    result = client.list_memories()
    logger.info(f"Memories: {json.dumps(result, indent=2)}")
    
    # Delete the memory
    logger.info(f"Deleting memory with ID: {memory_id} via API...")
    result = client.delete_memory(memory_id)
    logger.info(f"Result: {json.dumps(result, indent=2)}")
    
    # List all memories again
    logger.info("Listing all memories after deletion via API...")
    result = client.list_memories()
    logger.info(f"Memories: {json.dumps(result, indent=2)}")

async def main_async():
    """Async main entry point."""
    parser = argparse.ArgumentParser(description="Memory Service Advanced Client Example")
    parser.add_argument("--api-url", default="http://localhost:8811", help="Base URL of the Memory Service API")
    parser.add_argument("--mcp-url", default="http://localhost:8811/mcp", help="URL of the MCP server")
    parser.add_argument("--api-only", action="store_true", help="Run only the API demo")
    parser.add_argument("--mcp-only", action="store_true", help="Run only the MCP demo")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the demos
    if args.api_only:
        run_api_demo(args.api_url)
    elif args.mcp_only:
        await run_mcp_demo(args.mcp_url)
    else:
        # Run both demos
        run_api_demo(args.api_url)
        await run_mcp_demo(args.mcp_url)

def main():
    """Main entry point."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
