"""
Memory fixtures for testing.

This module provides fixtures for testing memory components, including FAISS memory,
Neo4j memory, and other memory implementations.
"""

import os
import tempfile
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.fixtures.base import Fixture, TempDirFixture, MockFixture


@tag("testing.fixtures")
class MemoryFixture(Fixture):
    """
    Fixture for memory components.
    
    This class provides fixtures for testing memory components, including FAISS memory,
    Neo4j memory, and other memory implementations.
    
    Attributes:
        name: The name of the fixture.
        memory_type: The type of memory to create.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the memory component.
    
    TODO(Issue #13): Add support for more memory types
    TODO(Issue #13): Implement memory validation
    """
    
    def __init__(
        self,
        name: str = "memory",
        memory_type: str = "faiss",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the memory fixture.
        
        Args:
            name: The name of the fixture.
            memory_type: The type of memory to create.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the memory component.
        """
        super().__init__(name, scope, metadata)
        self.memory_type = memory_type
        self.config = config or {}
        self._temp_dir = None
        self._memory = None
    
    def setup(self) -> Any:
        """
        Set up the memory component.
        
        Returns:
            The memory component.
        """
        # Create a temporary directory for the memory component
        self._temp_dir = tempfile.TemporaryDirectory()
        
        # Create the memory component
        if self.memory_type == "faiss":
            from augment_adam.memory.faiss_memory import FAISSMemory
            
            self._memory = FAISSMemory(
                persist_dir=self._temp_dir.name,
                collection_name=self.config.get("collection_name", "test_memory"),
                **{k: v for k, v in self.config.items() if k != "collection_name"}
            )
        elif self.memory_type == "neo4j":
            from augment_adam.memory.neo4j_memory import Neo4jMemory
            
            self._memory = Neo4jMemory(
                collection_name=self.config.get("collection_name", "test_memory"),
                **{k: v for k, v in self.config.items() if k != "collection_name"}
            )
        elif self.memory_type == "redis":
            from augment_adam.memory.redis_memory import RedisMemory
            
            self._memory = RedisMemory(
                collection_name=self.config.get("collection_name", "test_memory"),
                **{k: v for k, v in self.config.items() if k != "collection_name"}
            )
        elif self.memory_type == "chroma":
            from augment_adam.memory.chroma_memory import ChromaMemory
            
            self._memory = ChromaMemory(
                persist_dir=self._temp_dir.name,
                collection_name=self.config.get("collection_name", "test_memory"),
                **{k: v for k, v in self.config.items() if k != "collection_name"}
            )
        elif self.memory_type == "mock":
            import unittest.mock as mock
            
            self._memory = mock.MagicMock()
            
            # Configure the mock
            for key, value in self.config.items():
                setattr(self._memory, key, value)
        else:
            raise ValueError(f"Unknown memory type: {self.memory_type}")
        
        return self._memory
    
    def teardown(self) -> None:
        """Clean up the memory component."""
        if self._memory is not None:
            # Clean up the memory component
            if hasattr(self._memory, "cleanup") and callable(self._memory.cleanup):
                self._memory.cleanup()
            
            self._memory = None
        
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None


@tag("testing.fixtures")
class FAISSMemoryFixture(MemoryFixture):
    """
    Fixture for FAISS memory.
    
    This class provides a fixture for testing FAISS memory.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the FAISS memory.
    
    TODO(Issue #13): Add support for FAISS memory validation
    TODO(Issue #13): Implement FAISS memory analytics
    """
    
    def __init__(
        self,
        name: str = "faiss_memory",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the FAISS memory fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the FAISS memory.
        """
        super().__init__(name, "faiss", scope, metadata, config)


@tag("testing.fixtures")
class Neo4jMemoryFixture(MemoryFixture):
    """
    Fixture for Neo4j memory.
    
    This class provides a fixture for testing Neo4j memory.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the Neo4j memory.
    
    TODO(Issue #13): Add support for Neo4j memory validation
    TODO(Issue #13): Implement Neo4j memory analytics
    """
    
    def __init__(
        self,
        name: str = "neo4j_memory",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the Neo4j memory fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the Neo4j memory.
        """
        super().__init__(name, "neo4j", scope, metadata, config)


@tag("testing.fixtures")
class MockMemoryFixture(MemoryFixture):
    """
    Fixture for mock memory.
    
    This class provides a fixture for testing with a mock memory.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the mock memory.
    
    TODO(Issue #13): Add support for mock memory validation
    TODO(Issue #13): Implement mock memory analytics
    """
    
    def __init__(
        self,
        name: str = "mock_memory",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the mock memory fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the mock memory.
        """
        super().__init__(name, "mock", scope, metadata, config)
