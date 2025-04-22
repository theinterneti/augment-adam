"""Memory management for the Dukat assistant.

This module provides the core memory management functionality for
storing and retrieving information across conversations.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
import os
from pathlib import Path
import json
import time

import chromadb
from chromadb.config import Settings

from dukat.core.errors import (
    DatabaseError, ResourceError, NotFoundError, ErrorCategory,
    wrap_error, log_error, retry, CircuitBreaker
)
from dukat.core.settings import get_settings

logger = logging.getLogger(__name__)


class Memory:
    """Core memory management for the Dukat assistant.

    This class provides the foundation for storing and retrieving
    information across conversations.

    Attributes:
        persist_dir: Directory to persist memory data.
        client: ChromaDB client for vector storage.
        collections: Dictionary of ChromaDB collections.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = None,
    ):
        """Initialize the memory system.

        Args:
            persist_dir: Directory to persist memory data. If None, uses the value from settings.
            collection_name: Name of the default collection. If None, uses the value from settings.

        Raises:
            ResourceError: If there is an error creating the persist directory.
            DatabaseError: If there is an error initializing the ChromaDB client.
        """
        # Get settings for memory configuration
        settings = get_settings()
        memory_settings = settings.memory

        # Use provided values or defaults from settings
        self.persist_dir = persist_dir or os.path.expanduser("~/.dukat/memory")
        collection_name = collection_name or "dukat_memory"

        try:
            # Create directory if it doesn't exist
            os.makedirs(self.persist_dir, exist_ok=True)

            logger.info(
                f"Initializing memory system with persist_dir: {self.persist_dir}")

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            # Initialize collections
            self.collections = {}
            self._init_collections(collection_name)

            logger.info("Memory system initialized")

        except OSError as e:
            # Handle directory creation errors
            error = wrap_error(
                e,
                message=f"Failed to create memory directory: {self.persist_dir}",
                category=ErrorCategory.RESOURCE,
                details={
                    "persist_dir": self.persist_dir,
                },
            )
            log_error(error, logger=logger)
            raise error

        except Exception as e:
            # Handle ChromaDB initialization errors
            error = wrap_error(
                e,
                message="Failed to initialize memory system",
                category=ErrorCategory.DATABASE,
                details={
                    "persist_dir": self.persist_dir,
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            raise error

    def _init_collections(self, collection_name: str) -> None:
        """Initialize ChromaDB collections.

        Args:
            collection_name: Name of the default collection.

        Raises:
            DatabaseError: If there is an error initializing the collections.
        """
        try:
            # Create or get the main collection
            self.collections["main"] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Main memory collection for Dukat"}
            )

            logger.info(f"Initialized collection: {collection_name}")

        except Exception as e:
            # Wrap the exception in a DatabaseError
            error = wrap_error(
                e,
                message=f"Error initializing collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                },
            )

            # Log the error with context
            log_error(error, logger=logger)

            # Re-raise the wrapped error
            raise error

    @retry(max_attempts=2, delay=1.0)
    def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = "main",
        id_prefix: str = "mem",
    ) -> str:
        """Add a memory to the specified collection.

        Args:
            text: The text content to store.
            metadata: Additional metadata for the memory.
            collection_name: Name of the collection to store in.
            id_prefix: Prefix for the generated ID.

        Returns:
            The ID of the stored memory, or an empty string if there was an error.
        """
        if not text:
            logger.warning("Attempted to add empty text to memory")
            return ""

        # Generate a unique ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        memory_id = f"{id_prefix}_{timestamp}"

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata["timestamp"] = timestamp
        metadata["type"] = metadata.get("type", "general")

        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(
                    f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]

            # Add the memory
            collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[memory_id],
            )

            logger.info(f"Added memory with ID: {memory_id}")
            return memory_id

        except Exception as e:
            # Wrap the exception in a DatabaseError
            error = wrap_error(
                e,
                message="Error adding memory",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "memory_id": memory_id,
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "text_length": len(text),
                    "collection_name": collection_name,
                },
            )

            # Return empty string to indicate failure
            return ""

    # Create a circuit breaker for memory retrieval
    _retrieve_circuit = CircuitBreaker(
        name="memory_retrieval",
        failure_threshold=3,
        recovery_timeout=30.0,
    )

    @retry(max_attempts=2, delay=1.0)
    @_retrieve_circuit
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        collection_name: str = "main",
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve memories based on a query.

        Args:
            query: The query text to search for.
            n_results: Number of results to return.
            collection_name: Name of the collection to search in.
            filter_metadata: Metadata filters to apply.

        Returns:
            A list of matching memories with their metadata.

        Raises:
            DatabaseError: If there is an error retrieving memories.
            CircuitBreakerError: If the circuit breaker is open due to too many failures.
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(
                    f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]

            # Query the collection
            start_time = time.time()
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata,
            )
            query_time = time.time() - start_time

            # Format the results
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                })

            logger.info(
                f"Retrieved {len(formatted_results)} memories for query: {query[:50]}... in {query_time:.2f}s")
            return formatted_results

        except Exception as e:
            # Wrap the exception in a DatabaseError
            error = wrap_error(
                e,
                message="Error retrieving memories",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "query_length": len(query),
                    "n_results": n_results,
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "query_preview": query[:50] + "..." if len(query) > 50 else query,
                    "collection_name": collection_name,
                    "filter_metadata": filter_metadata,
                },
            )

            # Return empty list to indicate failure
            return []

    @retry(max_attempts=2, delay=1.0)
    def get_by_id(
        self,
        memory_id: str,
        collection_name: str = "main",
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: The ID of the memory to retrieve.
            collection_name: Name of the collection to search in.

        Returns:
            The memory with its metadata, or None if not found.

        Raises:
            DatabaseError: If there is an error retrieving the memory.
            NotFoundError: If the memory is not found.
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(
                    f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]

            # Get the memory
            result = collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"],
            )

            if not result["ids"]:
                # Create a NotFoundError
                error = NotFoundError(
                    message=f"Memory with ID {memory_id} not found",
                    details={
                        "memory_id": memory_id,
                        "collection_name": collection_name,
                    },
                )

                # Log the error
                log_error(error, logger=logger, level=logging.WARNING)

                # Return None to indicate not found
                return None

            # Format the result
            memory = {
                "id": result["ids"][0],
                "text": result["documents"][0],
                "metadata": result["metadatas"][0],
            }

            logger.info(f"Retrieved memory with ID: {memory_id}")
            return memory

        except Exception as e:
            # Wrap the exception in a DatabaseError
            error = wrap_error(
                e,
                message=f"Error retrieving memory by ID: {memory_id}",
                category=ErrorCategory.DATABASE,
                details={
                    "memory_id": memory_id,
                    "collection_name": collection_name,
                },
            )

            # Log the error with context
            log_error(error, logger=logger)

            # Return None to indicate failure
            return None

    @retry(max_attempts=2, delay=1.0)
    def delete(
        self,
        memory_id: str,
        collection_name: str = "main",
    ) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: The ID of the memory to delete.
            collection_name: Name of the collection to delete from.

        Returns:
            True if successful, False otherwise.

        Raises:
            DatabaseError: If there is an error deleting the memory.
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(
                    f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]

            # Delete the memory
            collection.delete(
                ids=[memory_id],
            )

            logger.info(f"Deleted memory with ID: {memory_id}")
            return True

        except Exception as e:
            # Wrap the exception in a DatabaseError
            error = wrap_error(
                e,
                message=f"Error deleting memory: {memory_id}",
                category=ErrorCategory.DATABASE,
                details={
                    "memory_id": memory_id,
                    "collection_name": collection_name,
                },
            )

            # Log the error with context
            log_error(error, logger=logger)

            # Return False to indicate failure
            return False

    @retry(max_attempts=2, delay=1.0)
    def clear(
        self,
        collection_name: str = "main",
    ) -> bool:
        """Clear all memories from a collection.

        Args:
            collection_name: Name of the collection to clear.

        Returns:
            True if successful, False otherwise.

        Raises:
            DatabaseError: If there is an error clearing the collection.
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(
                    f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]

            # Clear the collection
            collection.delete(
                where={},
            )

            logger.info(f"Cleared collection: {collection_name}")
            return True

        except Exception as e:
            # Wrap the exception in a DatabaseError
            error = wrap_error(
                e,
                message=f"Error clearing collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                },
            )

            # Log the error with context
            log_error(error, logger=logger)

            # Return False to indicate failure
            return False


# Singleton instance for easy access
default_memory: Optional[Memory] = None


def get_memory(
    persist_dir: Optional[str] = None,
    collection_name: str = None,
) -> Memory:
    """Get or create the default memory instance.

    Args:
        persist_dir: Directory to persist memory data. If None, uses the value from settings.
        collection_name: Name of the default collection. If None, uses the value from settings.

    Returns:
        The default memory instance.

    Raises:
        ResourceError: If there is an error creating the persist directory.
        DatabaseError: If there is an error initializing the ChromaDB client.
    """
    global default_memory

    try:
        if default_memory is None:
            # Get settings for memory configuration
            settings = get_settings()
            memory_settings = settings.memory

            # Use provided values or defaults from settings
            persist_dir = persist_dir or os.path.expanduser("~/.dukat/memory")
            collection_name = collection_name or "dukat_memory"

            # Create the memory instance
            default_memory = Memory(persist_dir, collection_name)

        return default_memory

    except Exception as e:
        # Wrap the exception in a DatabaseError
        error = wrap_error(
            e,
            message="Failed to initialize memory system",
            category=ErrorCategory.DATABASE,
            details={
                "persist_dir": persist_dir,
                "collection_name": collection_name,
            },
        )

        # Log the error with context
        log_error(error, logger=logger)

        # Re-raise the wrapped error
        raise error
