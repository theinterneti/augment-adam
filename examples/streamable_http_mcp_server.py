#!/usr/bin/env python3
"""
Streamable HTTP Transport Example for MCP Servers

This script demonstrates how to implement a Model Context Protocol (MCP) server
that supports both the new Streamable HTTP transport and the existing SSE transport.

Based on the Cloudflare blog post:
https://blog.cloudflare.com/streamable-http-mcp-servers-python/
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required libraries
try:
    from fastapi import FastAPI
    from mcp.server.fastmcp import FastMCP, Context, Image
except ImportError:
    print("This example requires FastAPI and the MCP Python SDK.")
    print("Install with: pip install fastapi mcp[cli]")
    sys.exit(1)

# Create a FastMCP server instance
mcp = FastMCP("Streamable HTTP Demo")

# Define a simple tool
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

# Define a resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Define a long-running tool that demonstrates streaming
@mcp.tool()
async def long_running_task(steps: int, ctx: Context) -> str:
    """A long-running task that demonstrates streaming progress updates"""
    result = []
    for i in range(steps):
        # Report progress to the client
        await ctx.report_progress(i, steps)
        
        # Send an info message that will be streamed to the client
        ctx.info(f"Processing step {i+1} of {steps}")
        
        # Simulate work
        await asyncio.sleep(0.5)
        
        result.append(f"Step {i+1} completed")
    
    return "\n".join(result)

# Create a FastAPI app
app = FastAPI(title="Streamable HTTP MCP Server Example")

# Mount the MCP server to support both transport methods
# 1. SSE transport at /sse endpoint
app.mount("/sse", mcp.serveSSE("/sse").fetch)

# 2. New Streamable HTTP transport at /mcp endpoint
app.mount("/mcp", mcp.serve("/mcp").fetch)

# Add a simple root endpoint
@app.get("/")
async def root():
    return {
        "message": "MCP Server with Streamable HTTP Transport",
        "endpoints": {
            "sse": "/sse - Legacy SSE transport",
            "streamable_http": "/mcp - New Streamable HTTP transport"
        },
        "tools": ["calculate_bmi", "long_running_task"],
        "resources": ["greeting://{name}"]
    }

# Run the server directly if executed as a script
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting MCP server with Streamable HTTP support on port {port}")
    print("Available endpoints:")
    print(f"  - SSE transport: http://localhost:{port}/sse")
    print(f"  - Streamable HTTP transport: http://localhost:{port}/mcp")
    print("\nPress Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=port)
