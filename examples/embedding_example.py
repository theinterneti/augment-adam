#!/usr/bin/env python3
"""
Embedding example for the model management system.

This script demonstrates how to use the ModelManager for generating embeddings.
"""

import os
import sys
from pathlib import Path
import numpy as np

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_manager import ModelManager


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    """Run the example."""
    # Create a model manager with default settings
    # This will use Ollama with a medium-sized model
    manager = ModelManager()
    
    print(f"Using model: {manager.model_name} ({manager.model_type})")
    
    # Generate embeddings for some texts
    texts = [
        "Python is a programming language.",
        "Python is a type of snake.",
        "Programming languages are used to write software.",
        "Snakes are reptiles."
    ]
    
    print("\nGenerating embeddings for the following texts:")
    for i, text in enumerate(texts):
        print(f"  {i+1}. {text}")
    
    # Generate embeddings
    embeddings = manager.batch_embed(texts)
    
    print(f"\nEmbedding dimensions: {len(embeddings[0])}")
    
    # Calculate similarities
    print("\nSimilarities:")
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            similarity = cosine_similarity(embeddings[i], embeddings[j])
            print(f"  Similarity between text {i+1} and {j+1}: {similarity:.4f}")
    
    # Find the most similar pair
    max_similarity = 0
    max_pair = (0, 0)
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            similarity = cosine_similarity(embeddings[i], embeddings[j])
            if similarity > max_similarity:
                max_similarity = similarity
                max_pair = (i, j)
    
    print(f"\nMost similar pair: {max_pair[0]+1} and {max_pair[1]+1} with similarity {max_similarity:.4f}")
    print(f"  Text 1: {texts[max_pair[0]]}")
    print(f"  Text 2: {texts[max_pair[1]]}")


if __name__ == "__main__":
    main()
