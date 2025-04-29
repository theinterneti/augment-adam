#!/usr/bin/env python3
"""
Test script for streaming responses from models.

This script demonstrates how to use the ModelManager to generate streaming
responses from language models.
"""

import os
import sys
import json
import argparse
import logging
import time
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
    parser = argparse.ArgumentParser(description="Test streaming responses")
    parser.add_argument(
        "--backend",
        choices=["huggingface", "ollama", "auto"],
        default="auto",
        help="Model backend to use (default: auto)"
    )
    parser.add_argument(
        "--model_size",
        choices=["small", "medium", "large", "xl", "qwen3_small", "qwen3_medium", "qwen3_large"],
        default="medium",
        help="Size of the model to use (default: medium)"
    )
    parser.add_argument(
        "--prompt",
        default="Write a short story about a robot learning to paint.",
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
        cache_dir=args.cache_dir
    )
    
    # Print model information
    model_info = manager.get_model_info()
    print(f"\n=== Model Information ===")
    print(json.dumps(model_info, indent=2))
    
    # Generate a streaming response
    print(f"\n=== Generating streaming response with {args.model_size} ===")
    print(f"Prompt: {args.prompt}")
    print("\nResponse:")
    
    # Stream the response
    start_time = time.time()
    for chunk in manager.generate_stream(
        prompt=args.prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    ):
        print(chunk, end="", flush=True)
    
    # Print timing information
    elapsed_time = time.time() - start_time
    print(f"\n\nGeneration completed in {elapsed_time:.2f} seconds")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
