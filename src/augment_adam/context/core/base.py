"""
Base classes for the context engine.

This module provides the base classes for the context engine, including
the Context class, ContextType enum, ContextEngine class, and ContextManager class.
"""

import uuid
import datetime
import json
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory


class ContextType(Enum):
    """
    Types of context in the context engine.
    
    This enum defines the types of context in the context engine, including
    text, code, conversation, document, and custom context types.
    """
    
    TEXT = auto()
    CODE = auto()
    CONVERSATION = auto()
    DOCUMENT = auto()
    KNOWLEDGE = auto()
    TASK = auto()
    SYSTEM = auto()
    USER = auto()
    CUSTOM = auto()


@dataclass
class Context:
    """
    Context for AI models.
    
    This class represents a context for AI models, including its content,
    metadata, and other properties.
    
    Attributes:
        id: Unique identifier for the context.
        content: The content of the context.
        context_type: The type of context.
        metadata: Additional metadata for the context.
        created_at: When the context was created.
        updated_at: When the context was last updated.
        expires_at: When the context expires (if applicable).
        importance: Importance score for the context (0-1).
        embedding: Vector embedding for the context (if applicable).
        tokens: Estimated token count for the context.
        chunks: List of chunk IDs if this context is composed of chunks.
        parent_id: ID of the parent context if this is a chunk.
        source: Source of the context (e.g., file path, URL).
        tags: List of tags for the context.
    
    TODO(Issue #7): Add support for context versioning
    TODO(Issue #7): Implement context validation
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    context_type: ContextType = ContextType.TEXT
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    expires_at: Optional[str] = None
    importance: float = 0.5
    embedding: Optional[List[float]] = None
    tokens: int = 0
    chunks: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize the context with timestamps."""
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        
        # Estimate token count if not provided
        if self.tokens == 0 and self.content:
            self.tokens = self._estimate_tokens(self.content)
    
    def update(self, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the context.
        
        Args:
            content: New content for the context.
            metadata: New metadata for the context.
        """
        if content is not None:
            self.content = content
            self.tokens = self._estimate_tokens(content)
        
        if metadata is not None:
            self.metadata.update(metadata)
        
        self.updated_at = datetime.datetime.now().isoformat()
    
    def is_expired(self) -> bool:
        """
        Check if the context is expired.
        
        Returns:
            True if the context is expired, False otherwise.
        """
        if self.expires_at is None:
            return False
        
        expires_at = datetime.datetime.fromisoformat(self.expires_at)
        return datetime.datetime.now() > expires_at
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the context.
        
        Args:
            tag: The tag to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the context.
        
        Args:
            tag: The tag to remove.
            
        Returns:
            True if the tag was removed, False otherwise.
        """
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the context has a specific tag.
        
        Args:
            tag: The tag to check.
            
        Returns:
            True if the context has the tag, False otherwise.
        """
        return tag in self.tags
    
    def add_chunk(self, chunk_id: str) -> None:
        """
        Add a chunk to the context.
        
        Args:
            chunk_id: The ID of the chunk to add.
        """
        if chunk_id not in self.chunks:
            self.chunks.append(chunk_id)
    
    def remove_chunk(self, chunk_id: str) -> bool:
        """
        Remove a chunk from the context.
        
        Args:
            chunk_id: The ID of the chunk to remove.
            
        Returns:
            True if the chunk was removed, False otherwise.
        """
        if chunk_id in self.chunks:
            self.chunks.remove(chunk_id)
            return True
        return False
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        
        Args:
            text: The text to estimate tokens for.
            
        Returns:
            Estimated number of tokens.
        """
        # Simple estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary.
        
        Returns:
            Dictionary representation of the context.
        """
        return {
            "id": self.id,
            "content": self.content,
            "context_type": self.context_type.name,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "importance": self.importance,
            "embedding": self.embedding,
            "tokens": self.tokens,
            "chunks": self.chunks,
            "parent_id": self.parent_id,
            "source": self.source,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """
        Create a context from a dictionary.
        
        Args:
            data: Dictionary representation of the context.
            
        Returns:
            Context.
        """
        # Convert context_type from string to enum
        context_type = data.get("context_type", ContextType.TEXT.name)
        if isinstance(context_type, str):
            try:
                context_type = ContextType[context_type]
            except KeyError:
                context_type = ContextType.CUSTOM
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content", ""),
            context_type=context_type,
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            expires_at=data.get("expires_at"),
            importance=data.get("importance", 0.5),
            embedding=data.get("embedding"),
            tokens=data.get("tokens", 0),
            chunks=data.get("chunks", []),
            parent_id=data.get("parent_id"),
            source=data.get("source"),
            tags=data.get("tags", []),
        )
    
    def to_json(self) -> str:
        """
        Convert the context to a JSON string.
        
        Returns:
            JSON string representation of the context.
        """
        data = self.to_dict()
        # Convert embedding to list if it's a numpy array
        if data["embedding"] is not None and hasattr(data["embedding"], "tolist"):
            data["embedding"] = data["embedding"].tolist()
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Context':
        """
        Create a context from a JSON string.
        
        Args:
            json_str: JSON string representation of the context.
            
        Returns:
            Context.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


@tag("context")
class ContextEngine:
    """
    Engine for managing context.
    
    This class provides methods for managing context, including chunking,
    composition, retrieval, and prompt management.
    
    Attributes:
        name: The name of the context engine.
        contexts: Dictionary of contexts, keyed by ID.
        metadata: Additional metadata for the context engine.
        chunker: The chunker to use for chunking content.
        composer: The composer to use for composing context.
        retriever: The retriever to use for retrieving context.
        storage: The storage to use for storing context.
    
    TODO(Issue #7): Add support for context persistence
    TODO(Issue #7): Implement context validation
    """
    
    def __init__(
        self,
        name: str,
        chunker: Optional['Chunker'] = None,
        composer: Optional['ContextComposer'] = None,
        retriever: Optional['ContextRetriever'] = None,
        storage: Optional['ContextStorage'] = None,
    ) -> None:
        """
        Initialize the context engine.
        
        Args:
            name: The name of the context engine.
            chunker: The chunker to use for chunking content.
            composer: The composer to use for composing context.
            retriever: The retriever to use for retrieving context.
            storage: The storage to use for storing context.
        """
        self.name = name
        self.contexts: Dict[str, Context] = {}
        self.metadata: Dict[str, Any] = {}
        
        # Components will be set later if not provided
        self.chunker = chunker
        self.composer = composer
        self.retriever = retriever
        self.storage = storage
    
    def add_context(self, context: Context) -> str:
        """
        Add a context to the engine.
        
        Args:
            context: The context to add.
            
        Returns:
            The ID of the added context.
        """
        self.contexts[context.id] = context
        
        # If storage is available, store the context
        if self.storage is not None:
            self.storage.store_context(context)
        
        return context.id
    
    def get_context(self, context_id: str) -> Optional[Context]:
        """
        Get a context by ID.
        
        Args:
            context_id: The ID of the context to get.
            
        Returns:
            The context, or None if it doesn't exist.
        """
        # Try to get from memory first
        context = self.contexts.get(context_id)
        
        # If not in memory but storage is available, try to get from storage
        if context is None and self.storage is not None:
            context = self.storage.retrieve_context(context_id)
            if context is not None:
                self.contexts[context_id] = context
        
        return context
    
    def update_context(self, context_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[Context]:
        """
        Update a context.
        
        Args:
            context_id: The ID of the context to update.
            content: New content for the context.
            metadata: New metadata for the context.
            
        Returns:
            The updated context, or None if it doesn't exist.
        """
        context = self.get_context(context_id)
        if context is None:
            return None
        
        context.update(content, metadata)
        
        # If storage is available, update the context in storage
        if self.storage is not None:
            self.storage.update_context(context)
        
        return context
    
    def remove_context(self, context_id: str) -> bool:
        """
        Remove a context.
        
        Args:
            context_id: The ID of the context to remove.
            
        Returns:
            True if the context was removed, False otherwise.
        """
        if context_id in self.contexts:
            del self.contexts[context_id]
            
            # If storage is available, remove the context from storage
            if self.storage is not None:
                self.storage.delete_context(context_id)
            
            return True
        
        # If not in memory but storage is available, try to remove from storage
        if self.storage is not None:
            return self.storage.delete_context(context_id)
        
        return False
    
    def chunk_content(self, content: str, context_type: ContextType, **kwargs: Any) -> List[Context]:
        """
        Chunk content into smaller contexts.
        
        Args:
            content: The content to chunk.
            context_type: The type of context.
            **kwargs: Additional arguments for the chunker.
            
        Returns:
            List of context chunks.
            
        Raises:
            ValueError: If no chunker is available.
        """
        if self.chunker is None:
            raise ValueError("No chunker available")
        
        return self.chunker.chunk(content, context_type, **kwargs)
    
    def compose_context(self, contexts: List[Context], **kwargs: Any) -> Context:
        """
        Compose multiple contexts into a single context.
        
        Args:
            contexts: The contexts to compose.
            **kwargs: Additional arguments for the composer.
            
        Returns:
            Composed context.
            
        Raises:
            ValueError: If no composer is available.
        """
        if self.composer is None:
            raise ValueError("No composer available")
        
        return self.composer.compose(contexts, **kwargs)
    
    def retrieve_context(self, query: str, limit: int = 10, **kwargs: Any) -> List[Context]:
        """
        Retrieve contexts based on a query.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            **kwargs: Additional arguments for the retriever.
            
        Returns:
            List of contexts that match the query.
            
        Raises:
            ValueError: If no retriever is available.
        """
        if self.retriever is None:
            raise ValueError("No retriever available")
        
        return self.retriever.retrieve(query, limit, **kwargs)
    
    def get_contexts_by_type(self, context_type: ContextType) -> List[Context]:
        """
        Get contexts by type.
        
        Args:
            context_type: The type of contexts to get.
            
        Returns:
            List of contexts of the specified type.
        """
        return [context for context in self.contexts.values() if context.context_type == context_type]
    
    def get_contexts_by_tag(self, tag: str) -> List[Context]:
        """
        Get contexts by tag.
        
        Args:
            tag: The tag to filter by.
            
        Returns:
            List of contexts with the specified tag.
        """
        return [context for context in self.contexts.values() if tag in context.tags]
    
    def get_contexts_by_source(self, source: str) -> List[Context]:
        """
        Get contexts by source.
        
        Args:
            source: The source to filter by.
            
        Returns:
            List of contexts with the specified source.
        """
        return [context for context in self.contexts.values() if context.source == source]
    
    def get_child_contexts(self, parent_id: str) -> List[Context]:
        """
        Get child contexts of a parent context.
        
        Args:
            parent_id: The ID of the parent context.
            
        Returns:
            List of child contexts.
        """
        return [context for context in self.contexts.values() if context.parent_id == parent_id]
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the context engine.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the context engine.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context engine to a dictionary.
        
        Returns:
            Dictionary representation of the context engine.
        """
        return {
            "name": self.name,
            "contexts": {context_id: context.to_dict() for context_id, context in self.contexts.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextEngine':
        """
        Create a context engine from a dictionary.
        
        Args:
            data: Dictionary representation of the context engine.
            
        Returns:
            Context engine.
        """
        engine = cls(name=data.get("name", ""))
        engine.metadata = data.get("metadata", {})
        
        for context_data in data.get("contexts", {}).values():
            context = Context.from_dict(context_data)
            engine.contexts[context.id] = context
        
        return engine


@tag("context")
class ContextManager:
    """
    Manager for context engines.
    
    This class manages multiple context engines, providing a unified interface
    for adding, retrieving, updating, and removing contexts.
    
    Attributes:
        engines: Dictionary of context engines, keyed by name.
        metadata: Additional metadata for the context manager.
    
    TODO(Issue #7): Add support for context persistence
    TODO(Issue #7): Implement context validation
    """
    
    def __init__(self) -> None:
        """Initialize the context manager."""
        self.engines: Dict[str, ContextEngine] = {}
        self.metadata: Dict[str, Any] = {}
    
    def register_engine(self, engine: ContextEngine) -> None:
        """
        Register a context engine with the manager.
        
        Args:
            engine: The context engine to register.
        """
        self.engines[engine.name] = engine
    
    def unregister_engine(self, name: str) -> bool:
        """
        Unregister a context engine from the manager.
        
        Args:
            name: The name of the context engine to unregister.
            
        Returns:
            True if the context engine was unregistered, False otherwise.
        """
        if name in self.engines:
            del self.engines[name]
            return True
        return False
    
    def get_engine(self, name: str) -> Optional[ContextEngine]:
        """
        Get a context engine by name.
        
        Args:
            name: The name of the context engine.
            
        Returns:
            The context engine, or None if it doesn't exist.
        """
        return self.engines.get(name)
    
    def get_all_engines(self) -> List[ContextEngine]:
        """
        Get all context engines.
        
        Returns:
            List of all context engines.
        """
        return list(self.engines.values())
    
    def add_context(self, engine_name: str, context: Context) -> Optional[str]:
        """
        Add a context to a context engine.
        
        Args:
            engine_name: The name of the context engine.
            context: The context to add.
            
        Returns:
            The ID of the added context, or None if the context engine doesn't exist.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return None
        
        return engine.add_context(context)
    
    def get_context(self, engine_name: str, context_id: str) -> Optional[Context]:
        """
        Get a context from a context engine.
        
        Args:
            engine_name: The name of the context engine.
            context_id: The ID of the context.
            
        Returns:
            The context, or None if the context engine or context doesn't exist.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return None
        
        return engine.get_context(context_id)
    
    def update_context(self, engine_name: str, context_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[Context]:
        """
        Update a context in a context engine.
        
        Args:
            engine_name: The name of the context engine.
            context_id: The ID of the context.
            content: New content for the context.
            metadata: New metadata for the context.
            
        Returns:
            The updated context, or None if the context engine or context doesn't exist.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return None
        
        return engine.update_context(context_id, content, metadata)
    
    def remove_context(self, engine_name: str, context_id: str) -> bool:
        """
        Remove a context from a context engine.
        
        Args:
            engine_name: The name of the context engine.
            context_id: The ID of the context.
            
        Returns:
            True if the context was removed, False otherwise.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return False
        
        return engine.remove_context(context_id)
    
    def chunk_content(self, engine_name: str, content: str, context_type: ContextType, **kwargs: Any) -> Optional[List[Context]]:
        """
        Chunk content into smaller contexts using a context engine.
        
        Args:
            engine_name: The name of the context engine.
            content: The content to chunk.
            context_type: The type of context.
            **kwargs: Additional arguments for the chunker.
            
        Returns:
            List of context chunks, or None if the context engine doesn't exist.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return None
        
        try:
            return engine.chunk_content(content, context_type, **kwargs)
        except ValueError:
            return None
    
    def compose_context(self, engine_name: str, contexts: List[Context], **kwargs: Any) -> Optional[Context]:
        """
        Compose multiple contexts into a single context using a context engine.
        
        Args:
            engine_name: The name of the context engine.
            contexts: The contexts to compose.
            **kwargs: Additional arguments for the composer.
            
        Returns:
            Composed context, or None if the context engine doesn't exist.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return None
        
        try:
            return engine.compose_context(contexts, **kwargs)
        except ValueError:
            return None
    
    def retrieve_context(self, engine_name: str, query: str, limit: int = 10, **kwargs: Any) -> Optional[List[Context]]:
        """
        Retrieve contexts based on a query using a context engine.
        
        Args:
            engine_name: The name of the context engine.
            query: The query to search for.
            limit: The maximum number of results to return.
            **kwargs: Additional arguments for the retriever.
            
        Returns:
            List of contexts that match the query, or None if the context engine doesn't exist.
        """
        engine = self.get_engine(engine_name)
        if engine is None:
            return None
        
        try:
            return engine.retrieve_context(query, limit, **kwargs)
        except ValueError:
            return None
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the context manager.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the context manager.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context manager to a dictionary.
        
        Returns:
            Dictionary representation of the context manager.
        """
        return {
            "engines": {name: engine.to_dict() for name, engine in self.engines.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextManager':
        """
        Create a context manager from a dictionary.
        
        Args:
            data: Dictionary representation of the context manager.
            
        Returns:
            Context manager.
        """
        manager = cls()
        manager.metadata = data.get("metadata", {})
        
        for engine_data in data.get("engines", {}).values():
            engine = ContextEngine.from_dict(engine_data)
            manager.register_engine(engine)
        
        return manager


# Singleton instance
_context_manager: Optional[ContextManager] = None

def get_context_manager() -> ContextManager:
    """
    Get the singleton instance of the context manager.
    
    Returns:
        The context manager instance.
    """
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
