#!/usr/bin/env python3
"""
Run the MCP client for Augment Adam.

This script connects to an MCP server and allows interacting with it from the command line.
"""

import os
import sys
import logging
import argparse
import asyncio
import json

from augment_adam.server.mcp_client import MCPClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run the MCP client for Augment Adam")
    parser.add_argument("--url", default="http://localhost:8811/mcp", help="URL of the MCP server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--call", help="Call a tool")
    parser.add_argument("--params", help="Parameters for the tool call (JSON)")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Connect to the MCP server
    async with MCPClient(args.url) as client:
        # Check connection
        if not await client.connect():
            logger.error(f"Failed to connect to MCP server at {args.url}")
            sys.exit(1)
        
        logger.info(f"Connected to MCP server at {args.url}")
        
        # List tools
        if args.list_tools:
            tools = await client.get_tools()
            print(f"Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
                if tool['parameters']:
                    print(f"    Parameters:")
                    for param_name, param_info in tool['parameters'].items():
                        print(f"      - {param_name}: {param_info.get('description', '')}")
        
        # Call a tool
        if args.call:
            if not args.params:
                logger.error("Parameters are required for tool calls")
                sys.exit(1)
            
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                logger.error("Invalid JSON parameters")
                sys.exit(1)
            
            try:
                result = await client.call_tool(args.call, params)
                print(f"Result: {json.dumps(result, indent=2)}")
            except Exception as e:
                logger.error(f"Error calling tool: {e}")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
