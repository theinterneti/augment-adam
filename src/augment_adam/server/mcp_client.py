"""
MCP Client implementation for Augment Adam.

This module provides a client for interacting with MCP servers, including
the Augment Adam MCP server and VS Code's MCP server.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client implementation for Augment Adam."""

    def __init__(self, base_url: str):
        """Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url.rstrip("/")
        self.session = None
        self.tools = []
    
    async def __aenter__(self):
        """Enter the async context manager."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def connect(self) -> bool:
        """Connect to the MCP server.
        
        Returns:
            True if the connection was successful, False otherwise
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(f"{self.base_url}/connection") as response:
                if response.status == 200:
                    logger.info(f"Connected to MCP server at {self.base_url}")
                    return True
                else:
                    logger.error(f"Failed to connect to MCP server: {response.status}")
                    return False
        except Exception as e:
            logger.exception(f"Error connecting to MCP server: {e}")
            return False
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of available tools.
        
        Returns:
            List of tool descriptions
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(f"{self.base_url}/tools") as response:
                if response.status == 200:
                    self.tools = await response.json()
                    logger.info(f"Got {len(self.tools)} tools from MCP server")
                    return self.tools
                else:
                    logger.error(f"Failed to get tools from MCP server: {response.status}")
                    return []
        except Exception as e:
            logger.exception(f"Error getting tools from MCP server: {e}")
            return []
    
    async def call_tool(self, name: str, parameters: Dict[str, Any] = None) -> Any:
        """Call a tool on the MCP server.
        
        Args:
            name: Name of the tool to call
            parameters: Parameters for the tool call
            
        Returns:
            Result of the tool call
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        if parameters is None:
            parameters = {}
        
        try:
            payload = {
                "name": name,
                "parameters": parameters
            }
            
            async with self.session.post(f"{self.base_url}/call", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if "error" in result and result["error"]:
                        logger.error(f"Tool '{name}' returned an error: {result['error']}")
                        raise Exception(result["error"])
                    
                    logger.info(f"Tool '{name}' called successfully")
                    return result["result"]
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to call tool '{name}': {response.status} - {error_text}")
                    raise Exception(f"Failed to call tool '{name}': {response.status} - {error_text}")
        except Exception as e:
            logger.exception(f"Error calling tool '{name}': {e}")
            raise
