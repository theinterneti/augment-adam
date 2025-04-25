"""Document Retriever for the Context Engine.

This module provides a retriever for fetching relevant information from
documents.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextItem
from augment_adam.context_engine.chunking.intelligent_chunker import IntelligentChunker

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Document Retriever for the Context Engine.
    
    This class retrieves relevant information from documents.
    
    Attributes:
        document_dir: Directory containing documents
        chunker: Chunker for splitting documents into manageable chunks
        default_relevance: The default relevance score for retrieved items
        supported_extensions: List of supported file extensions
    """
    
    def __init__(
        self,
        document_dir: Optional[str] = None,
        chunker: Optional[IntelligentChunker] = None,
        default_relevance: float = 0.5
    ):
        """Initialize the Document Retriever.
        
        Args:
            document_dir: Directory containing documents
            chunker: Chunker for splitting documents into manageable chunks
            default_relevance: The default relevance score for retrieved items
        """
        self.document_dir = document_dir
        self.chunker = chunker or IntelligentChunker()
        self.default_relevance = default_relevance
        self.supported_extensions = [".txt", ".md", ".csv", ".json"]
        
        logger.info("Document Retriever initialized")
    
    def retrieve(
        self,
        query: str,
        max_items: int = 10,
        file_pattern: Optional[str] = None
    ) -> List[ContextItem]:
        """Retrieve context items from documents.
        
        Args:
            query: The query to retrieve context for
            max_items: The maximum number of items to retrieve
            file_pattern: Pattern to filter files by name
            
        Returns:
            The retrieved context items
        """
        try:
            if not self.document_dir:
                logger.warning("Document directory not provided")
                return []
            
            # Get list of documents
            documents = self._get_documents(file_pattern)
            
            # Extract content from documents
            items = []
            for doc_path in documents:
                # Read document
                content = self._read_document(doc_path)
                if not content:
                    continue
                
                # Chunk content
                chunks = self.chunker.chunk(content)
                
                # Create context items from chunks
                for i, chunk in enumerate(chunks):
                    # Estimate token count (very rough approximation)
                    token_count = len(chunk.split()) * 1.3  # Rough approximation
                    
                    item = ContextItem(
                        content=chunk,
                        source=f"document:{doc_path.name}",
                        relevance=self.default_relevance,
                        metadata={
                            "document": str(doc_path),
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                        },
                        token_count=int(token_count)
                    )
                    items.append(item)
                    
                    # Stop if we've reached max_items
                    if len(items) >= max_items:
                        break
                
                # Stop if we've reached max_items
                if len(items) >= max_items:
                    break
            
            logger.info(f"Retrieved {len(items)} items from documents for query: {query}")
            return items
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to retrieve from documents",
                category=ErrorCategory.RESOURCE,
                details={
                    "query": query,
                    "document_dir": self.document_dir,
                },
            )
            log_error(error, logger=logger)
            return []
    
    def _get_documents(self, file_pattern: Optional[str] = None) -> List[Path]:
        """Get list of documents.
        
        Args:
            file_pattern: Pattern to filter files by name
            
        Returns:
            List of document paths
        """
        if not self.document_dir:
            return []
        
        document_dir = Path(self.document_dir)
        if not document_dir.exists() or not document_dir.is_dir():
            logger.warning(f"Document directory not found: {self.document_dir}")
            return []
        
        # Get all files with supported extensions
        documents = []
        for ext in self.supported_extensions:
            documents.extend(document_dir.glob(f"*{ext}"))
        
        # Filter by pattern if provided
        if file_pattern:
            documents = [doc for doc in documents if file_pattern in doc.name]
        
        return documents
    
    def _read_document(self, doc_path: Path) -> Optional[str]:
        """Read a document.
        
        Args:
            doc_path: Path to the document
            
        Returns:
            The document content, or None if the read failed
        """
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            logger.warning(f"Failed to read document {doc_path}: {e}")
            return None
