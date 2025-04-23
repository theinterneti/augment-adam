"""Embedding module for the MCP-enabled context engine."""

import os
import numpy as np
from typing import List, Union

class EmbeddingModel:
    """Simple embedding model for text to vector conversion."""
    
    def __init__(self):
        """Initialize the embedding model."""
        self.model_name = "simple-hash-embedding"
        self.dimension = 384
    
    def encode(self, text: Union[str, List[str]]) -> List[float]:
        """Encode text to vector using a simple hash function.
        
        Args:
            text: Text to encode
            
        Returns:
            Vector embedding
        """
        if isinstance(text, list):
            return [self._hash_text(t) for t in text]
        return self._hash_text(text)
    
    def _hash_text(self, text: str) -> List[float]:
        """Hash text to a vector.
        
        Args:
            text: Text to hash
            
        Returns:
            Vector embedding
        """
        # Use a simple hash function to generate a vector
        import hashlib
        
        # Initialize the vector
        vector = np.zeros(self.dimension, dtype=np.float32)
        
        # Split the text into words
        words = text.split()
        
        # Hash each word and add to the vector
        for i, word in enumerate(words):
            # Hash the word
            hash_value = int(hashlib.md5(word.encode()).hexdigest(), 16)
            
            # Use the hash to set values in the vector
            for j in range(min(10, self.dimension)):
                idx = (hash_value + j) % self.dimension
                vector[idx] = 0.1 * ((hash_value % 20) - 10) + vector[idx]
        
        # Normalize the vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.tolist()


# Singleton instance
embedding_model = EmbeddingModel()
