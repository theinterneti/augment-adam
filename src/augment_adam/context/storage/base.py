"""
Base classes for the storage module.

This module provides the base classes for the storage module, including
the ContextStorage base class and various storage implementations.
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.context.core.base import Context, ContextType


@tag("context.storage")
class ContextStorage(ABC):
    """
    Base class for context storage backends.
    
    This class defines the interface for context storage backends, which
    store and retrieve contexts.
    
    Attributes:
        name: The name of the storage backend.
        metadata: Additional metadata for the storage backend.
    
    TODO(Issue #7): Add support for storage validation
    TODO(Issue #7): Implement storage analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the storage backend.
        
        Args:
            name: The name of the storage backend.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def store_context(self, context: Context) -> bool:
        """
        Store a context.
        
        Args:
            context: The context to store.
            
        Returns:
            True if the context was stored successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def retrieve_context(self, context_id: str) -> Optional[Context]:
        """
        Retrieve a context by ID.
        
        Args:
            context_id: The ID of the context to retrieve.
            
        Returns:
            The context, or None if it doesn't exist.
        """
        pass
    
    @abstractmethod
    def update_context(self, context: Context) -> bool:
        """
        Update a context.
        
        Args:
            context: The context to update.
            
        Returns:
            True if the context was updated successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context.
        
        Args:
            context_id: The ID of the context to delete.
            
        Returns:
            True if the context was deleted successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def search_contexts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Context]:
        """
        Search for contexts.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            **kwargs: Additional arguments for the search.
            
        Returns:
            List of contexts that match the query.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the storage backend.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the storage backend.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("context.storage.redis")
class RedisStorage(ContextStorage):
    """
    Redis-based context storage backend.
    
    This class implements a context storage backend using Redis for efficient
    key-value storage and retrieval.
    
    Attributes:
        name: The name of the storage backend.
        metadata: Additional metadata for the storage backend.
        redis_client: The Redis client to use for storage.
        prefix: The prefix to use for Redis keys.
        ttl: The time-to-live for stored contexts in seconds (0 means no expiration).
    
    TODO(Issue #7): Add support for Redis Streams for real-time updates
    TODO(Issue #7): Implement storage validation
    """
    
    def __init__(
        self,
        name: str = "redis_storage",
        redis_client: Optional[Any] = None,
        prefix: str = "context:",
        ttl: int = 0,
    ) -> None:
        """
        Initialize the Redis storage backend.
        
        Args:
            name: The name of the storage backend.
            redis_client: The Redis client to use for storage.
            prefix: The prefix to use for Redis keys.
            ttl: The time-to-live for stored contexts in seconds (0 means no expiration).
        """
        super().__init__(name)
        
        self.redis_client = redis_client
        self.prefix = prefix
        self.ttl = ttl
        
        self.metadata["prefix"] = prefix
        self.metadata["ttl"] = ttl
    
    def store_context(self, context: Context) -> bool:
        """
        Store a context in Redis.
        
        Args:
            context: The context to store.
            
        Returns:
            True if the context was stored successfully, False otherwise.
        """
        if self.redis_client is None:
            return False
        
        try:
            # Store the context as a JSON string
            key = f"{self.prefix}{context.id}"
            value = context.to_json()
            
            if self.ttl > 0:
                self.redis_client.setex(key, self.ttl, value)
            else:
                self.redis_client.set(key, value)
            
            # Store the context in secondary indices
            self._index_context(context)
            
            return True
        except Exception:
            return False
    
    def retrieve_context(self, context_id: str) -> Optional[Context]:
        """
        Retrieve a context from Redis by ID.
        
        Args:
            context_id: The ID of the context to retrieve.
            
        Returns:
            The context, or None if it doesn't exist.
        """
        if self.redis_client is None:
            return None
        
        try:
            # Retrieve the context JSON string
            key = f"{self.prefix}{context_id}"
            value = self.redis_client.get(key)
            
            if value is None:
                return None
            
            # Parse the JSON string to a Context object
            return Context.from_json(value.decode("utf-8"))
        except Exception:
            return None
    
    def update_context(self, context: Context) -> bool:
        """
        Update a context in Redis.
        
        Args:
            context: The context to update.
            
        Returns:
            True if the context was updated successfully, False otherwise.
        """
        if self.redis_client is None:
            return False
        
        try:
            # Remove old indices
            old_context = self.retrieve_context(context.id)
            if old_context is not None:
                self._remove_indices(old_context)
            
            # Store the updated context
            return self.store_context(context)
        except Exception:
            return False
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context from Redis.
        
        Args:
            context_id: The ID of the context to delete.
            
        Returns:
            True if the context was deleted successfully, False otherwise.
        """
        if self.redis_client is None:
            return False
        
        try:
            # Retrieve the context to remove indices
            context = self.retrieve_context(context_id)
            if context is not None:
                self._remove_indices(context)
            
            # Delete the context
            key = f"{self.prefix}{context_id}"
            self.redis_client.delete(key)
            
            return True
        except Exception:
            return False
    
    def search_contexts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Context]:
        """
        Search for contexts in Redis.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            **kwargs: Additional arguments for the search.
                context_type: Filter by context type.
                source: Filter by source.
                tags: Filter by tags.
                min_importance: Filter by minimum importance.
                max_tokens: Filter by maximum tokens.
            
        Returns:
            List of contexts that match the query.
        """
        if self.redis_client is None:
            return []
        
        try:
            # Get search parameters
            context_type = kwargs.get("context_type")
            source = kwargs.get("source")
            tags = kwargs.get("tags", [])
            min_importance = kwargs.get("min_importance", 0.0)
            max_tokens = kwargs.get("max_tokens")
            
            # Build filter sets
            filter_sets = []
            
            # Filter by context type
            if context_type is not None:
                context_type_str = context_type.name if isinstance(context_type, ContextType) else context_type
                filter_sets.append(f"{self.prefix}type:{context_type_str}")
            
            # Filter by source
            if source is not None:
                filter_sets.append(f"{self.prefix}source:{source}")
            
            # Filter by tags
            for tag in tags:
                filter_sets.append(f"{self.prefix}tag:{tag}")
            
            # If no filters, use all contexts
            if not filter_sets:
                all_keys = self.redis_client.keys(f"{self.prefix}*")
                context_keys = [key for key in all_keys if b":" not in key[len(self.prefix):]]
                
                # Retrieve contexts
                contexts = []
                for key in context_keys[:limit]:
                    value = self.redis_client.get(key)
                    if value is not None:
                        try:
                            context = Context.from_json(value.decode("utf-8"))
                            
                            # Apply additional filters
                            if context.importance >= min_importance and (max_tokens is None or context.tokens <= max_tokens):
                                contexts.append(context)
                        except Exception:
                            pass
                
                return contexts
            
            # Intersect filter sets
            result_set = None
            for filter_set in filter_sets:
                members = self.redis_client.smembers(filter_set)
                if result_set is None:
                    result_set = set(members)
                else:
                    result_set &= set(members)
            
            if not result_set:
                return []
            
            # Retrieve contexts
            contexts = []
            for context_id in list(result_set)[:limit]:
                context = self.retrieve_context(context_id.decode("utf-8"))
                if context is not None:
                    # Apply additional filters
                    if context.importance >= min_importance and (max_tokens is None or context.tokens <= max_tokens):
                        contexts.append(context)
            
            return contexts
        except Exception:
            return []
    
    def _index_context(self, context: Context) -> None:
        """
        Index a context in Redis for efficient searching.
        
        Args:
            context: The context to index.
        """
        if self.redis_client is None:
            return
        
        # Index by context type
        type_key = f"{self.prefix}type:{context.context_type.name}"
        self.redis_client.sadd(type_key, context.id)
        
        # Index by source
        if context.source:
            source_key = f"{self.prefix}source:{context.source}"
            self.redis_client.sadd(source_key, context.id)
        
        # Index by tags
        for tag in context.tags:
            tag_key = f"{self.prefix}tag:{tag}"
            self.redis_client.sadd(tag_key, context.id)
    
    def _remove_indices(self, context: Context) -> None:
        """
        Remove a context from Redis indices.
        
        Args:
            context: The context to remove from indices.
        """
        if self.redis_client is None:
            return
        
        # Remove from context type index
        type_key = f"{self.prefix}type:{context.context_type.name}"
        self.redis_client.srem(type_key, context.id)
        
        # Remove from source index
        if context.source:
            source_key = f"{self.prefix}source:{context.source}"
            self.redis_client.srem(source_key, context.id)
        
        # Remove from tag indices
        for tag in context.tags:
            tag_key = f"{self.prefix}tag:{tag}"
            self.redis_client.srem(tag_key, context.id)


@tag("context.storage.chroma")
class ChromaStorage(ContextStorage):
    """
    Chroma-based context storage backend.
    
    This class implements a context storage backend using Chroma for efficient
    vector storage and retrieval.
    
    Attributes:
        name: The name of the storage backend.
        metadata: Additional metadata for the storage backend.
        chroma_client: The Chroma client to use for storage.
        collection_name: The name of the Chroma collection.
        embedding_function: The embedding function to use for generating embeddings.
    
    TODO(Issue #7): Add support for more embedding functions
    TODO(Issue #7): Implement storage validation
    """
    
    def __init__(
        self,
        name: str = "chroma_storage",
        chroma_client: Optional[Any] = None,
        collection_name: str = "contexts",
        embedding_function: Optional[Any] = None,
    ) -> None:
        """
        Initialize the Chroma storage backend.
        
        Args:
            name: The name of the storage backend.
            chroma_client: The Chroma client to use for storage.
            collection_name: The name of the Chroma collection.
            embedding_function: The embedding function to use for generating embeddings.
        """
        super().__init__(name)
        
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.embedding_function = embedding_function
        self.collection = None
        
        self.metadata["collection_name"] = collection_name
        
        # Initialize collection if client is provided
        if self.chroma_client is not None:
            self._init_collection()
    
    def _init_collection(self) -> None:
        """Initialize the Chroma collection."""
        if self.chroma_client is None:
            return
        
        try:
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
        except Exception:
            self.collection = None
    
    def store_context(self, context: Context) -> bool:
        """
        Store a context in Chroma.
        
        Args:
            context: The context to store.
            
        Returns:
            True if the context was stored successfully, False otherwise.
        """
        if self.collection is None:
            return False
        
        try:
            # Convert context to Chroma format
            document = context.content
            metadata = {
                "context_type": context.context_type.name,
                "created_at": context.created_at,
                "updated_at": context.updated_at,
                "expires_at": context.expires_at,
                "importance": context.importance,
                "tokens": context.tokens,
                "parent_id": context.parent_id,
                "source": context.source,
                "tags": json.dumps(context.tags),
                "metadata": json.dumps(context.metadata),
                "chunks": json.dumps(context.chunks),
            }
            
            # Use existing embedding if available, otherwise let Chroma generate one
            embedding = context.embedding
            
            # Add to collection
            self.collection.add(
                ids=[context.id],
                documents=[document],
                metadatas=[metadata],
                embeddings=[embedding] if embedding is not None else None
            )
            
            return True
        except Exception:
            return False
    
    def retrieve_context(self, context_id: str) -> Optional[Context]:
        """
        Retrieve a context from Chroma by ID.
        
        Args:
            context_id: The ID of the context to retrieve.
            
        Returns:
            The context, or None if it doesn't exist.
        """
        if self.collection is None:
            return None
        
        try:
            # Query the collection by ID
            result = self.collection.get(ids=[context_id])
            
            if not result["ids"]:
                return None
            
            # Extract data
            document = result["documents"][0]
            metadata = result["metadatas"][0]
            embedding = result["embeddings"][0] if "embeddings" in result and result["embeddings"] else None
            
            # Parse metadata
            context_type_str = metadata.get("context_type", "TEXT")
            try:
                context_type = ContextType[context_type_str]
            except KeyError:
                context_type = ContextType.CUSTOM
            
            tags = json.loads(metadata.get("tags", "[]"))
            context_metadata = json.loads(metadata.get("metadata", "{}"))
            chunks = json.loads(metadata.get("chunks", "[]"))
            
            # Create context object
            context = Context(
                id=context_id,
                content=document,
                context_type=context_type,
                metadata=context_metadata,
                created_at=metadata.get("created_at"),
                updated_at=metadata.get("updated_at"),
                expires_at=metadata.get("expires_at"),
                importance=metadata.get("importance", 0.5),
                embedding=embedding,
                tokens=metadata.get("tokens", 0),
                chunks=chunks,
                parent_id=metadata.get("parent_id"),
                source=metadata.get("source"),
                tags=tags,
            )
            
            return context
        except Exception:
            return None
    
    def update_context(self, context: Context) -> bool:
        """
        Update a context in Chroma.
        
        Args:
            context: The context to update.
            
        Returns:
            True if the context was updated successfully, False otherwise.
        """
        if self.collection is None:
            return False
        
        try:
            # Delete the existing context
            self.collection.delete(ids=[context.id])
            
            # Store the updated context
            return self.store_context(context)
        except Exception:
            return False
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context from Chroma.
        
        Args:
            context_id: The ID of the context to delete.
            
        Returns:
            True if the context was deleted successfully, False otherwise.
        """
        if self.collection is None:
            return False
        
        try:
            # Delete the context
            self.collection.delete(ids=[context_id])
            return True
        except Exception:
            return False
    
    def search_contexts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Context]:
        """
        Search for contexts in Chroma.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            **kwargs: Additional arguments for the search.
                context_type: Filter by context type.
                source: Filter by source.
                tags: Filter by tags.
                min_importance: Filter by minimum importance.
                max_tokens: Filter by maximum tokens.
            
        Returns:
            List of contexts that match the query.
        """
        if self.collection is None:
            return []
        
        try:
            # Get search parameters
            context_type = kwargs.get("context_type")
            source = kwargs.get("source")
            tags = kwargs.get("tags", [])
            min_importance = kwargs.get("min_importance", 0.0)
            max_tokens = kwargs.get("max_tokens")
            
            # Build where clause
            where_clause = {}
            
            if context_type is not None:
                context_type_str = context_type.name if isinstance(context_type, ContextType) else context_type
                where_clause["context_type"] = context_type_str
            
            if source is not None:
                where_clause["source"] = source
            
            if min_importance > 0.0:
                where_clause["importance"] = {"$gte": min_importance}
            
            if max_tokens is not None:
                where_clause["tokens"] = {"$lte": max_tokens}
            
            # Tags filtering is more complex with Chroma
            # We'll filter tags after retrieving results
            
            # Query the collection
            result = self.collection.query(
                query_texts=[query],
                n_results=limit * 2,  # Get more results to account for tag filtering
                where=where_clause if where_clause else None
            )
            
            if not result["ids"]:
                return []
            
            # Convert results to contexts
            contexts = []
            for i, context_id in enumerate(result["ids"][0]):
                document = result["documents"][0][i]
                metadata = result["metadatas"][0][i]
                embedding = result["embeddings"][0][i] if "embeddings" in result and result["embeddings"] else None
                
                # Parse metadata
                context_type_str = metadata.get("context_type", "TEXT")
                try:
                    context_type = ContextType[context_type_str]
                except KeyError:
                    context_type = ContextType.CUSTOM
                
                tags_json = metadata.get("tags", "[]")
                context_tags = json.loads(tags_json) if tags_json else []
                
                # Filter by tags
                if tags and not all(tag in context_tags for tag in tags):
                    continue
                
                context_metadata = json.loads(metadata.get("metadata", "{}"))
                chunks = json.loads(metadata.get("chunks", "[]"))
                
                # Create context object
                context = Context(
                    id=context_id,
                    content=document,
                    context_type=context_type,
                    metadata=context_metadata,
                    created_at=metadata.get("created_at"),
                    updated_at=metadata.get("updated_at"),
                    expires_at=metadata.get("expires_at"),
                    importance=metadata.get("importance", 0.5),
                    embedding=embedding,
                    tokens=metadata.get("tokens", 0),
                    chunks=chunks,
                    parent_id=metadata.get("parent_id"),
                    source=metadata.get("source"),
                    tags=context_tags,
                )
                
                contexts.append(context)
                
                if len(contexts) >= limit:
                    break
            
            return contexts
        except Exception:
            return []


@tag("context.storage.hybrid")
class HybridStorage(ContextStorage):
    """
    Hybrid context storage backend.
    
    This class implements a context storage backend that combines multiple
    storage backends for more efficient storage and retrieval.
    
    Attributes:
        name: The name of the storage backend.
        metadata: Additional metadata for the storage backend.
        primary_storage: The primary storage backend for metadata and content.
        vector_storage: The vector storage backend for similarity search.
        cache_ttl: The time-to-live for cached contexts in seconds (0 means no expiration).
    
    TODO(Issue #7): Add support for more storage backends
    TODO(Issue #7): Implement storage validation
    """
    
    def __init__(
        self,
        name: str = "hybrid_storage",
        primary_storage: Optional[ContextStorage] = None,
        vector_storage: Optional[ContextStorage] = None,
        cache_ttl: int = 3600,
    ) -> None:
        """
        Initialize the hybrid storage backend.
        
        Args:
            name: The name of the storage backend.
            primary_storage: The primary storage backend for metadata and content.
            vector_storage: The vector storage backend for similarity search.
            cache_ttl: The time-to-live for cached contexts in seconds (0 means no expiration).
        """
        super().__init__(name)
        
        self.primary_storage = primary_storage
        self.vector_storage = vector_storage
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        self.metadata["cache_ttl"] = cache_ttl
    
    def store_context(self, context: Context) -> bool:
        """
        Store a context in multiple storage backends.
        
        Args:
            context: The context to store.
            
        Returns:
            True if the context was stored successfully in at least one backend, False otherwise.
        """
        success = False
        
        # Store in primary storage
        if self.primary_storage is not None:
            primary_success = self.primary_storage.store_context(context)
            success = success or primary_success
        
        # Store in vector storage
        if self.vector_storage is not None:
            vector_success = self.vector_storage.store_context(context)
            success = success or vector_success
        
        # Update cache
        if success:
            self._cache_context(context)
        
        return success
    
    def retrieve_context(self, context_id: str) -> Optional[Context]:
        """
        Retrieve a context by ID.
        
        Args:
            context_id: The ID of the context to retrieve.
            
        Returns:
            The context, or None if it doesn't exist.
        """
        # Check cache first
        cached_context = self._get_cached_context(context_id)
        if cached_context is not None:
            return cached_context
        
        # Try primary storage first
        if self.primary_storage is not None:
            context = self.primary_storage.retrieve_context(context_id)
            if context is not None:
                self._cache_context(context)
                return context
        
        # Try vector storage as fallback
        if self.vector_storage is not None:
            context = self.vector_storage.retrieve_context(context_id)
            if context is not None:
                self._cache_context(context)
                return context
        
        return None
    
    def update_context(self, context: Context) -> bool:
        """
        Update a context in multiple storage backends.
        
        Args:
            context: The context to update.
            
        Returns:
            True if the context was updated successfully in at least one backend, False otherwise.
        """
        success = False
        
        # Update in primary storage
        if self.primary_storage is not None:
            primary_success = self.primary_storage.update_context(context)
            success = success or primary_success
        
        # Update in vector storage
        if self.vector_storage is not None:
            vector_success = self.vector_storage.update_context(context)
            success = success or vector_success
        
        # Update cache
        if success:
            self._cache_context(context)
        
        return success
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context from multiple storage backends.
        
        Args:
            context_id: The ID of the context to delete.
            
        Returns:
            True if the context was deleted successfully from at least one backend, False otherwise.
        """
        success = False
        
        # Delete from primary storage
        if self.primary_storage is not None:
            primary_success = self.primary_storage.delete_context(context_id)
            success = success or primary_success
        
        # Delete from vector storage
        if self.vector_storage is not None:
            vector_success = self.vector_storage.delete_context(context_id)
            success = success or vector_success
        
        # Remove from cache
        if context_id in self.cache:
            del self.cache[context_id]
            if context_id in self.cache_timestamps:
                del self.cache_timestamps[context_id]
        
        return success
    
    def search_contexts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Context]:
        """
        Search for contexts.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            **kwargs: Additional arguments for the search.
            
        Returns:
            List of contexts that match the query.
        """
        # Use vector storage for search if available
        if self.vector_storage is not None:
            return self.vector_storage.search_contexts(query, limit, **kwargs)
        
        # Fall back to primary storage
        if self.primary_storage is not None:
            return self.primary_storage.search_contexts(query, limit, **kwargs)
        
        return []
    
    def _cache_context(self, context: Context) -> None:
        """
        Cache a context.
        
        Args:
            context: The context to cache.
        """
        self.cache[context.id] = context.to_dict()
        self.cache_timestamps[context.id] = time.time()
        
        # Clean up expired cache entries
        self._clean_cache()
    
    def _get_cached_context(self, context_id: str) -> Optional[Context]:
        """
        Get a context from the cache.
        
        Args:
            context_id: The ID of the context to get.
            
        Returns:
            The context, or None if it doesn't exist in the cache or is expired.
        """
        # Check if context is in cache
        if context_id not in self.cache:
            return None
        
        # Check if context is expired
        if self.cache_ttl > 0:
            timestamp = self.cache_timestamps.get(context_id, 0)
            if time.time() - timestamp > self.cache_ttl:
                del self.cache[context_id]
                del self.cache_timestamps[context_id]
                return None
        
        # Return cached context
        try:
            return Context.from_dict(self.cache[context_id])
        except Exception:
            return None
    
    def _clean_cache(self) -> None:
        """Clean up expired cache entries."""
        if self.cache_ttl <= 0:
            return
        
        current_time = time.time()
        expired_ids = []
        
        for context_id, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl:
                expired_ids.append(context_id)
        
        for context_id in expired_ids:
            if context_id in self.cache:
                del self.cache[context_id]
            if context_id in self.cache_timestamps:
                del self.cache_timestamps[context_id]
