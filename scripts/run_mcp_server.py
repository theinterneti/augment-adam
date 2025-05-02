#!/usr/bin/env python3
"""
Run the MCP server for VS Code integration.

This script starts the MCP server that VS Code can connect to for context engine integration.
"""

import os
import sys
import logging
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from augment_adam.server.run_mcp_server import main

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the MCP server
    main()
