#!/usr/bin/env python3
"""
VS Code MCP Demo

This script demonstrates how to use the Augment Adam MCP server with VS Code.
It starts the MCP server and provides instructions for connecting VS Code to it.
"""

import os
import sys
import logging
import argparse
import subprocess
import webbrowser
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from augment_adam.server.run_mcp_server import main as run_mcp_server

def print_instructions(host: str, port: int):
    """Print instructions for connecting VS Code to the MCP server."""
    print("\n" + "=" * 80)
    print("VS Code MCP Demo")
    print("=" * 80)
    print(f"\nMCP server running at http://{host}:{port}/mcp")
    print("\nTo connect VS Code to the MCP server:")
    print("1. Open VS Code")
    print("2. Open the Command Palette (Ctrl+Shift+P)")
    print("3. Type 'MCP: Connect to Server'")
    print(f"4. Enter the URL: http://{host}:{port}/mcp")
    print("\nIf you're running VS Code in a different environment (e.g., Docker, WSL),")
    print("you may need to use socat to create a bridge:")
    print(f"\n    docker run -i --rm alpine/socat STDIO TCP:host.docker.internal:{port}")
    print("\nPress Ctrl+C to stop the MCP server")
    print("=" * 80 + "\n")

def open_vscode_docs():
    """Open the VS Code MCP documentation in a browser."""
    url = "https://code.visualstudio.com/docs/copilot/chat/mcp-servers"
    print(f"Opening VS Code MCP documentation: {url}")
    webbrowser.open(url)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="VS Code MCP Demo")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8811, help="Port to bind to")
    parser.add_argument("--docs", action="store_true", help="Open VS Code MCP documentation")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Open VS Code MCP documentation if requested
    if args.docs:
        open_vscode_docs()
    
    # Print instructions
    print_instructions(args.host, args.port)
    
    # Start the MCP server
    # We use sys.argv to pass the arguments to the MCP server
    sys.argv = [sys.argv[0], "--host", args.host, "--port", str(args.port)]
    if args.debug:
        sys.argv.append("--debug")
    
    try:
        run_mcp_server()
    except KeyboardInterrupt:
        print("\nMCP server stopped")

if __name__ == "__main__":
    main()
