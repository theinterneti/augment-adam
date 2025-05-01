#!/usr/bin/env python3
"""
Model sharing example for the model management system.

This script demonstrates how to share models between HuggingFace and Ollama backends.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager
from src.models.model_registry import get_registry


def main():
    """Run the example."""
    # Create a cache directory
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_models")
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"Using cache directory: {cache_dir}")
    
    # Create a model manager with HuggingFace backend
    print("\nCreating HuggingFace model manager...")
    hf_manager = ModelManager(
        model_type="huggingface",
        model_size="small",  # Use a small model for faster loading
        cache_dir=cache_dir,
        share_with_ollama=True  # Enable model sharing
    )
    
    print(f"Using HuggingFace model: {hf_manager.model_name}")
    
    # Generate a response with HuggingFace
    prompt = "What is model sharing in the context of language models?"
    system_prompt = "You are a helpful assistant with expertise in AI and language models."
    
    print(f"\nPrompt: {prompt}")
    print(f"System prompt: {system_prompt}")
    print("\nGenerating response with HuggingFace...")
    
    hf_response = hf_manager.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=200
    )
    
    print(f"\nHuggingFace response:\n{hf_response}")
    
    # Create a model manager with Ollama backend using the same model
    print("\nCreating Ollama model manager with the shared model...")
    ollama_manager = ModelManager(
        model_type="ollama",
        model_name=hf_manager.model_name.split("/")[-1],  # Use the same model name
        cache_dir=cache_dir
    )
    
    print(f"Using Ollama model: {ollama_manager.model_name}")
    
    # Generate a response with Ollama
    print("\nGenerating response with Ollama...")
    
    ollama_response = ollama_manager.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=200
    )
    
    print(f"\nOllama response:\n{ollama_response}")
    
    # Get the registry and list all models
    registry = get_registry()
    models = registry.list_models()
    
    print("\nRegistered models:")
    for model in models:
        print(f"  {model['backend']}:{model['model_id']}")


if __name__ == "__main__":
    main()
