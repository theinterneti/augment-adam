"""Memory interface for the Augment Adam assistant.

This module provides an interface for memory systems.

Version: 0.1.0
Created: 2025-04-25
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union


class MemoryInterface(ABC):
    """Interface for memory systems.
    
    This abstract class defines the interface that all memory systems
    must implement.
    """
    
    @abstractmethod
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
            collection_name: The name of the collection to add to
            id_prefix: Prefix for the generated ID
            
        Returns:
            The ID of the added memory
        """
        pass
    
    @abstractmethod
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
            collection_name: The name of the collection to search
            
        Returns:
            A list of tuples containing the memory and its similarity score
        """
        pass
    
    @abstractmethod
    def get_by_id(
        self,
        memory_id: str,
        collection_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get a memory by ID.
        
        Args:
            memory_id: The ID of the memory to get
            collection_name: The name of the collection to search
            
        Returns:
            The memory, or None if not found
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        memory_id: str,
        collection_name: str = None
    ) -> bool:
        """Delete a memory by ID.
        
        Args:
            memory_id: The ID of the memory to delete
            collection_name: The name of the collection to delete from
            
        Returns:
            True if the memory was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(
        self,
        collection_name: str = None
    ) -> bool:
        """Clear all memories from a collection.
        
        Args:
            collection_name: The name of the collection to clear
            
        Returns:
            True if the collection was cleared, False otherwise
        """
        pass
