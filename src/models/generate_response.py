#!/usr/bin/env python3
"""
Generate Response Script for Dukat: Development Environment Assistant

This script is called by the VS Code extension to generate responses
from the language model with a focus on Docker, WSL, and devcontainer
development environments.
"""

import argparse
import json
import sys
from model_manager import ModelManager

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate a response from the language model")
    parser.add_argument("--prompt", required=True, help="The user prompt")
    parser.add_argument("--system", help="Optional system prompt")
    parser.add_argument("--model", default="llama3:8b", help="Model name to use")
    parser.add_argument("--local", default="true", help="Whether to use local model (true/false)")
    parser.add_argument("--domain", default="general",
                      choices=["docker", "wsl", "devcontainer", "general"],
                      help="Domain of expertise (docker, wsl, devcontainer, general)")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()

    # Convert string boolean to actual boolean
    use_local = args.local.lower() == "true"

    # Initialize the model manager with the specified domain
    model_manager = ModelManager(model_name=args.model, use_local=use_local, domain=args.domain)

    # Generate the response
    response = model_manager.generate_response(
        prompt=args.prompt,
        system_prompt=args.system
    )

    # Add domain-specific information if available
    if args.domain == "docker" and model_manager.docker_available:
        try:
            # Add a note about Docker availability
            docker_info = model_manager.get_docker_info()
            if docker_info.get("available"):
                response += "\n\n---\n*Note: Docker is available on this system.*"
        except Exception as e:
            print(f"Error getting Docker info: {e}", file=sys.stderr)

    elif args.domain == "wsl" and model_manager.wsl_available:
        try:
            # Add a note about WSL availability
            wsl_info = model_manager.get_wsl_info()
            if wsl_info.get("available"):
                response += "\n\n---\n*Note: WSL is available on this system.*"
        except Exception as e:
            print(f"Error getting WSL info: {e}", file=sys.stderr)

    # Print the response (will be captured by the JS bridge)
    print(response)

    return 0

if __name__ == "__main__":
    sys.exit(main())
