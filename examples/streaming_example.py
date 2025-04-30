#!/usr/bin/env python3
"""
Streaming example for the model management system.

This script demonstrates how to use the ModelManager for streaming text generation.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager


def main():
    """Run the example."""
    # Create a model manager with default settings
    # This will use Ollama with a medium-sized model
    manager = ModelManager()
    
    print(f"Using model: {manager.model_name} ({manager.model_type})")
    
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


if __name__ == "__main__":
    main()
