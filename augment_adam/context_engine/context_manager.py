"""Context Manager for the Augment Adam assistant.

This module provides the core Context Manager for orchestrating context
retrieval, composition, and optimization.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field

from augment_adam.core.errors import (
    ResourceError, ValidationError, wrap_error, log_error, ErrorCategory
)
from augment_adam.core.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """A single item of context.
    
    Attributes:
        content: The content of the context item
        source: The source of the context item
        relevance: The relevance score of the context item
        metadata: Additional metadata for the context item
        token_count: The number of tokens in the context item
    """
    
    content: str
    source: str
    relevance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0


@dataclass
class ContextWindow:
    """A context window containing multiple context items.
    
    Attributes:
        items: The context items in the window
        max_tokens: The maximum number of tokens allowed in the window
        current_tokens: The current number of tokens in the window
        metadata: Additional metadata for the context window
    """
    
    items: List[ContextItem] = field(default_factory=list)
    max_tokens: int = 4096
    current_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_item(self, item: ContextItem) -> bool:
        """Add a context item to the window.
        
        Args:
            item: The context item to add
            
        Returns:
            True if the item was added, False if it would exceed the token limit
        """
        if self.current_tokens + item.token_count > self.max_tokens:
            return False
        
        self.items.append(item)
        self.current_tokens += item.token_count
        return True
    
    def remove_item(self, index: int) -> Optional[ContextItem]:
        """Remove a context item from the window.
        
        Args:
            index: The index of the item to remove
            
        Returns:
            The removed item, or None if the index is invalid
        """
        if 0 <= index < len(self.items):
            item = self.items.pop(index)
            self.current_tokens -= item.token_count
            return item
        return None
    
    def clear(self) -> None:
        """Clear all items from the window."""
        self.items.clear()
        self.current_tokens = 0
    
    def get_content(self) -> str:
        """Get the combined content of all items in the window.
        
        Returns:
            The combined content
        """
        return "\n\n".join(item.content for item in self.items)
    
    def get_available_tokens(self) -> int:
        """Get the number of tokens available in the window.
        
        Returns:
            The number of available tokens
        """
        return self.max_tokens - self.current_tokens


class ContextManager:
    """Context Manager for the Augment Adam assistant.
    
    This class orchestrates context retrieval, composition, and optimization.
    It manages context windows and ensures efficient use of token budgets.
    
    Attributes:
        retrievers: Dictionary of retrievers for different sources
        composers: Dictionary of composers for different types of composition
        chunkers: Dictionary of chunkers for different types of content
        prompt_composers: Dictionary of prompt composers for different types of prompts
        context_windows: Dictionary of context windows for different purposes
    """
    
    def __init__(self):
        """Initialize the Context Manager."""
        self.retrievers = {}
        self.composers = {}
        self.chunkers = {}
        self.prompt_composers = {}
        self.context_windows = {}
        
        # Initialize default context window
        self.context_windows["default"] = ContextWindow()
        
        logger.info("Context Manager initialized")
    
    def register_retriever(self, name: str, retriever: Any) -> None:
        """Register a retriever.
        
        Args:
            name: The name of the retriever
            retriever: The retriever instance
        """
        self.retrievers[name] = retriever
        logger.info(f"Registered retriever: {name}")
    
    def register_composer(self, name: str, composer: Any) -> None:
        """Register a composer.
        
        Args:
            name: The name of the composer
            composer: The composer instance
        """
        self.composers[name] = composer
        logger.info(f"Registered composer: {name}")
    
    def register_chunker(self, name: str, chunker: Any) -> None:
        """Register a chunker.
        
        Args:
            name: The name of the chunker
            chunker: The chunker instance
        """
        self.chunkers[name] = chunker
        logger.info(f"Registered chunker: {name}")
    
    def register_prompt_composer(self, name: str, prompt_composer: Any) -> None:
        """Register a prompt composer.
        
        Args:
            name: The name of the prompt composer
            prompt_composer: The prompt composer instance
        """
        self.prompt_composers[name] = prompt_composer
        logger.info(f"Registered prompt composer: {name}")
    
    def create_context_window(self, name: str, max_tokens: int = 4096) -> ContextWindow:
        """Create a new context window.
        
        Args:
            name: The name of the context window
            max_tokens: The maximum number of tokens allowed in the window
            
        Returns:
            The created context window
        """
        window = ContextWindow(max_tokens=max_tokens)
        self.context_windows[name] = window
        logger.info(f"Created context window: {name} with {max_tokens} max tokens")
        return window
    
    def get_context_window(self, name: str = "default") -> Optional[ContextWindow]:
        """Get a context window by name.
        
        Args:
            name: The name of the context window
            
        Returns:
            The context window, or None if not found
        """
        return self.context_windows.get(name)
    
    def retrieve(
        self,
        query: str,
        sources: List[str] = None,
        max_items: int = 10,
        window_name: str = "default"
    ) -> List[ContextItem]:
        """Retrieve context items from various sources.
        
        Args:
            query: The query to retrieve context for
            sources: The sources to retrieve from (if None, use all registered retrievers)
            max_items: The maximum number of items to retrieve
            window_name: The name of the context window to use
            
        Returns:
            The retrieved context items
        """
        if sources is None:
            sources = list(self.retrievers.keys())
        
        items = []
        for source in sources:
            retriever = self.retrievers.get(source)
            if retriever is None:
                logger.warning(f"Retriever not found: {source}")
                continue
            
            try:
                source_items = retriever.retrieve(query, max_items=max_items)
                items.extend(source_items)
            except Exception as e:
                error = wrap_error(
                    e,
                    message=f"Error retrieving from {source}",
                    category=ErrorCategory.RESOURCE,
                    details={"source": source, "query": query},
                )
                log_error(error, logger=logger)
        
        # Sort by relevance
        items.sort(key=lambda item: item.relevance, reverse=True)
        
        # Limit to max_items
        items = items[:max_items]
        
        return items
    
    def compose_context(
        self,
        query: str,
        items: List[ContextItem],
        composer_name: str = "default",
        window_name: str = "default"
    ) -> ContextWindow:
        """Compose a context window from context items.
        
        Args:
            query: The query to compose context for
            items: The context items to compose
            composer_name: The name of the composer to use
            window_name: The name of the context window to use
            
        Returns:
            The composed context window
        """
        window = self.get_context_window(window_name)
        if window is None:
            window = self.create_context_window(window_name)
        
        composer = self.composers.get(composer_name)
        if composer is None:
            logger.warning(f"Composer not found: {composer_name}")
            # Fall back to simple composition
            for item in items:
                window.add_item(item)
            return window
        
        try:
            return composer.compose(query, items, window)
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Error composing context with {composer_name}",
                category=ErrorCategory.RESOURCE,
                details={"composer": composer_name, "query": query},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple composition
            for item in items:
                window.add_item(item)
            return window
    
    def optimize_context(
        self,
        window: ContextWindow,
        optimizer_name: str = "default",
        target_tokens: Optional[int] = None
    ) -> ContextWindow:
        """Optimize a context window for token efficiency.
        
        Args:
            window: The context window to optimize
            optimizer_name: The name of the optimizer to use
            target_tokens: The target number of tokens (if None, use window.max_tokens)
            
        Returns:
            The optimized context window
        """
        optimizer = self.composers.get(optimizer_name)
        if optimizer is None:
            logger.warning(f"Optimizer not found: {optimizer_name}")
            return window
        
        try:
            return optimizer.optimize(window, target_tokens)
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Error optimizing context with {optimizer_name}",
                category=ErrorCategory.RESOURCE,
                details={"optimizer": optimizer_name},
            )
            log_error(error, logger=logger)
            return window
    
    def create_prompt(
        self,
        query: str,
        window: ContextWindow,
        prompt_type: str = "default"
    ) -> str:
        """Create a prompt with context.
        
        Args:
            query: The query to create a prompt for
            window: The context window to use
            prompt_type: The type of prompt to create
            
        Returns:
            The created prompt
        """
        composer = self.prompt_composers.get(prompt_type)
        if composer is None:
            logger.warning(f"Prompt composer not found: {prompt_type}")
            # Fall back to simple prompt
            return f"Context:\n{window.get_content()}\n\nQuery: {query}"
        
        try:
            return composer.compose(query, window)
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Error creating prompt with {prompt_type}",
                category=ErrorCategory.RESOURCE,
                details={"prompt_type": prompt_type, "query": query},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple prompt
            return f"Context:\n{window.get_content()}\n\nQuery: {query}"
    
    def process_query(
        self,
        query: str,
        sources: List[str] = None,
        max_items: int = 10,
        composer_name: str = "default",
        optimizer_name: str = "default",
        prompt_type: str = "default",
        window_name: str = "default"
    ) -> str:
        """Process a query end-to-end.
        
        This method retrieves context, composes it, optimizes it, and creates a prompt.
        
        Args:
            query: The query to process
            sources: The sources to retrieve from
            max_items: The maximum number of items to retrieve
            composer_name: The name of the composer to use
            optimizer_name: The name of the optimizer to use
            prompt_type: The type of prompt to create
            window_name: The name of the context window to use
            
        Returns:
            The created prompt
        """
        # Retrieve context
        items = self.retrieve(query, sources, max_items, window_name)
        
        # Compose context
        window = self.compose_context(query, items, composer_name, window_name)
        
        # Optimize context
        window = self.optimize_context(window, optimizer_name)
        
        # Create prompt
        prompt = self.create_prompt(query, window, prompt_type)
        
        return prompt


# Global instance for singleton pattern
_context_manager = None


def get_context_manager() -> ContextManager:
    """Get the global Context Manager instance.
    
    Returns:
        The global Context Manager instance
    """
    global _context_manager
    
    if _context_manager is None:
        _context_manager = ContextManager()
    
    return _context_manager
