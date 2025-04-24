"""Intelligent Chunker for the Context Engine.

This module provides a chunker for intelligently splitting content into
manageable chunks.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)

logger = logging.getLogger(__name__)


class IntelligentChunker:
    """Intelligent Chunker for the Context Engine.
    
    This class intelligently splits content into manageable chunks based on
    semantic boundaries rather than arbitrary character limits.
    
    Attributes:
        max_chunk_size: The maximum size of a chunk in characters
        min_chunk_size: The minimum size of a chunk in characters
        overlap: The number of characters to overlap between chunks
    """
    
    def __init__(
        self,
        max_chunk_size: int = 1000,
        min_chunk_size: int = 100,
        overlap: int = 50
    ):
        """Initialize the Intelligent Chunker.
        
        Args:
            max_chunk_size: The maximum size of a chunk in characters
            min_chunk_size: The minimum size of a chunk in characters
            overlap: The number of characters to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap
        
        logger.info("Intelligent Chunker initialized")
    
    def chunk(self, content: str) -> List[str]:
        """Chunk content intelligently.
        
        Args:
            content: The content to chunk
            
        Returns:
            A list of chunks
        """
        try:
            if not content:
                return []
            
            if len(content) <= self.max_chunk_size:
                return [content]
            
            # Split by paragraphs
            paragraphs = re.split(r'\n\s*\n', content)
            
            chunks = []
            current_chunk = ""
            
            for paragraph in paragraphs:
                # If adding this paragraph would exceed max_chunk_size
                if len(current_chunk) + len(paragraph) + 2 > self.max_chunk_size:
                    # If current_chunk is not empty, add it to chunks
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    # If paragraph is longer than max_chunk_size, split it
                    if len(paragraph) > self.max_chunk_size:
                        # Split by sentences
                        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                        
                        current_chunk = ""
                        for sentence in sentences:
                            # If adding this sentence would exceed max_chunk_size
                            if len(current_chunk) + len(sentence) + 1 > self.max_chunk_size:
                                # If current_chunk is not empty, add it to chunks
                                if current_chunk:
                                    chunks.append(current_chunk)
                                
                                # If sentence is longer than max_chunk_size, split it
                                if len(sentence) > self.max_chunk_size:
                                    # Split by words
                                    words = sentence.split()
                                    
                                    current_chunk = ""
                                    for word in words:
                                        # If adding this word would exceed max_chunk_size
                                        if len(current_chunk) + len(word) + 1 > self.max_chunk_size:
                                            # If current_chunk is not empty, add it to chunks
                                            if current_chunk:
                                                chunks.append(current_chunk)
                                            
                                            current_chunk = word
                                        else:
                                            # Add word to current_chunk
                                            if current_chunk:
                                                current_chunk += " " + word
                                            else:
                                                current_chunk = word
                                else:
                                    # Start a new chunk with this sentence
                                    current_chunk = sentence
                            else:
                                # Add sentence to current_chunk
                                if current_chunk:
                                    current_chunk += " " + sentence
                                else:
                                    current_chunk = sentence
                    else:
                        # Start a new chunk with this paragraph
                        current_chunk = paragraph
                else:
                    # Add paragraph to current_chunk
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # Add the last chunk if not empty
            if current_chunk:
                chunks.append(current_chunk)
            
            # Add overlap between chunks
            if self.overlap > 0 and len(chunks) > 1:
                overlapped_chunks = []
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        # Add overlap from previous chunk
                        prev_chunk = chunks[i - 1]
                        overlap_text = prev_chunk[-self.overlap:] if len(prev_chunk) > self.overlap else prev_chunk
                        chunk = overlap_text + "... " + chunk
                    
                    overlapped_chunks.append(chunk)
                
                chunks = overlapped_chunks
            
            logger.info(f"Chunked content into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to chunk content",
                category=ErrorCategory.RESOURCE,
                details={"content_length": len(content) if content else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple chunking
            return self._simple_chunk(content)
    
    def _simple_chunk(self, content: str) -> List[str]:
        """Simple chunking by character count.
        
        Args:
            content: The content to chunk
            
        Returns:
            A list of chunks
        """
        if not content:
            return []
        
        chunks = []
        for i in range(0, len(content), self.max_chunk_size - self.overlap):
            chunk = content[i:i + self.max_chunk_size]
            chunks.append(chunk)
        
        return chunks
