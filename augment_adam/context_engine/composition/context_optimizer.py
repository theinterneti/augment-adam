"""Context Optimizer for the Context Engine.

This module provides an optimizer for maximizing information density
in context windows.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextItem, ContextWindow
from augment_adam.context_engine.chunking.summarizer import Summarizer

logger = logging.getLogger(__name__)


class ContextOptimizer:
    """Context Optimizer for the Context Engine.
    
    This class optimizes context windows for maximum information density.
    
    Attributes:
        summarizer: The summarizer to use for condensing content
        token_budget_ratio: The ratio of tokens to allocate to different relevance levels
        min_relevance: The minimum relevance score for items to be included
    """
    
    def __init__(
        self,
        summarizer: Optional[Summarizer] = None,
        token_budget_ratio: Dict[str, float] = None,
        min_relevance: float = 0.3
    ):
        """Initialize the Context Optimizer.
        
        Args:
            summarizer: The summarizer to use for condensing content
            token_budget_ratio: The ratio of tokens to allocate to different relevance levels
            min_relevance: The minimum relevance score for items to be included
        """
        self.summarizer = summarizer or Summarizer()
        
        # Default token budget ratio: 60% high relevance, 30% medium, 10% low
        self.token_budget_ratio = token_budget_ratio or {
            "high": 0.6,
            "medium": 0.3,
            "low": 0.1
        }
        
        self.min_relevance = min_relevance
        
        logger.info("Context Optimizer initialized")
    
    def optimize(
        self,
        window: ContextWindow,
        target_tokens: Optional[int] = None
    ) -> ContextWindow:
        """Optimize a context window for token efficiency.
        
        Args:
            window: The context window to optimize
            target_tokens: The target number of tokens (if None, use window.max_tokens)
            
        Returns:
            The optimized context window
        """
        try:
            if not window.items:
                return window
            
            # Use window.max_tokens if target_tokens is not specified
            target_tokens = target_tokens or window.max_tokens
            
            # If current tokens are already below target, no optimization needed
            if window.current_tokens <= target_tokens:
                return window
            
            # Categorize items by relevance
            high_relevance = []
            medium_relevance = []
            low_relevance = []
            
            for item in window.items:
                if item.relevance >= 0.7:
                    high_relevance.append(item)
                elif item.relevance >= 0.5:
                    medium_relevance.append(item)
                elif item.relevance >= self.min_relevance:
                    low_relevance.append(item)
            
            # Calculate token budgets
            high_budget = int(target_tokens * self.token_budget_ratio["high"])
            medium_budget = int(target_tokens * self.token_budget_ratio["medium"])
            low_budget = int(target_tokens * self.token_budget_ratio["low"])
            
            # Adjust budgets if some categories are empty
            if not high_relevance:
                medium_budget += high_budget // 2
                low_budget += high_budget // 2
                high_budget = 0
            
            if not medium_relevance:
                high_budget += medium_budget // 2
                low_budget += medium_budget // 2
                medium_budget = 0
            
            if not low_relevance:
                high_budget += low_budget // 2
                medium_budget += low_budget // 2
                low_budget = 0
            
            # Optimize each category
            optimized_high = self._optimize_category(high_relevance, high_budget)
            optimized_medium = self._optimize_category(medium_relevance, medium_budget)
            optimized_low = self._optimize_category(low_relevance, low_budget)
            
            # Create a new window with optimized items
            optimized_window = ContextWindow(max_tokens=window.max_tokens)
            
            # Add items in order of relevance
            for item in optimized_high + optimized_medium + optimized_low:
                optimized_window.add_item(item)
            
            logger.info(
                f"Optimized context window from {window.current_tokens} tokens to "
                f"{optimized_window.current_tokens} tokens"
            )
            
            return optimized_window
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to optimize context",
                category=ErrorCategory.RESOURCE,
                details={
                    "current_tokens": window.current_tokens,
                    "target_tokens": target_tokens,
                },
            )
            log_error(error, logger=logger)
            return window
    
    def _optimize_category(
        self,
        items: List[ContextItem],
        token_budget: int
    ) -> List[ContextItem]:
        """Optimize a category of items to fit within a token budget.
        
        Args:
            items: The items to optimize
            token_budget: The token budget for this category
            
        Returns:
            The optimized items
        """
        if not items:
            return []
        
        # Sort by relevance
        items.sort(key=lambda item: item.relevance, reverse=True)
        
        # Calculate current tokens
        current_tokens = sum(item.token_count for item in items)
        
        # If already within budget, return as is
        if current_tokens <= token_budget:
            return items
        
        # If we need to reduce tokens
        optimized_items = []
        remaining_budget = token_budget
        
        for item in items:
            # If this item fits in the budget, add it as is
            if item.token_count <= remaining_budget:
                optimized_items.append(item)
                remaining_budget -= item.token_count
            else:
                # Try to summarize the item to fit
                detail_level = "medium"
                if item.relevance >= 0.8:
                    detail_level = "high"
                elif item.relevance < 0.5:
                    detail_level = "low"
                
                # Summarize content
                summarized_content = self.summarizer.summarize(
                    item.content,
                    target_length=remaining_budget,
                    detail_level=detail_level
                )
                
                # Estimate token count
                token_count = len(summarized_content.split()) * 1.3  # Rough approximation
                
                # Create new item with summarized content
                summarized_item = ContextItem(
                    content=summarized_content,
                    source=item.source,
                    relevance=item.relevance,
                    metadata=item.metadata.copy(),
                    token_count=int(token_count)
                )
                
                # Add metadata to indicate summarization
                summarized_item.metadata["summarized"] = True
                summarized_item.metadata["original_length"] = item.token_count
                
                # Add to optimized items
                optimized_items.append(summarized_item)
                remaining_budget -= summarized_item.token_count
            
            # If budget is exhausted, stop
            if remaining_budget <= 0:
                break
        
        return optimized_items
