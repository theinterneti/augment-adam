#!/usr/bin/env python3
"""
Test script for the Qwen 3 model integration.

This script demonstrates how to use the ModelManager to work with Qwen 3 models,
with HuggingFace as the primary backend and Ollama as a fallback.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test Qwen 3 model integration")
    parser.add_argument(
        "--backend",
        choices=["huggingface", "ollama", "auto"],
        default="auto",
        help="Model backend to use (default: auto)"
    )
    parser.add_argument(
        "--model_size",
        choices=["qwen3_small", "qwen3_medium", "qwen3_large", "qwen3_xl", "qwen3_xxl", "qwen3_xxxl"],
        default="qwen3_small",
        help="Size of the Qwen 3 model to use (default: qwen3_small)"
    )
    parser.add_argument(
        "--prompt",
        default="Explain the key features of Qwen 3 models compared to previous versions.",
        help="Prompt to send to the model"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)"
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=500,
        help="Maximum number of tokens to generate (default: 500)"
    )
    parser.add_argument(
        "--cache_dir",
        help="Directory to cache models"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Share models between backends"
    )
    return parser.parse_args()


def main():
    """Run the test."""
    args = parse_args()
    
    # Determine the backend to use
    if args.backend == "auto":
        # Try HuggingFace first, fall back to Ollama
        try:
            import torch
            import transformers
            backend = "huggingface"
            logger.info("Using HuggingFace backend")
        except ImportError:
            backend = "ollama"
            logger.info("Falling back to Ollama backend")
    else:
        backend = args.backend
        logger.info(f"Using {backend} backend as specified")
    
    # Create the model manager
    manager = ModelManager(
        model_type=backend,
        model_size=args.model_size,
        cache_dir=args.cache_dir,
        share_with_ollama=args.share
    )
    
    # Print model information
    model_info = manager.get_model_info()
    print(f"\n=== Model Information ===")
    print(json.dumps(model_info, indent=2))
    
    # Generate a response
    print(f"\n=== Generating response with {args.model_size} ===")
    print(f"Prompt: {args.prompt}")
    print("\nGenerating...")
    
    response = manager.generate_response(
        prompt=args.prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    print("\nResponse:")
    print(response)
    
    # Get available models
    available_models = manager.get_available_models()
    print("\n=== Available Models ===")
    if isinstance(available_models, dict):
        for backend, models in available_models.items():
            print(f"\n{backend.upper()} Models:")
            for model in models:
                print(f"- {model}")
    else:
        for model in available_models:
            print(f"- {model}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
