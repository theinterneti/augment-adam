"""Memory Retriever for the Context Engine.

This module provides a retriever for fetching relevant information from
memory systems.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.memory import create_memory, get_default_memory
from augment_adam.context_engine.context_manager import ContextItem

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """Memory Retriever for the Context Engine.
    
    This class retrieves relevant information from memory systems.
    
    Attributes:
        memory: The memory system to retrieve from
        collection_name: The name of the memory collection to use
        default_relevance: The default relevance score for retrieved items
    """
    
    def __init__(
        self,
        memory_type: str = None,
        collection_name: str = None,
        default_relevance: float = 0.7
    ):
        """Initialize the Memory Retriever.
        
        Args:
            memory_type: The type of memory system to use (if None, use default)
            collection_name: The name of the memory collection to use
            default_relevance: The default relevance score for retrieved items
        """
        try:
            if memory_type:
                self.memory = create_memory(memory_type)
            else:
                self.memory = get_default_memory()
            
            self.collection_name = collection_name
            self.default_relevance = default_relevance
            
            logger.info(f"Memory Retriever initialized with {memory_type or 'default'} memory")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to initialize Memory Retriever",
                category=ErrorCategory.RESOURCE,
                details={
                    "memory_type": memory_type,
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            raise error
    
    def retrieve(
        self,
        query: str,
        max_items: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ContextItem]:
        """Retrieve context items from memory.
        
        Args:
            query: The query to retrieve context for
            max_items: The maximum number of items to retrieve
            filter_metadata: Filter to apply to the metadata
            
        Returns:
            The retrieved context items
        """
        try:
            # Retrieve from memory
            results = self.memory.retrieve(
                query=query,
                n_results=max_items,
                filter_metadata=filter_metadata,
                collection_name=self.collection_name
            )
            
            # Convert to context items
            items = []
            for memory_item, similarity in results:
                # Estimate token count (very rough approximation)
                text = memory_item.get("text", "")
                token_count = len(text.split()) * 1.3  # Rough approximation
                
                item = ContextItem(
                    content=text,
                    source="memory",
                    relevance=similarity,
                    metadata=memory_item,
                    token_count=int(token_count)
                )
                items.append(item)
            
            logger.info(f"Retrieved {len(items)} items from memory for query: {query}")
            return items
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to retrieve from memory",
                category=ErrorCategory.RESOURCE,
                details={
                    "query": query,
                    "collection_name": self.collection_name,
                },
            )
            log_error(error, logger=logger)
            return []
