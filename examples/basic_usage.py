#!/usr/bin/env python3
"""
Basic usage example for the model management system.

This script demonstrates how to use the ModelManager for text generation.
"""

import os
import sys
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
    
    # Generate a response
    prompt = "What are the key features of Python 3.12?"
    system_prompt = "You are a helpful assistant with expertise in programming languages."
    
    print(f"\nPrompt: {prompt}")
    print(f"System prompt: {system_prompt}")
    print("\nGenerating response...")
    
    response = manager.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=500
    )
    
    print(f"\nResponse:\n{response}")
    
    # Get model information
    model_info = manager.get_model_info()
    print("\nModel information:")
    for key, value in model_info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
