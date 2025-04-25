"""
Base classes for the chunking module.

This module provides the base classes for the chunking module, including
the Chunker base class and various chunker implementations.
"""

import re
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.context.core.base import Context, ContextType


@tag("context.chunking")
class Chunker(ABC):
    """
    Base class for content chunkers.
    
    This class defines the interface for content chunkers, which break down
    content into smaller chunks for more efficient processing and retrieval.
    
    Attributes:
        name: The name of the chunker.
        metadata: Additional metadata for the chunker.
    
    TODO(Issue #7): Add support for chunker validation
    TODO(Issue #7): Implement chunker analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the chunker.
        
        Args:
            name: The name of the chunker.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def chunk(self, content: str, context_type: ContextType, **kwargs: Any) -> List[Context]:
        """
        Chunk content into smaller contexts.
        
        Args:
            content: The content to chunk.
            context_type: The type of context.
            **kwargs: Additional arguments for the chunker.
            
        Returns:
            List of context chunks.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the chunker.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the chunker.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("context.chunking.text")
class TextChunker(Chunker):
    """
    Chunker for text content.
    
    This class implements a chunker for text content, which breaks down
    text into smaller chunks based on various strategies.
    
    Attributes:
        name: The name of the chunker.
        metadata: Additional metadata for the chunker.
        chunk_size: The maximum size of each chunk in characters.
        chunk_overlap: The number of characters to overlap between chunks.
        strategy: The chunking strategy to use.
    
    TODO(Issue #7): Add support for more chunking strategies
    TODO(Issue #7): Implement chunker validation
    """
    
    def __init__(
        self,
        name: str = "text_chunker",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        strategy: str = "paragraph",
    ) -> None:
        """
        Initialize the text chunker.
        
        Args:
            name: The name of the chunker.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            strategy: The chunking strategy to use ("paragraph", "sentence", "fixed").
        """
        super().__init__(name)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        
        self.metadata["chunk_size"] = chunk_size
        self.metadata["chunk_overlap"] = chunk_overlap
        self.metadata["strategy"] = strategy
    
    def chunk(self, content: str, context_type: ContextType, **kwargs: Any) -> List[Context]:
        """
        Chunk text content into smaller contexts.
        
        Args:
            content: The text content to chunk.
            context_type: The type of context.
            **kwargs: Additional arguments for the chunker.
                chunk_size: Override the default chunk size.
                chunk_overlap: Override the default chunk overlap.
                strategy: Override the default chunking strategy.
                parent_id: ID of the parent context.
                source: Source of the content.
                tags: List of tags for the chunks.
            
        Returns:
            List of context chunks.
        """
        # Get chunking parameters
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        strategy = kwargs.get("strategy", self.strategy)
        parent_id = kwargs.get("parent_id")
        source = kwargs.get("source")
        tags = kwargs.get("tags", [])
        
        # Choose chunking strategy
        if strategy == "paragraph":
            chunks = self._chunk_by_paragraph(content, chunk_size, chunk_overlap)
        elif strategy == "sentence":
            chunks = self._chunk_by_sentence(content, chunk_size, chunk_overlap)
        else:  # Default to fixed-size chunking
            chunks = self._chunk_fixed_size(content, chunk_size, chunk_overlap)
        
        # Create context objects for each chunk
        contexts = []
        for i, chunk in enumerate(chunks):
            context = Context(
                content=chunk,
                context_type=context_type,
                parent_id=parent_id,
                source=source,
                tags=tags.copy(),
                metadata={
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "chunker": self.name,
                    "strategy": strategy,
                }
            )
            contexts.append(context)
        
        return contexts
    
    def _chunk_by_paragraph(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chunk text by paragraphs.
        
        Args:
            content: The text content to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            
        Returns:
            List of text chunks.
        """
        # Split content into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the chunk size, start a new chunk
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Start new chunk with overlap
                if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                    current_chunk = current_chunk[-chunk_overlap:] + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_by_sentence(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chunk text by sentences.
        
        Args:
            content: The text content to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            
        Returns:
            List of text chunks.
        """
        # Split content into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the chunk size, start a new chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Start new chunk with overlap
                if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                    current_chunk = current_chunk[-chunk_overlap:] + " " + sentence
                else:
                    current_chunk = sentence
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_fixed_size(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chunk text into fixed-size chunks.
        
        Args:
            content: The text content to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            
        Returns:
            List of text chunks.
        """
        chunks = []
        
        # If content is smaller than chunk size, return it as a single chunk
        if len(content) <= chunk_size:
            return [content]
        
        # Otherwise, create overlapping chunks
        start = 0
        while start < len(content):
            end = start + chunk_size
            
            # If this is not the first chunk, include overlap
            if start > 0:
                start = start - chunk_overlap
                end = start + chunk_size
            
            # If we've reached the end of the content, adjust the end
            if end > len(content):
                end = len(content)
            
            # Add the chunk
            chunks.append(content[start:end])
            
            # Move to the next chunk
            start = end
        
        return chunks


@tag("context.chunking.code")
class CodeChunker(Chunker):
    """
    Chunker for code content.
    
    This class implements a chunker for code content, which breaks down
    code into smaller chunks based on various strategies.
    
    Attributes:
        name: The name of the chunker.
        metadata: Additional metadata for the chunker.
        chunk_size: The maximum size of each chunk in characters.
        chunk_overlap: The number of characters to overlap between chunks.
        strategy: The chunking strategy to use.
    
    TODO(Issue #7): Add support for more programming languages
    TODO(Issue #7): Implement chunker validation
    """
    
    def __init__(
        self,
        name: str = "code_chunker",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        strategy: str = "function",
    ) -> None:
        """
        Initialize the code chunker.
        
        Args:
            name: The name of the chunker.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            strategy: The chunking strategy to use ("function", "class", "file", "fixed").
        """
        super().__init__(name)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        
        self.metadata["chunk_size"] = chunk_size
        self.metadata["chunk_overlap"] = chunk_overlap
        self.metadata["strategy"] = strategy
    
    def chunk(self, content: str, context_type: ContextType, **kwargs: Any) -> List[Context]:
        """
        Chunk code content into smaller contexts.
        
        Args:
            content: The code content to chunk.
            context_type: The type of context.
            **kwargs: Additional arguments for the chunker.
                chunk_size: Override the default chunk size.
                chunk_overlap: Override the default chunk overlap.
                strategy: Override the default chunking strategy.
                language: The programming language of the code.
                parent_id: ID of the parent context.
                source: Source of the content.
                tags: List of tags for the chunks.
            
        Returns:
            List of context chunks.
        """
        # Get chunking parameters
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        strategy = kwargs.get("strategy", self.strategy)
        language = kwargs.get("language", "python")
        parent_id = kwargs.get("parent_id")
        source = kwargs.get("source")
        tags = kwargs.get("tags", [])
        
        # Choose chunking strategy based on language
        if language == "python":
            if strategy == "function":
                chunks = self._chunk_python_by_function(content, chunk_size, chunk_overlap)
            elif strategy == "class":
                chunks = self._chunk_python_by_class(content, chunk_size, chunk_overlap)
            else:  # Default to fixed-size chunking
                chunks = self._chunk_fixed_size(content, chunk_size, chunk_overlap)
        else:
            # For unsupported languages, use fixed-size chunking
            chunks = self._chunk_fixed_size(content, chunk_size, chunk_overlap)
        
        # Create context objects for each chunk
        contexts = []
        for i, chunk in enumerate(chunks):
            context = Context(
                content=chunk,
                context_type=context_type,
                parent_id=parent_id,
                source=source,
                tags=tags.copy(),
                metadata={
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "chunker": self.name,
                    "strategy": strategy,
                    "language": language,
                }
            )
            contexts.append(context)
        
        return contexts
    
    def _chunk_python_by_function(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chunk Python code by functions.
        
        Args:
            content: The Python code to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            
        Returns:
            List of code chunks.
        """
        # Regular expression to match Python function definitions
        function_pattern = r'(def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:(?:\s*"""[\s\S]*?""")?\s*(?:#[^\n]*\n)*(?:[ \t]+[^\n]+\n)+)'
        
        # Find all function definitions
        functions = re.finditer(function_pattern, content, re.MULTILINE)
        
        # Extract function positions
        positions = []
        for match in functions:
            start, end = match.span()
            positions.append((start, end))
        
        # If no functions found, use fixed-size chunking
        if not positions:
            return self._chunk_fixed_size(content, chunk_size, chunk_overlap)
        
        # Create chunks based on function positions
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for start, end in positions:
            function_code = content[start:end]
            
            # If adding this function would exceed the chunk size, start a new chunk
            if len(current_chunk) + len(function_code) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Start new chunk with overlap
                if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                    current_chunk = current_chunk[-chunk_overlap:] + "\n" + function_code
                else:
                    current_chunk = function_code
            else:
                # Add function to current chunk
                if current_chunk:
                    current_chunk += "\n" + function_code
                else:
                    current_chunk = function_code
            
            current_start = end
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        # If there's code after the last function, add it as a separate chunk
        if current_start < len(content):
            remaining_code = content[current_start:]
            if len(remaining_code) <= chunk_size:
                chunks.append(remaining_code)
            else:
                # Use fixed-size chunking for the remaining code
                remaining_chunks = self._chunk_fixed_size(remaining_code, chunk_size, chunk_overlap)
                chunks.extend(remaining_chunks)
        
        return chunks
    
    def _chunk_python_by_class(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chunk Python code by classes.
        
        Args:
            content: The Python code to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            
        Returns:
            List of code chunks.
        """
        # Regular expression to match Python class definitions
        class_pattern = r'(class\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\([^)]*\))?\s*:(?:\s*"""[\s\S]*?""")?\s*(?:#[^\n]*\n)*(?:[ \t]+[^\n]+\n)+)'
        
        # Find all class definitions
        classes = re.finditer(class_pattern, content, re.MULTILINE)
        
        # Extract class positions
        positions = []
        for match in classes:
            start, end = match.span()
            positions.append((start, end))
        
        # If no classes found, use function-based chunking
        if not positions:
            return self._chunk_python_by_function(content, chunk_size, chunk_overlap)
        
        # Create chunks based on class positions
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for start, end in positions:
            class_code = content[start:end]
            
            # If adding this class would exceed the chunk size, start a new chunk
            if len(current_chunk) + len(class_code) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Start new chunk with overlap
                if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                    current_chunk = current_chunk[-chunk_overlap:] + "\n" + class_code
                else:
                    current_chunk = class_code
            else:
                # Add class to current chunk
                if current_chunk:
                    current_chunk += "\n" + class_code
                else:
                    current_chunk = class_code
            
            current_start = end
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        # If there's code after the last class, add it as a separate chunk
        if current_start < len(content):
            remaining_code = content[current_start:]
            if len(remaining_code) <= chunk_size:
                chunks.append(remaining_code)
            else:
                # Use function-based chunking for the remaining code
                remaining_chunks = self._chunk_python_by_function(remaining_code, chunk_size, chunk_overlap)
                chunks.extend(remaining_chunks)
        
        return chunks
    
    def _chunk_fixed_size(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Chunk code into fixed-size chunks.
        
        Args:
            content: The code content to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            
        Returns:
            List of code chunks.
        """
        chunks = []
        
        # If content is smaller than chunk size, return it as a single chunk
        if len(content) <= chunk_size:
            return [content]
        
        # Otherwise, create overlapping chunks
        start = 0
        while start < len(content):
            end = start + chunk_size
            
            # If this is not the first chunk, include overlap
            if start > 0:
                start = start - chunk_overlap
                end = start + chunk_size
            
            # If we've reached the end of the content, adjust the end
            if end > len(content):
                end = len(content)
            
            # Add the chunk
            chunks.append(content[start:end])
            
            # Move to the next chunk
            start = end
        
        return chunks


@tag("context.chunking.semantic")
class SemanticChunker(Chunker):
    """
    Chunker for semantic content.
    
    This class implements a chunker for semantic content, which breaks down
    content into smaller chunks based on semantic meaning.
    
    Attributes:
        name: The name of the chunker.
        metadata: Additional metadata for the chunker.
        chunk_size: The maximum size of each chunk in characters.
        chunk_overlap: The number of characters to overlap between chunks.
        embedding_model: The embedding model to use for semantic chunking.
    
    TODO(Issue #7): Add support for more embedding models
    TODO(Issue #7): Implement chunker validation
    """
    
    def __init__(
        self,
        name: str = "semantic_chunker",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: Optional[str] = None,
    ) -> None:
        """
        Initialize the semantic chunker.
        
        Args:
            name: The name of the chunker.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            embedding_model: The embedding model to use for semantic chunking.
        """
        super().__init__(name)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        
        self.metadata["chunk_size"] = chunk_size
        self.metadata["chunk_overlap"] = chunk_overlap
        self.metadata["embedding_model"] = embedding_model
    
    def chunk(self, content: str, context_type: ContextType, **kwargs: Any) -> List[Context]:
        """
        Chunk content into smaller contexts based on semantic meaning.
        
        Args:
            content: The content to chunk.
            context_type: The type of context.
            **kwargs: Additional arguments for the chunker.
                chunk_size: Override the default chunk size.
                chunk_overlap: Override the default chunk overlap.
                embedding_model: Override the default embedding model.
                parent_id: ID of the parent context.
                source: Source of the content.
                tags: List of tags for the chunks.
            
        Returns:
            List of context chunks.
        """
        # Get chunking parameters
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        embedding_model = kwargs.get("embedding_model", self.embedding_model)
        parent_id = kwargs.get("parent_id")
        source = kwargs.get("source")
        tags = kwargs.get("tags", [])
        
        # If no embedding model is specified, use a fallback chunker
        if embedding_model is None:
            if context_type == ContextType.CODE:
                chunker = CodeChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            else:
                chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            return chunker.chunk(content, context_type, **kwargs)
        
        # Otherwise, use semantic chunking
        chunks = self._chunk_semantic(content, chunk_size, chunk_overlap, embedding_model)
        
        # Create context objects for each chunk
        contexts = []
        for i, chunk in enumerate(chunks):
            context = Context(
                content=chunk,
                context_type=context_type,
                parent_id=parent_id,
                source=source,
                tags=tags.copy(),
                metadata={
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "chunker": self.name,
                    "embedding_model": embedding_model,
                }
            )
            contexts.append(context)
        
        return contexts
    
    def _chunk_semantic(self, content: str, chunk_size: int, chunk_overlap: int, embedding_model: str) -> List[str]:
        """
        Chunk content based on semantic meaning.
        
        Args:
            content: The content to chunk.
            chunk_size: The maximum size of each chunk in characters.
            chunk_overlap: The number of characters to overlap between chunks.
            embedding_model: The embedding model to use for semantic chunking.
            
        Returns:
            List of content chunks.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use an embedding model to identify
        # semantic boundaries and create chunks accordingly
        
        # For now, use a fallback chunker
        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return chunker._chunk_by_paragraph(content, chunk_size, chunk_overlap)
