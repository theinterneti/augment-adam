"""Memory factory for the Augment Adam assistant.

This module provides a factory for creating different types of memory systems.

Version: 0.1.0
Created: 2025-04-25
"""

import logging
from typing import Dict, Any, Optional, Union, Type

from augment_adam.core.settings import get_settings
from augment_adam.core.errors import (
    ValidationError, wrap_error, log_error, ErrorCategory
)

logger = logging.getLogger(__name__)


class MemoryFactory:
    """Factory for creating memory systems.
    
    This class provides methods for creating different types of memory systems
    based on configuration.
    """
    
    @staticmethod
    def create_memory(
        memory_type: str = None,
        **kwargs
    ) -> Any:
        """Create a memory system.
        
        Args:
            memory_type: Type of memory system to create (faiss, neo4j)
            **kwargs: Additional arguments to pass to the memory constructor
            
        Returns:
            A memory system instance
            
        Raises:
            ValidationError: If the memory type is invalid
        """
        # Get settings for memory configuration
        settings = get_settings()
        memory_settings = settings.memory
        
        # Use provided memory type or default from settings
        memory_type = memory_type or memory_settings.default_memory_backend
        
        try:
            if memory_type.lower() == "faiss":
                from augment_adam.memory.faiss_memory import FAISSMemory
                return FAISSMemory(**kwargs)
            elif memory_type.lower() == "neo4j":
                from augment_adam.memory.neo4j_memory import Neo4jMemory
                return Neo4jMemory(**kwargs)
            else:
                raise ValidationError(
                    message=f"Invalid memory type: {memory_type}",
                    details={
                        "memory_type": memory_type,
                        "valid_types": ["faiss", "neo4j"],
                    },
                )
        except Exception as e:
            # Handle creation errors
            error = wrap_error(
                e,
                message=f"Failed to create memory system of type: {memory_type}",
                category=ErrorCategory.VALIDATION,
                details={
                    "memory_type": memory_type,
                    "kwargs": kwargs,
                },
            )
            log_error(error, logger=logger)
            raise error
    
    @staticmethod
    def get_default_memory(memory_type: str = None) -> Any:
        """Get the default memory instance.
        
        Args:
            memory_type: Type of memory system to get (faiss, neo4j)
            
        Returns:
            The default memory instance
            
        Raises:
            ValidationError: If the memory type is invalid
        """
        # Get settings for memory configuration
        settings = get_settings()
        memory_settings = settings.memory
        
        # Use provided memory type or default from settings
        memory_type = memory_type or memory_settings.default_memory_backend
        
        try:
            if memory_type.lower() == "faiss":
                from augment_adam.memory.faiss_memory import get_faiss_memory
                return get_faiss_memory()
            elif memory_type.lower() == "neo4j":
                from augment_adam.memory.neo4j_memory import get_neo4j_memory
                return get_neo4j_memory()
            else:
                raise ValidationError(
                    message=f"Invalid memory type: {memory_type}",
                    details={
                        "memory_type": memory_type,
                        "valid_types": ["faiss", "neo4j"],
                    },
                )
        except Exception as e:
            # Handle creation errors
            error = wrap_error(
                e,
                message=f"Failed to get default memory system of type: {memory_type}",
                category=ErrorCategory.VALIDATION,
                details={
                    "memory_type": memory_type,
                },
            )
            log_error(error, logger=logger)
            raise error


# Convenience functions
def create_memory(memory_type: str = None, **kwargs) -> Any:
    """Create a memory system.
    
    Args:
        memory_type: Type of memory system to create (faiss, neo4j)
        **kwargs: Additional arguments to pass to the memory constructor
        
    Returns:
        A memory system instance
    """
    return MemoryFactory.create_memory(memory_type, **kwargs)


def get_default_memory(memory_type: str = None) -> Any:
    """Get the default memory instance.
    
    Args:
        memory_type: Type of memory system to get (faiss, neo4j)
        
    Returns:
        The default memory instance
    """
    return MemoryFactory.get_default_memory(memory_type)
