#!/usr/bin/env python3
"""
Setup script for downloading and configuring models.
This script is called from the post-start.sh script in the devcontainer.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def setup_ollama_models():
    """Setup Ollama models."""
    print("Setting up Ollama models...")
    
    # List of models to pull
    models = ["llama3"]
    
    for model in models:
        try:
            print(f"Pulling Ollama model: {model}")
            # Check if the model is already pulled
            result = subprocess.run(
                ["curl", "-s", "http://ollama:11434/api/tags"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if model not in result.stdout:
                # Pull the model
                subprocess.run(
                    ["ollama", "pull", model],
                    check=True
                )
                print(f"Successfully pulled {model}")
            else:
                print(f"Model {model} is already available")
        except subprocess.CalledProcessError as e:
            print(f"Error pulling model {model}: {e}")
            continue

def setup_huggingface_models():
    """Setup HuggingFace models."""
    print("Setting up HuggingFace models...")
    
    # This would typically use the Hugging Face Hub API to download models
    # For now, we'll just create the cache directory
    cache_dir = Path("/workspace/.cache/huggingface")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"HuggingFace cache directory created at {cache_dir}")

def setup_domain_specific_models(domains):
    """Setup domain-specific models."""
    print(f"Setting up models for domains: {', '.join(domains)}")
    
    # Example implementation - in a real scenario, you would download
    # specific models based on the domains
    for domain in domains:
        print(f"Setting up models for domain: {domain}")
        # Domain-specific setup would go here

def main():
    parser = argparse.ArgumentParser(description="Setup models for augment-adam")
    parser.add_argument("--domains", nargs="+", default=[], 
                        help="Domains to setup models for")
    parser.add_argument("--skip-ollama", action="store_true",
                        help="Skip Ollama model setup")
    parser.add_argument("--skip-huggingface", action="store_true",
                        help="Skip HuggingFace model setup")
    
    args = parser.parse_args()
    
    if not args.skip_ollama:
        setup_ollama_models()
    
    if not args.skip_huggingface:
        setup_huggingface_models()
    
    if args.domains:
        setup_domain_specific_models(args.domains)
    
    print("Model setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
