#!/usr/bin/env python3
"""
Memory Client Demo

This script demonstrates how to use the memory client to interact with the memory service
via both REST API and MCP.
"""

import asyncio
import json
import logging
import argparse
import os
from typing import Optional

from augment_adam.memory.client import MemoryClient, ClientType

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_rest_demo(api_url: str, api_key: Optional[str] = None):
    """Run the REST API demo.
    
    Args:
        api_url: Base URL of the Memory Service API
        api_key: Optional API key for authentication
    """
    logger.info("=== REST API Client Demo ===")
    
    # Create client
    client = MemoryClient.create(ClientType.REST, api_url, api_key)
    
    try:
        # Connect to the API
        logger.info("Connecting to Memory Service API...")
        connected = await client.connect()
        if not connected:
            logger.error("Failed to connect to Memory Service API")
            return
        
        # Add a memory
        logger.info("Adding a memory via API...")
        result = await client.add_memory(
            text="This is a memory from the REST API client",
            metadata={"source": "rest_api_client", "importance": 0.9}
        )
        logger.info(f"Added memory: {json.dumps(result, indent=2)}")
        
        # Get the memory ID
        memory_id = result.get("memory", {}).get("id")
        if not memory_id:
            logger.error("Failed to get memory ID")
            return
        
        # Get the memory
        logger.info(f"Getting memory {memory_id}...")
        result = await client.get_memory(memory_id)
        logger.info(f"Memory: {json.dumps(result, indent=2)}")
        
        # Update the memory
        logger.info(f"Updating memory {memory_id}...")
        result = await client.update_memory(
            memory_id=memory_id,
            text="This is an updated memory from the REST API client",
            metadata={"source": "rest_api_client", "importance": 1.0}
        )
        logger.info(f"Updated memory: {json.dumps(result, indent=2)}")
        
        # List all memories
        logger.info("Listing all memories...")
        result = await client.list_memories(limit=10)
        logger.info(f"Memories: {json.dumps(result, indent=2)}")
        
        # Search memories
        logger.info("Searching memories...")
        result = await client.search_memories(query="REST API client")
        logger.info(f"Search results: {json.dumps(result, indent=2)}")
        
        # Delete the memory
        logger.info(f"Deleting memory {memory_id}...")
        result = await client.delete_memory(memory_id)
        logger.info(f"Delete result: {json.dumps(result, indent=2)}")
        
        # List all memories again
        logger.info("Listing all memories after deletion...")
        result = await client.list_memories(limit=10)
        logger.info(f"Memories: {json.dumps(result, indent=2)}")
    
    finally:
        # Disconnect from the API
        logger.info("Disconnecting from Memory Service API...")
        await client.disconnect()


async def run_mcp_demo(mcp_url: str):
    """Run the MCP demo.
    
    Args:
        mcp_url: URL of the MCP server
    """
    logger.info("=== MCP Client Demo ===")
    
    # Create client
    client = MemoryClient.create(ClientType.MCP, mcp_url)
    
    try:
        # Connect to the MCP server
        logger.info("Connecting to MCP server...")
        connected = await client.connect()
        if not connected:
            logger.error("Failed to connect to MCP server")
            return
        
        # Add a memory
        logger.info("Adding a memory via MCP...")
        result = await client.add_memory(
            text="This is a memory from the MCP client",
            metadata={"source": "mcp_client", "importance": 0.9}
        )
        logger.info(f"Added memory: {json.dumps(result, indent=2)}")
        
        # Get the memory ID
        memory_id = result.get("memory", {}).get("id")
        if not memory_id:
            logger.error("Failed to get memory ID")
            return
        
        # Get the memory
        logger.info(f"Getting memory {memory_id}...")
        result = await client.get_memory(memory_id)
        logger.info(f"Memory: {json.dumps(result, indent=2)}")
        
        # Update the memory
        logger.info(f"Updating memory {memory_id}...")
        result = await client.update_memory(
            memory_id=memory_id,
            text="This is an updated memory from the MCP client",
            metadata={"source": "mcp_client", "importance": 1.0}
        )
        logger.info(f"Updated memory: {json.dumps(result, indent=2)}")
        
        # List all memories
        logger.info("Listing all memories...")
        result = await client.list_memories(limit=10)
        logger.info(f"Memories: {json.dumps(result, indent=2)}")
        
        # Search memories
        logger.info("Searching memories...")
        result = await client.search_memories(query="MCP client")
        logger.info(f"Search results: {json.dumps(result, indent=2)}")
        
        # Delete the memory
        logger.info(f"Deleting memory {memory_id}...")
        result = await client.delete_memory(memory_id)
        logger.info(f"Delete result: {json.dumps(result, indent=2)}")
        
        # List all memories again
        logger.info("Listing all memories after deletion...")
        result = await client.list_memories(limit=10)
        logger.info(f"Memories: {json.dumps(result, indent=2)}")
    
    finally:
        # Disconnect from the MCP server
        logger.info("Disconnecting from MCP server...")
        await client.disconnect()


async def run_demo_with_context_manager(api_url: str, mcp_url: str):
    """Run a demo using the context manager.
    
    Args:
        api_url: Base URL of the Memory Service API
        mcp_url: URL of the MCP server
    """
    logger.info("=== Context Manager Demo ===")
    
    # Using REST API client with context manager
    logger.info("Using REST API client with context manager...")
    async with MemoryClient.create(ClientType.REST, api_url) as client:
        result = await client.add_memory(
            text="Memory created with context manager (REST)",
            metadata={"source": "context_manager", "type": "rest"}
        )
        logger.info(f"Added memory: {json.dumps(result, indent=2)}")
    
    # Using MCP client with context manager
    logger.info("Using MCP client with context manager...")
    async with MemoryClient.create(ClientType.MCP, mcp_url) as client:
        result = await client.add_memory(
            text="Memory created with context manager (MCP)",
            metadata={"source": "context_manager", "type": "mcp"}
        )
        logger.info(f"Added memory: {json.dumps(result, indent=2)}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Memory Client Demo")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Base URL of the Memory Service API")
    parser.add_argument("--mcp-url", default="http://localhost:8001", help="URL of the MCP server")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--client", choices=["rest", "mcp", "both"], default="both", help="Client type to use")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get API key from environment if not provided
    api_key = args.api_key or os.environ.get("MEMORY_SERVICE_API_KEY")
    
    # Run the demos
    if args.client in ["rest", "both"]:
        await run_rest_demo(args.api_url, api_key)
    
    if args.client in ["mcp", "both"]:
        await run_mcp_demo(args.mcp_url)
    
    # Run the context manager demo
    await run_demo_with_context_manager(args.api_url, args.mcp_url)


if __name__ == "__main__":
    asyncio.run(main())
