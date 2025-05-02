"""
TextChunker module.

This module contains the TextChunker class for chunking text.
"""

from typing import List, Optional

from augment_adam.context.chunking.base import Chunker

class TextChunker(Chunker):
    """
    TextChunker class for chunking text.
    
    This class implements the Chunker interface for text chunking.
    """
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize the TextChunker.
        
        Args:
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> List[str]:
        """
        Chunk the text into smaller pieces.
        
        Args:
            text: The text to chunk
            
        Returns:
            A list of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Adjust end to avoid cutting words
            if end < len(text):
                # Find the last space before the end
                while end > start and text[end] != ' ':
                    end -= 1
                
                # If no space found, use the original end
                if end == start:
                    end = min(start + self.chunk_size, len(text))
            
            chunks.append(text[start:end])
            
            # Move start for the next chunk, considering overlap
            start = end - self.overlap
            
            # Ensure we make progress
            if start >= end:
                start = end
        
        return chunks
    
    def merge_chunks(self, chunks: List[str]) -> str:
        """
        Merge chunks back into a single text.
        
        Args:
            chunks: The chunks to merge
            
        Returns:
            The merged text
        """
        if not chunks:
            return ""
        
        # Simple concatenation for now
        return " ".join(chunks)
