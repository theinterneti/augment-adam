"""Neo4j-based memory for the Augment Adam assistant.

This module provides a Neo4j-based memory implementation for
efficient vector storage and retrieval with graph capabilities.

Version: 0.1.0
Created: 2025-04-25
"""

from augment_adam.memory.memory_interface import MemoryInterface

import os
import time
import uuid
import json
import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from augment_adam.core.settings import get_settings
from augment_adam.core.errors import (
    ResourceError, DatabaseError, wrap_error, log_error, ErrorCategory
)
from augment_adam.memory.neo4j_client import Neo4jClient, get_neo4j_client

logger = logging.getLogger(__name__)


class Neo4jMemory(MemoryInterface):
    """Neo4j-based memory for the Augment Adam assistant.

    This class provides a Neo4j-based implementation for storing and
    retrieving vector embeddings efficiently with graph capabilities.

    Attributes:
        client: Neo4j client for database operations
        embedding_model: SentenceTransformer model for creating embeddings
        embedding_dim: Dimension of the embeddings
        default_collection: Default collection name
    """

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        collection_name: str = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """Initialize the Neo4j memory system.

        Args:
            neo4j_uri: URI for the Neo4j server
            neo4j_user: Username for Neo4j authentication
            neo4j_password: Password for Neo4j authentication
            collection_name: Name of the default collection
            embedding_model: Name of the SentenceTransformer model to use for embeddings

        Raises:
            ResourceError: If there is an error initializing resources
            DatabaseError: If there is an error initializing the Neo4j database
        """
        # Get settings for memory configuration
        settings = get_settings()
        memory_settings = settings.memory

        # Use provided values or defaults from settings
        self.default_collection = collection_name or "augment_adam_memory"

        try:
            # Initialize Neo4j client
            self.client = get_neo4j_client(
                uri=neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                user=neo4j_user or os.getenv("NEO4J_USER", "neo4j"),
                password=neo4j_password or os.getenv("NEO4J_PASSWORD", "password")
            )

            logger.info(f"Initializing Neo4j memory system with default collection: {self.default_collection}")

            # Initialize embedding model
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

                # Update Neo4j client with correct vector dimensions
                self.client.vector_dimensions = self.embedding_dim
            except Exception as e:
                # Fall back to a simpler embedding approach if SentenceTransformer fails
                logger.warning(f"Failed to load SentenceTransformer model: {e}")
                logger.warning("Falling back to simple embedding approach")

                # Use a simple embedding approach based on word counts
                self.embedding_model = TfidfVectorizer(max_features=768)
                self.embedding_dim = 768  # Standard dimension

                # Update Neo4j client with correct vector dimensions
                self.client.vector_dimensions = self.embedding_dim

            # Initialize collection
            asyncio.run(self._init_collection(self.default_collection))

            logger.info("Neo4j memory system initialized")

        except Exception as e:
            # Handle initialization errors
            error = wrap_error(
                e,
                message="Failed to initialize Neo4j memory system",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": self.default_collection,
                },
            )
            log_error(error, logger=logger)
            raise error

    async def _init_collection(self, collection_name: str) -> None:
        """Initialize a Neo4j collection.

        Args:
            collection_name: Name of the collection to initialize

        Raises:
            DatabaseError: If there is an error initializing the collection
        """
        try:
            # Create vector index for the collection
            success = await self.client.create_index(collection_name)

            if not success:
                raise DatabaseError(
                    message=f"Failed to create vector index for collection: {collection_name}",
                    details={"collection_name": collection_name}
                )

            logger.info(f"Initialized collection: {collection_name}")
        except Exception as e:
            # Handle collection initialization errors
            error = wrap_error(
                e,
                message=f"Failed to initialize collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            raise error

    def _create_embedding(self, text: str) -> List[float]:
        """Create an embedding for the given text.

        Args:
            text: Text to create an embedding for

        Returns:
            Vector embedding
        """
        if isinstance(self.embedding_model, TfidfVectorizer):
            # For TfidfVectorizer, we need to fit and transform
            if not hasattr(self.embedding_model, 'vocabulary_'):
                # First time, fit the vectorizer
                self.embedding_model.fit([text])

            # Transform the text to get the embedding
            embedding_matrix = self.embedding_model.transform([text])
            embedding = embedding_matrix.toarray()[0]

            # Ensure the embedding has the right dimension
            if len(embedding) < self.embedding_dim:
                # Pad with zeros if needed
                embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
            elif len(embedding) > self.embedding_dim:
                # Truncate if needed
                embedding = embedding[:self.embedding_dim]
        else:
            # For SentenceTransformer
            embedding = self.embedding_model.encode([text])[0]

        return embedding.tolist()

    def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = None,
        id_prefix: str = "mem"
    ) -> str:
        """Add a memory to the specified collection.

        Args:
            text: The text to add
            metadata: Additional metadata for the memory
            collection_name: The name of the collection to add to. If None, uses the default collection.
            id_prefix: Prefix for the generated ID

        Returns:
            The ID of the added memory
        """
        # Use default collection if none specified
        collection_name = collection_name or self.default_collection

        if not text:
            logger.warning("Attempted to add empty text to memory")
            return ""

        try:
            # Generate a unique ID
            memory_id = f"{id_prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # Create embedding
            embedding = self._create_embedding(text)

            # Add metadata
            metadata = metadata or {}
            metadata["text"] = text
            metadata["timestamp"] = int(time.time())

            # Store in Neo4j
            success = asyncio.run(self.client.store_vector(
                vector_id=memory_id,
                embedding=embedding,
                metadata=metadata,
                collection_name=collection_name
            ))

            if not success:
                logger.warning(f"Failed to add memory to collection: {collection_name}")
                return ""

            logger.info(f"Added memory {memory_id} to collection {collection_name}")
            return memory_id
        except Exception as e:
            # Handle add errors
            error = wrap_error(
                e,
                message=f"Failed to add memory to collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "text_length": len(text) if text else 0,
                },
            )
            log_error(error, logger=logger)
            return ""

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve memories similar to the query.

        Args:
            query: The query text
            n_results: Maximum number of results to return
            filter_metadata: Filter to apply to the metadata
            collection_name: The name of the collection to search. If None, uses the default collection.

        Returns:
            A list of tuples containing the memory and its similarity score
        """
        # Use default collection if none specified
        collection_name = collection_name or self.default_collection

        if not query:
            logger.warning("Attempted to retrieve with empty query")
            return []

        try:
            # Create embedding
            query_embedding = self._create_embedding(query)

            # Search in Neo4j
            results = asyncio.run(self.client.search_vectors(
                query_vector=query_embedding,
                k=n_results,
                filter_metadata=filter_metadata,
                collection_name=collection_name
            ))

            return results
        except Exception as e:
            # Handle retrieve errors
            error = wrap_error(
                e,
                message=f"Failed to retrieve memories from collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "query_length": len(query) if query else 0,
                },
            )
            log_error(error, logger=logger)
            return []

    def get_by_id(
        self,
        memory_id: str,
        collection_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get a memory by ID.

        Args:
            memory_id: The ID of the memory to get
            collection_name: The name of the collection to search. If None, uses the default collection.

        Returns:
            The memory, or None if not found
        """
        # Use default collection if none specified
        collection_name = collection_name or self.default_collection

        try:
            # Get from Neo4j
            memory = asyncio.run(self.client.get_by_id(
                vector_id=memory_id,
                collection_name=collection_name
            ))

            return memory
        except Exception as e:
            # Handle get errors
            error = wrap_error(
                e,
                message=f"Failed to get memory by ID from collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "memory_id": memory_id,
                },
            )
            log_error(error, logger=logger)
            return None

    def delete(
        self,
        memory_id: str,
        collection_name: str = None
    ) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: The ID of the memory to delete
            collection_name: The name of the collection to delete from. If None, uses the default collection.

        Returns:
            True if the memory was deleted, False otherwise
        """
        # Use default collection if none specified
        collection_name = collection_name or self.default_collection

        try:
            # Delete from Neo4j
            success = asyncio.run(self.client.delete(
                vector_id=memory_id,
                collection_name=collection_name
            ))

            return success
        except Exception as e:
            # Handle delete errors
            error = wrap_error(
                e,
                message=f"Failed to delete memory from collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "memory_id": memory_id,
                },
            )
            log_error(error, logger=logger)
            return False

    def clear(
        self,
        collection_name: str = None
    ) -> bool:
        """Clear all memories from a collection.

        Args:
            collection_name: The name of the collection to clear. If None, uses the default collection.

        Returns:
            True if the collection was cleared, False otherwise
        """
        # Use default collection if none specified
        collection_name = collection_name or self.default_collection

        try:
            # Clear from Neo4j
            success = asyncio.run(self.client.clear(
                collection_name=collection_name
            ))

            return success
        except Exception as e:
            # Handle clear errors
            error = wrap_error(
                e,
                message=f"Failed to clear collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return False

    def create_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        collection_name: str = None
    ) -> bool:
        """Create a relationship between two memories.

        Args:
            from_id: Source memory ID
            to_id: Target memory ID
            relationship_type: Type of relationship
            properties: Relationship properties
            collection_name: The name of the collection. If None, uses the default collection.

        Returns:
            True if successful, False otherwise
        """
        # Use default collection if none specified
        collection_name = collection_name or self.default_collection

        try:
            # Create relationship in Neo4j
            success = asyncio.run(self.client.create_relationship(
                from_id=from_id,
                to_id=to_id,
                relationship_type=relationship_type,
                properties=properties,
                collection_name=collection_name
            ))

            return success
        except Exception as e:
            # Handle relationship creation errors
            error = wrap_error(
                e,
                message=f"Failed to create relationship in collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "from_id": from_id,
                    "to_id": to_id,
                    "relationship_type": relationship_type,
                },
            )
            log_error(error, logger=logger)
            return False

    def close(self):
        """Close the Neo4j memory system."""
        try:
            asyncio.run(self.client.close())
            logger.info("Closed Neo4j memory system")
        except Exception as e:
            # Handle close errors
            error = wrap_error(
                e,
                message="Failed to close Neo4j memory system",
                category=ErrorCategory.DATABASE
            )
            log_error(error, logger=logger)


# Global instance for singleton pattern
default_memory = None


def get_neo4j_memory(
    neo4j_uri: Optional[str] = None,
    neo4j_user: Optional[str] = None,
    neo4j_password: Optional[str] = None,
    collection_name: Optional[str] = None,
    embedding_model: str = "all-MiniLM-L6-v2",
) -> Neo4jMemory:
    """Get the default Neo4j memory instance.

    This function returns the global Neo4j memory instance, creating it
    if it doesn't exist.

    Args:
        neo4j_uri: URI for the Neo4j server
        neo4j_user: Username for Neo4j authentication
        neo4j_password: Password for Neo4j authentication
        collection_name: Name of the default collection
        embedding_model: Name of the SentenceTransformer model to use for embeddings

    Returns:
        The default Neo4j memory instance

    Raises:
        ResourceError: If there is an error initializing resources
        DatabaseError: If there is an error initializing the Neo4j database
    """
    global default_memory

    try:
        if default_memory is None:
            # Get settings for memory configuration
            settings = get_settings()
            memory_settings = settings.memory

            # Use provided values or defaults from settings
            collection_name = collection_name or "augment_adam_memory"

            # Create the memory instance
            default_memory = Neo4jMemory(
                neo4j_uri=neo4j_uri,
                neo4j_user=neo4j_user,
                neo4j_password=neo4j_password,
                collection_name=collection_name,
                embedding_model=embedding_model
            )

        return default_memory
    except Exception as e:
        # Handle initialization errors
        error = wrap_error(
            e,
            message="Failed to get default Neo4j memory instance",
            category=ErrorCategory.DATABASE,
            details={
                "collection_name": collection_name,
            },
        )
        log_error(error, logger=logger)
        raise error
