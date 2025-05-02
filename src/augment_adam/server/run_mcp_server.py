#!/usr/bin/env python3
"""
Run the MCP server for Augment Adam.

This script starts a FastAPI server with MCP support, allowing VS Code and other
MCP clients to interact with Augment Adam.
"""

import os
import sys
import logging
import argparse
import uvicorn
from fastapi import FastAPI

from augment_adam.context_engine.mcp import create_mcp_context_engine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run the MCP server for Augment Adam")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8811, help="Port to bind to")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up the FastAPI app
    app = FastAPI(
        title="Augment Adam MCP Server",
        description="MCP server for Augment Adam",
        version="0.1.0"
    )
    
    # Create the MCP Context Engine
    engine = create_mcp_context_engine(app, api_key=args.api_key)
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the server
    logger.info(f"Starting MCP server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
