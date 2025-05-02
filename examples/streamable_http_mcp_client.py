#!/usr/bin/env python3
"""
Streamable HTTP Transport Client Example for MCP

This script demonstrates how to connect to an MCP server using the new
Streamable HTTP transport protocol.

Based on the Cloudflare blog post:
https://blog.cloudflare.com/streamable-http-mcp-servers-python/
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required libraries
try:
    from mcp import ClientSession, types
    from mcp.client.http import http_client
except ImportError:
    print("This example requires the MCP Python SDK.")
    print("Install with: pip install mcp[cli]")
    sys.exit(1)

async def main():
    """Run the MCP client example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Streamable HTTP Client Example")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000/mcp",
        help="URL of the MCP server's streamable HTTP endpoint (default: http://localhost:8000/mcp)"
    )
    parser.add_argument(
        "--weight", 
        type=float, 
        default=70.0,
        help="Weight in kg for BMI calculation (default: 70.0)"
    )
    parser.add_argument(
        "--height", 
        type=float, 
        default=1.75,
        help="Height in meters for BMI calculation (default: 1.75)"
    )
    parser.add_argument(
        "--steps", 
        type=int, 
        default=5,
        help="Number of steps for the long-running task (default: 5)"
    )
    parser.add_argument(
        "--name", 
        default="World",
        help="Name for the greeting resource (default: World)"
    )
    args = parser.parse_args()

    print(f"Connecting to MCP server at {args.url} using Streamable HTTP transport...")
    
    # Create a client session using the streamable HTTP transport
    async with http_client(args.url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connection initialized successfully!")
            
            # List available tools
            print("\nListing available tools...")
            tools = await session.list_tools()
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # List available resources
            print("\nListing available resources...")
            resources = await session.list_resources()
            for resource in resources:
                print(f"  - {resource.name}: {resource.description}")
            
            # Call the BMI calculation tool
            print(f"\nCalculating BMI for weight={args.weight}kg, height={args.height}m...")
            bmi_result = await session.call_tool(
                "calculate_bmi", 
                arguments={"weight_kg": args.weight, "height_m": args.height}
            )
            print(f"BMI result: {bmi_result}")
            
            # Read a greeting resource
            print(f"\nReading greeting resource for name={args.name}...")
            greeting_content, mime_type = await session.read_resource(f"greeting://{args.name}")
            print(f"Greeting: {greeting_content}")
            
            # Call the long-running task with progress updates
            print(f"\nRunning long task with {args.steps} steps...")
            print("Progress updates will be streamed via the Streamable HTTP transport:")
            
            # Set up a progress callback to handle streaming updates
            async def progress_callback(progress):
                percent = int((progress.current / progress.total) * 100)
                print(f"  Progress: {progress.current}/{progress.total} ({percent}%)")
            
            # Set up an info callback to handle info messages
            async def info_callback(info):
                print(f"  Info: {info.message}")
            
            # Register the callbacks
            session.on_progress(progress_callback)
            session.on_info(info_callback)
            
            # Call the long-running task
            result = await session.call_tool(
                "long_running_task", 
                arguments={"steps": args.steps}
            )
            
            print("\nLong task completed!")
            print(f"Result: {result}")
            
            print("\nStreamable HTTP client example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
