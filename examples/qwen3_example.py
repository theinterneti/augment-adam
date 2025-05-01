#!/usr/bin/env python3
"""
Qwen 3 example for the model management system.

This script demonstrates how to use Qwen 3 models with the model management system.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager


def main():
    """Run the example."""
    # Create a cache directory
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_models")
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"Using cache directory: {cache_dir}")
    
    # Create a model manager with Qwen 3 model
    print("\nCreating model manager with Qwen 3 model...")
    manager = ModelManager(
        model_type="huggingface",
        model_size="qwen3_medium",  # Use the medium-sized Qwen 3 model
        cache_dir=cache_dir
    )
    
    print(f"Using model: {manager.model_name} ({manager.model_type})")
    
    # Get model information
    model_info = manager.get_model_info()
    print("\nModel information:")
    for key, value in model_info.items():
        print(f"  {key}: {value}")
    
    # Generate a response
    prompt = "What are the key features of Qwen 3 models?"
    system_prompt = "You are a helpful assistant with expertise in AI and language models."
    
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
    
    # Test the long context window
    print("\nTesting long context window...")
    
    # Generate a long prompt
    long_prompt = "Analyze the following text:\n\n" + "This is a test. " * 1000
    
    # Get token count
    token_count = manager.get_token_count(long_prompt)
    print(f"Token count: {token_count}")
    
    # Generate a response with the long prompt
    print("\nGenerating response with long prompt...")
    
    long_response = manager.generate_response(
        prompt=long_prompt,
        system_prompt="Summarize the text in one sentence.",
        temperature=0.7,
        max_tokens=100
    )
    
    print(f"\nResponse to long prompt:\n{long_response}")


if __name__ == "__main__":
    main()
