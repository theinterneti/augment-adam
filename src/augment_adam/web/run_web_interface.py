#!/usr/bin/env python3
"""Run the Augment Adam web interface.

This script launches the Augment Adam web interface.

Usage:
    python -m augment_adam.web.run_web_interface [--port PORT] [--model MODEL]
"""

import logging
import argparse
import sys
import os

from augment_adam.web.server import start_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run the Augment Adam web interface")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--model", default="llama3:8b", help="Model to use")
    parser.add_argument("--theme", default="soft", help="Theme to use")
    parser.add_argument("--title", default="Augment Adam Assistant", help="Title of the interface")
    parser.add_argument("--description", default="An open-source AI assistant focused on personal automation.", help="Description of the interface")
    parser.add_argument("--version", default="0.1.0", help="Version of the interface")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Start the server
        start_server(
            host=args.host,
            port=args.port,
            model_name=args.model,
            theme=args.theme,
            title=args.title,
            description=args.description,
            version=args.version,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down web interface")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Error starting web interface: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
