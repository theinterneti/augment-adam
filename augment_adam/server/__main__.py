"""Server entry point for Augment Adam.

This module provides an entry point for the Augment Adam server.

Usage:
    python -m augment_adam.server [--host HOST] [--port PORT]

Version: 0.1.0
Created: 2025-04-29
"""

import argparse
import logging
from augment_adam.server.api import start_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Augment Adam Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Augment Adam Server on {args.host}:{args.port}")
    start_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
