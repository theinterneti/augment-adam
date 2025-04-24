"""Memory Manager for the AI Agent.

This module provides a manager for integrating with memory systems.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.memory import create_memory, get_default_memory

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory Manager for the AI Agent.
    
    This class manages interactions with memory systems.
    
    Attributes:
        memory: The memory system to use
        agent_id: The ID of the agent
        collection_name: The name of the memory collection
    """
    
    def __init__(
        self,
        memory_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        """Initialize the Memory Manager.
        
        Args:
            memory_type: The type of memory to use (if None, use default)
            agent_id: The ID of the agent (if None, generate a random ID)
            collection_name: The name of the memory collection
        """
        try:
            # Initialize memory
            if memory_type:
                self.memory = create_memory(memory_type)
            else:
                self.memory = get_default_memory()
            
            # Set agent ID
            self.agent_id = agent_id or str(uuid.uuid4())
            
            # Set collection name
            self.collection_name = collection_name or f"agent_{self.agent_id}"
            
            logger.info(f"Initialized Memory Manager for agent {self.agent_id}")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to initialize Memory Manager",
                category=ErrorCategory.RESOURCE,
                details={
                    "memory_type": memory_type,
                    "agent_id": agent_id,
                },
            )
            log_error(error, logger=logger)
            raise error
    
    def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a memory.
        
        Args:
            text: The text to add
            metadata: Additional metadata for the memory
            
        Returns:
            The ID of the added memory
        """
        try:
            # Add agent ID to metadata
            metadata = metadata or {}
            metadata["agent_id"] = self.agent_id
            
            # Add to memory
            memory_id = self.memory.add(
                text=text,
                metadata=metadata,
                collection_name=self.collection_name
            )
            
            logger.info(f"Added memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to add memory",
                category=ErrorCategory.RESOURCE,
                details={
                    "text_length": len(text) if text else 0,
                    "collection_name": self.collection_name,
                },
            )
            log_error(error, logger=logger)
            return ""
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve memories.
        
        Args:
            query: The query to retrieve memories for
            n_results: Maximum number of results to retrieve
            filter_metadata: Filter to apply to the metadata
            
        Returns:
            A list of tuples containing the memory and its similarity score
        """
        try:
            # Add agent ID to filter metadata
            filter_metadata = filter_metadata or {}
            filter_metadata["agent_id"] = self.agent_id
            
            # Retrieve from memory
            results = self.memory.retrieve(
                query=query,
                n_results=n_results,
                filter_metadata=filter_metadata,
                collection_name=self.collection_name
            )
            
            logger.info(f"Retrieved {len(results)} memories for query: {query}")
            return results
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to retrieve memories",
                category=ErrorCategory.RESOURCE,
                details={
                    "query": query,
                    "collection_name": self.collection_name,
                },
            )
            log_error(error, logger=logger)
            return []
    
    def update(
        self,
        memory_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a memory.
        
        Args:
            memory_id: The ID of the memory to update
            text: The new text (if None, keep existing text)
            metadata: The new metadata (if None, keep existing metadata)
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Update memory
            success = self.memory.update(
                memory_id=memory_id,
                text=text,
                metadata=metadata,
                collection_name=self.collection_name
            )
            
            logger.info(f"Updated memory with ID: {memory_id}")
            return success
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to update memory",
                category=ErrorCategory.RESOURCE,
                details={
                    "memory_id": memory_id,
                    "collection_name": self.collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            # Delete memory
            success = self.memory.delete(
                memory_id=memory_id,
                collection_name=self.collection_name
            )
            
            logger.info(f"Deleted memory with ID: {memory_id}")
            return success
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to delete memory",
                category=ErrorCategory.RESOURCE,
                details={
                    "memory_id": memory_id,
                    "collection_name": self.collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
