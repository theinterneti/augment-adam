"""Context Composer for the Context Engine.

This module provides a composer for combining context items into a
coherent context window.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextItem, ContextWindow

logger = logging.getLogger(__name__)


class ContextComposer:
    """Context Composer for the Context Engine.
    
    This class composes context items into a coherent context window.
    
    Attributes:
        relevance_threshold: The minimum relevance score for items to be included
        max_items: The maximum number of items to include
        sort_by_relevance: Whether to sort items by relevance
    """
    
    def __init__(
        self,
        relevance_threshold: float = 0.5,
        max_items: int = 20,
        sort_by_relevance: bool = True
    ):
        """Initialize the Context Composer.
        
        Args:
            relevance_threshold: The minimum relevance score for items to be included
            max_items: The maximum number of items to include
            sort_by_relevance: Whether to sort items by relevance
        """
        self.relevance_threshold = relevance_threshold
        self.max_items = max_items
        self.sort_by_relevance = sort_by_relevance
        
        logger.info("Context Composer initialized")
    
    def compose(
        self,
        query: str,
        items: List[ContextItem],
        window: ContextWindow
    ) -> ContextWindow:
        """Compose context items into a context window.
        
        Args:
            query: The query to compose context for
            items: The context items to compose
            window: The context window to compose into
            
        Returns:
            The composed context window
        """
        try:
            # Clear the window
            window.clear()
            
            # Filter items by relevance
            filtered_items = [
                item for item in items
                if item.relevance >= self.relevance_threshold
            ]
            
            # Sort by relevance if needed
            if self.sort_by_relevance:
                filtered_items.sort(key=lambda item: item.relevance, reverse=True)
            
            # Limit to max_items
            filtered_items = filtered_items[:self.max_items]
            
            # Add items to window
            for item in filtered_items:
                if not window.add_item(item):
                    # Window is full
                    break
            
            logger.info(f"Composed context window with {len(window.items)} items for query: {query}")
            return window
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to compose context",
                category=ErrorCategory.RESOURCE,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return window
