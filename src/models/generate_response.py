#!/usr/bin/env python3
"""
Generate Response Script for Augment Adam

This script provides a command-line interface for generating responses
from language models, with support for both HuggingFace and Ollama backends.
"""

import argparse
import json
import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager, get_model_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate a response from the language model")
    parser.add_argument("--prompt", required=True, help="The user prompt")
    parser.add_argument("--system", help="Optional system prompt")
    parser.add_argument("--model_type", default="ollama", choices=["huggingface", "ollama"],
                      help="Type of model to use (huggingface or ollama)")
    parser.add_argument("--model_name", help="Model name to use (if not specified, will use recommended model for size)")
    parser.add_argument("--model_size", default="medium",
                      help="Size of model to use (small, medium, large, xl, qwen3_small, qwen3_medium, etc.)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--max_tokens", type=int, default=1000, help="Maximum number of tokens to generate")
    parser.add_argument("--top_p", type=float, default=0.9, help="Nucleus sampling parameter")
    parser.add_argument("--domain", default="general",
                      choices=["docker", "wsl", "devcontainer", "code", "general"],
                      help="Domain of expertise")
    parser.add_argument("--cache_dir", help="Directory to cache models")
    parser.add_argument("--stream", action="store_true", help="Stream the response")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()

    # Use the shared cache directory if specified
    cache_dir = args.cache_dir
    if not cache_dir:
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_models")

    # Initialize the model manager with the specified parameters
    model_manager = get_model_manager(
        model_type=args.model_type,
        model_name=args.model_name,
        model_size=args.model_size,
        domain=args.domain,
        cache_dir=cache_dir
    )

    # Generate the response
    if args.stream:
        # Stream the response
        print("Streaming response...\n")
        for chunk in model_manager.generate_stream(
            prompt=args.prompt,
            system_prompt=args.system,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            top_p=args.top_p
        ):
            print(chunk, end="", flush=True)
        print("\n")
    else:
        # Generate the full response
        response = model_manager.generate_response(
            prompt=args.prompt,
            system_prompt=args.system,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            top_p=args.top_p
        )

        # Add domain-specific information if available
        if args.domain == "docker" and model_manager.docker_available:
            try:
                # Add a note about Docker availability
                docker_info = model_manager.get_docker_info()
                if docker_info.get("available"):
                    response += "\n\n---\n*Note: Docker is available on this system.*"
            except Exception as e:
                logger.error(f"Error getting Docker info: {e}")

        elif args.domain == "wsl" and model_manager.wsl_available:
            try:
                # Add a note about WSL availability
                wsl_info = model_manager.get_wsl_info()
                if wsl_info.get("available"):
                    response += "\n\n---\n*Note: WSL is available on this system.*"
            except Exception as e:
                logger.error(f"Error getting WSL info: {e}")

        # Print the response
        print(response)

    # Print model information
    model_info = model_manager.get_model_info()
    logger.info(f"Used model: {model_info.get('model_id')} ({model_info.get('backend', 'unknown')} backend)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
