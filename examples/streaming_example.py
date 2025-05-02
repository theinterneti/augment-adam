#!/usr/bin/env python3
"""
Streaming example for the model management system.

This script demonstrates how to use the ModelManager for streaming text generation.
It also includes information about different streaming transport methods for MCP servers.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager


def print_transport_info():
    """Print information about different streaming transport methods."""
    print("\n=== Streaming Transport Methods ===")
    print("When building MCP servers, you can use different transport methods:")
    print("1. Server-Sent Events (SSE) - Traditional method using two endpoints:")
    print("   - One endpoint for the client to receive streaming responses")
    print("   - Another endpoint for the client to send requests")
    print("\n2. Streamable HTTP - New method using a single endpoint:")
    print("   - One endpoint for both sending requests and receiving responses")
    print("   - Supports automatic connection upgrades for streaming")
    print("   - Provides better resumability and error handling")
    print("\nSee examples/streamable_http_mcp_server.py for an implementation example.")
    print("See docs/streamable_http_transport.md for detailed documentation.")
    print("=" * 40)


def main():
    """Run the example."""
    # Print information about streaming transport methods
    print_transport_info()

    # Create a model manager with default settings
    # This will use Ollama with a medium-sized model
    manager = ModelManager()

    print(f"\nUsing model: {manager.model_name} ({manager.model_type})")

    # Generate a streaming response
    prompt = "Write a short story about a robot learning to paint."
    system_prompt = "You are a creative writing assistant."

    print(f"\nPrompt: {prompt}")
    print(f"System prompt: {system_prompt}")
    print("\nGenerating streaming response...\n")

    # Generate streaming response
    for chunk in manager.generate_stream(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=500
    ):
        print(chunk, end="", flush=True)
        time.sleep(0.01)  # Slow down the output for demonstration

    print("\n\nStreaming complete!")

    print("\nNote: This example demonstrates basic text streaming.")
    print("For MCP-specific streaming with Streamable HTTP transport,")
    print("see the examples/streamable_http_mcp_server.py and")
    print("examples/streamable_http_mcp_client.py examples.")


if __name__ == "__main__":
    main()
