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

import chromadb
from chromadb.config import Settings

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
        collection_name: str = "dukat_memory",
    ):
        """Initialize the memory system.
        
        Args:
            persist_dir: Directory to persist memory data.
            collection_name: Name of the default collection.
        """
        self.persist_dir = persist_dir or os.path.expanduser("~/.dukat/memory")
        
        # Create directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)
        
        logger.info(f"Initializing memory system with persist_dir: {self.persist_dir}")
        
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
    
    def _init_collections(self, collection_name: str) -> None:
        """Initialize ChromaDB collections.
        
        Args:
            collection_name: Name of the default collection.
        """
        try:
            # Create or get the main collection
            self.collections["main"] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Main memory collection for Dukat"}
            )
            
            logger.info(f"Initialized collection: {collection_name}")
        
        except Exception as e:
            logger.error(f"Error initializing collections: {str(e)}")
            raise RuntimeError(f"Error initializing collections: {str(e)}")
    
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
            The ID of the stored memory.
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
                logger.warning(f"Collection {collection_name} not found, using main")
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
            logger.error(f"Error adding memory: {str(e)}")
            return ""
    
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
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]
            
            # Query the collection
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata,
            )
            
            # Format the results
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                })
            
            logger.info(f"Retrieved {len(formatted_results)} memories for query: {query[:50]}...")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return []
    
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
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]
            
            # Get the memory
            result = collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"],
            )
            
            if not result["ids"]:
                logger.warning(f"Memory with ID {memory_id} not found")
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
            logger.error(f"Error retrieving memory by ID: {str(e)}")
            return None
    
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
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]
            
            # Delete the memory
            collection.delete(
                ids=[memory_id],
            )
            
            logger.info(f"Deleted memory with ID: {memory_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return False
    
    def clear(
        self,
        collection_name: str = "main",
    ) -> bool:
        """Clear all memories from a collection.
        
        Args:
            collection_name: Name of the collection to clear.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the collection
            collection = self.collections.get(collection_name)
            if collection is None:
                logger.warning(f"Collection {collection_name} not found, using main")
                collection = self.collections["main"]
            
            # Clear the collection
            collection.delete(
                where={},
            )
            
            logger.info(f"Cleared collection: {collection_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False


# Singleton instance for easy access
default_memory: Optional[Memory] = None


def get_memory(
    persist_dir: Optional[str] = None,
    collection_name: str = "dukat_memory",
) -> Memory:
    """Get or create the default memory instance.
    
    Args:
        persist_dir: Directory to persist memory data.
        collection_name: Name of the default collection.
        
    Returns:
        The default memory instance.
    """
    global default_memory
    
    if default_memory is None:
        default_memory = Memory(persist_dir, collection_name)
    
    return default_memory
