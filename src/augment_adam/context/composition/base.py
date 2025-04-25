"""
Base classes for the composition module.

This module provides the base classes for the composition module, including
the ContextComposer base class and various composer implementations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.context.core.base import Context, ContextType


@tag("context.composition")
class ContextComposer(ABC):
    """
    Base class for context composers.
    
    This class defines the interface for context composers, which combine
    multiple contexts into a single coherent context.
    
    Attributes:
        name: The name of the composer.
        metadata: Additional metadata for the composer.
    
    TODO(Issue #7): Add support for composer validation
    TODO(Issue #7): Implement composer analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the composer.
        
        Args:
            name: The name of the composer.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def compose(self, contexts: List[Context], **kwargs: Any) -> Context:
        """
        Compose multiple contexts into a single context.
        
        Args:
            contexts: The contexts to compose.
            **kwargs: Additional arguments for the composer.
            
        Returns:
            Composed context.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the composer.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the composer.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("context.composition.sequential")
class SequentialComposer(ContextComposer):
    """
    Composer for sequential composition of contexts.
    
    This class implements a composer that combines contexts in sequential order,
    with optional separators and headers.
    
    Attributes:
        name: The name of the composer.
        metadata: Additional metadata for the composer.
        separator: The separator to use between contexts.
        header_template: The template to use for context headers.
        footer_template: The template to use for context footers.
        include_metadata: Whether to include metadata in the composed context.
    
    TODO(Issue #7): Add support for more composition strategies
    TODO(Issue #7): Implement composer validation
    """
    
    def __init__(
        self,
        name: str = "sequential_composer",
        separator: str = "\n\n",
        header_template: Optional[str] = None,
        footer_template: Optional[str] = None,
        include_metadata: bool = False,
    ) -> None:
        """
        Initialize the sequential composer.
        
        Args:
            name: The name of the composer.
            separator: The separator to use between contexts.
            header_template: The template to use for context headers.
            footer_template: The template to use for context footers.
            include_metadata: Whether to include metadata in the composed context.
        """
        super().__init__(name)
        
        self.separator = separator
        self.header_template = header_template
        self.footer_template = footer_template
        self.include_metadata = include_metadata
        
        self.metadata["separator"] = separator
        self.metadata["header_template"] = header_template
        self.metadata["footer_template"] = footer_template
        self.metadata["include_metadata"] = include_metadata
    
    def compose(self, contexts: List[Context], **kwargs: Any) -> Context:
        """
        Compose multiple contexts into a single context in sequential order.
        
        Args:
            contexts: The contexts to compose.
            **kwargs: Additional arguments for the composer.
                separator: Override the default separator.
                header_template: Override the default header template.
                footer_template: Override the default footer template.
                include_metadata: Override whether to include metadata.
                context_type: The type of the composed context.
                source: Source of the composed context.
                tags: List of tags for the composed context.
            
        Returns:
            Composed context.
        """
        if not contexts:
            return Context(content="", context_type=ContextType.TEXT)
        
        # Get composition parameters
        separator = kwargs.get("separator", self.separator)
        header_template = kwargs.get("header_template", self.header_template)
        footer_template = kwargs.get("footer_template", self.footer_template)
        include_metadata = kwargs.get("include_metadata", self.include_metadata)
        context_type = kwargs.get("context_type", contexts[0].context_type)
        source = kwargs.get("source")
        tags = kwargs.get("tags", [])
        
        # Compose contexts
        composed_content = []
        chunk_ids = []
        total_tokens = 0
        
        for i, context in enumerate(contexts):
            # Add header if template is provided
            if header_template is not None:
                header = header_template.format(
                    index=i,
                    count=len(contexts),
                    id=context.id,
                    type=context.context_type.name,
                    source=context.source or "",
                    **context.metadata
                )
                composed_content.append(header)
            
            # Add context content
            composed_content.append(context.content)
            
            # Add footer if template is provided
            if footer_template is not None:
                footer = footer_template.format(
                    index=i,
                    count=len(contexts),
                    id=context.id,
                    type=context.context_type.name,
                    source=context.source or "",
                    **context.metadata
                )
                composed_content.append(footer)
            
            # Add separator if this is not the last context
            if i < len(contexts) - 1:
                composed_content.append(separator)
            
            # Add chunk ID
            chunk_ids.append(context.id)
            
            # Add tokens
            total_tokens += context.tokens
        
        # Create metadata for the composed context
        composed_metadata = {
            "composer": self.name,
            "context_count": len(contexts),
            "original_tokens": total_tokens,
        }
        
        # Include metadata from original contexts if requested
        if include_metadata:
            for i, context in enumerate(contexts):
                for key, value in context.metadata.items():
                    composed_metadata[f"context_{i}_{key}"] = value
        
        # Create the composed context
        composed_context = Context(
            content=separator.join(composed_content),
            context_type=context_type,
            metadata=composed_metadata,
            chunks=chunk_ids,
            source=source,
            tags=tags,
        )
        
        return composed_context


@tag("context.composition.hierarchical")
class HierarchicalComposer(ContextComposer):
    """
    Composer for hierarchical composition of contexts.
    
    This class implements a composer that combines contexts in a hierarchical
    structure, with parent-child relationships.
    
    Attributes:
        name: The name of the composer.
        metadata: Additional metadata for the composer.
        max_depth: The maximum depth of the hierarchy.
        indent_string: The string to use for indentation.
        include_metadata: Whether to include metadata in the composed context.
    
    TODO(Issue #7): Add support for more composition strategies
    TODO(Issue #7): Implement composer validation
    """
    
    def __init__(
        self,
        name: str = "hierarchical_composer",
        max_depth: int = 3,
        indent_string: str = "  ",
        include_metadata: bool = False,
    ) -> None:
        """
        Initialize the hierarchical composer.
        
        Args:
            name: The name of the composer.
            max_depth: The maximum depth of the hierarchy.
            indent_string: The string to use for indentation.
            include_metadata: Whether to include metadata in the composed context.
        """
        super().__init__(name)
        
        self.max_depth = max_depth
        self.indent_string = indent_string
        self.include_metadata = include_metadata
        
        self.metadata["max_depth"] = max_depth
        self.metadata["indent_string"] = indent_string
        self.metadata["include_metadata"] = include_metadata
    
    def compose(self, contexts: List[Context], **kwargs: Any) -> Context:
        """
        Compose multiple contexts into a single context in a hierarchical structure.
        
        Args:
            contexts: The contexts to compose.
            **kwargs: Additional arguments for the composer.
                max_depth: Override the default maximum depth.
                indent_string: Override the default indent string.
                include_metadata: Override whether to include metadata.
                context_type: The type of the composed context.
                source: Source of the composed context.
                tags: List of tags for the composed context.
            
        Returns:
            Composed context.
        """
        if not contexts:
            return Context(content="", context_type=ContextType.TEXT)
        
        # Get composition parameters
        max_depth = kwargs.get("max_depth", self.max_depth)
        indent_string = kwargs.get("indent_string", self.indent_string)
        include_metadata = kwargs.get("include_metadata", self.include_metadata)
        context_type = kwargs.get("context_type", contexts[0].context_type)
        source = kwargs.get("source")
        tags = kwargs.get("tags", [])
        
        # Build a hierarchy of contexts
        hierarchy = self._build_hierarchy(contexts)
        
        # Compose contexts
        composed_content = self._compose_hierarchy(hierarchy, 0, max_depth, indent_string)
        chunk_ids = [context.id for context in contexts]
        total_tokens = sum(context.tokens for context in contexts)
        
        # Create metadata for the composed context
        composed_metadata = {
            "composer": self.name,
            "context_count": len(contexts),
            "original_tokens": total_tokens,
            "max_depth": max_depth,
        }
        
        # Include metadata from original contexts if requested
        if include_metadata:
            for i, context in enumerate(contexts):
                for key, value in context.metadata.items():
                    composed_metadata[f"context_{i}_{key}"] = value
        
        # Create the composed context
        composed_context = Context(
            content=composed_content,
            context_type=context_type,
            metadata=composed_metadata,
            chunks=chunk_ids,
            source=source,
            tags=tags,
        )
        
        return composed_context
    
    def _build_hierarchy(self, contexts: List[Context]) -> Dict[Optional[str], List[Context]]:
        """
        Build a hierarchy of contexts based on parent-child relationships.
        
        Args:
            contexts: The contexts to organize into a hierarchy.
            
        Returns:
            Dictionary mapping parent IDs to lists of child contexts.
        """
        hierarchy: Dict[Optional[str], List[Context]] = {None: []}
        
        # First pass: organize contexts by parent ID
        for context in contexts:
            parent_id = context.parent_id
            if parent_id not in hierarchy:
                hierarchy[parent_id] = []
            hierarchy[parent_id].append(context)
        
        # Second pass: for contexts with parent IDs that don't exist in the list,
        # move them to the root level
        for parent_id in list(hierarchy.keys()):
            if parent_id is not None and parent_id not in [context.id for context in contexts]:
                if parent_id in hierarchy:
                    hierarchy[None].extend(hierarchy[parent_id])
                    del hierarchy[parent_id]
        
        return hierarchy
    
    def _compose_hierarchy(self, hierarchy: Dict[Optional[str], List[Context]], depth: int, max_depth: int, indent_string: str) -> str:
        """
        Recursively compose a hierarchy of contexts.
        
        Args:
            hierarchy: Dictionary mapping parent IDs to lists of child contexts.
            depth: Current depth in the hierarchy.
            max_depth: Maximum depth to traverse.
            indent_string: String to use for indentation.
            
        Returns:
            Composed content.
        """
        if depth > max_depth:
            return ""
        
        # Start with root contexts
        composed_parts = []
        
        for context in hierarchy.get(None, []):
            # Add context content with appropriate indentation
            indentation = indent_string * depth
            content_lines = context.content.split("\n")
            indented_content = "\n".join(indentation + line for line in content_lines)
            composed_parts.append(indented_content)
            
            # Add child contexts if any
            if context.id in hierarchy:
                child_content = self._compose_hierarchy(hierarchy, depth + 1, max_depth, indent_string)
                if child_content:
                    composed_parts.append(child_content)
        
        return "\n\n".join(composed_parts)


@tag("context.composition.semantic")
class SemanticComposer(ContextComposer):
    """
    Composer for semantic composition of contexts.
    
    This class implements a composer that combines contexts based on semantic
    similarity and relevance.
    
    Attributes:
        name: The name of the composer.
        metadata: Additional metadata for the composer.
        embedding_model: The embedding model to use for semantic composition.
        include_metadata: Whether to include metadata in the composed context.
    
    TODO(Issue #7): Add support for more embedding models
    TODO(Issue #7): Implement composer validation
    """
    
    def __init__(
        self,
        name: str = "semantic_composer",
        embedding_model: Optional[str] = None,
        include_metadata: bool = False,
    ) -> None:
        """
        Initialize the semantic composer.
        
        Args:
            name: The name of the composer.
            embedding_model: The embedding model to use for semantic composition.
            include_metadata: Whether to include metadata in the composed context.
        """
        super().__init__(name)
        
        self.embedding_model = embedding_model
        self.include_metadata = include_metadata
        
        self.metadata["embedding_model"] = embedding_model
        self.metadata["include_metadata"] = include_metadata
    
    def compose(self, contexts: List[Context], **kwargs: Any) -> Context:
        """
        Compose multiple contexts into a single context based on semantic similarity.
        
        Args:
            contexts: The contexts to compose.
            **kwargs: Additional arguments for the composer.
                embedding_model: Override the default embedding model.
                include_metadata: Override whether to include metadata.
                query: The query to use for relevance ranking.
                context_type: The type of the composed context.
                source: Source of the composed context.
                tags: List of tags for the composed context.
            
        Returns:
            Composed context.
        """
        if not contexts:
            return Context(content="", context_type=ContextType.TEXT)
        
        # Get composition parameters
        embedding_model = kwargs.get("embedding_model", self.embedding_model)
        include_metadata = kwargs.get("include_metadata", self.include_metadata)
        query = kwargs.get("query")
        context_type = kwargs.get("context_type", contexts[0].context_type)
        source = kwargs.get("source")
        tags = kwargs.get("tags", [])
        
        # If no embedding model or query is specified, use a fallback composer
        if embedding_model is None or query is None:
            composer = SequentialComposer()
            return composer.compose(contexts, **kwargs)
        
        # Otherwise, use semantic composition
        ranked_contexts = self._rank_by_relevance(contexts, query, embedding_model)
        
        # Compose contexts
        composer = SequentialComposer()
        return composer.compose(
            ranked_contexts,
            context_type=context_type,
            source=source,
            tags=tags,
            include_metadata=include_metadata,
        )
    
    def _rank_by_relevance(self, contexts: List[Context], query: str, embedding_model: str) -> List[Context]:
        """
        Rank contexts by relevance to a query.
        
        Args:
            contexts: The contexts to rank.
            query: The query to use for relevance ranking.
            embedding_model: The embedding model to use for semantic similarity.
            
        Returns:
            List of contexts ranked by relevance.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use an embedding model to calculate
        # semantic similarity between the query and each context, then rank them
        
        # For now, just return the contexts in their original order
        return contexts
