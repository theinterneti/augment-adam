"""
Context fixtures for testing.

This module provides fixtures for testing context components, including context engines,
context chunkers, and context retrievers.
"""

import os
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.fixtures.base import Fixture, MockFixture


@tag("testing.fixtures")
class ContextFixture(Fixture):
    """
    Fixture for context components.
    
    This class provides fixtures for testing context components, including context engines,
    context chunkers, and context retrievers.
    
    Attributes:
        name: The name of the fixture.
        context_type: The type of context component to create.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the context component.
    
    TODO(Issue #13): Add support for more context types
    TODO(Issue #13): Implement context validation
    """
    
    def __init__(
        self,
        name: str = "context",
        context_type: str = "mock",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the context fixture.
        
        Args:
            name: The name of the fixture.
            context_type: The type of context component to create.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the context component.
        """
        super().__init__(name, scope, metadata)
        self.context_type = context_type
        self.config = config or {}
        self._context = None
    
    def setup(self) -> Any:
        """
        Set up the context component.
        
        Returns:
            The context component.
        """
        # Create the context component
        if self.context_type == "engine":
            from augment_adam.context.engine import ContextEngine
            
            self._context = ContextEngine(
                **self.config
            )
        elif self.context_type == "chunker":
            from augment_adam.context.chunker import ContextChunker
            
            self._context = ContextChunker(
                **self.config
            )
        elif self.context_type == "retriever":
            from augment_adam.context.retriever import ContextRetriever
            
            self._context = ContextRetriever(
                **self.config
            )
        elif self.context_type == "mock":
            import unittest.mock as mock
            
            self._context = mock.MagicMock()
            
            # Configure the mock
            for key, value in self.config.items():
                setattr(self._context, key, value)
        else:
            raise ValueError(f"Unknown context type: {self.context_type}")
        
        return self._context
    
    def teardown(self) -> None:
        """Clean up the context component."""
        if self._context is not None:
            # Clean up the context component
            if hasattr(self._context, "cleanup") and callable(self._context.cleanup):
                self._context.cleanup()
            
            self._context = None


@tag("testing.fixtures")
class MockContextFixture(ContextFixture):
    """
    Fixture for mock context components.
    
    This class provides a fixture for testing with a mock context component.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        config: Configuration for the mock context component.
        responses: Predefined responses for the mock context component.
    
    TODO(Issue #13): Add support for mock context validation
    TODO(Issue #13): Implement mock context analytics
    """
    
    def __init__(
        self,
        name: str = "mock_context",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        responses: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the mock context fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            config: Configuration for the mock context component.
            responses: Predefined responses for the mock context component.
        """
        super().__init__(name, "mock", scope, metadata, config)
        self.responses = responses or {}
    
    def setup(self) -> Any:
        """
        Set up the mock context component.
        
        Returns:
            The mock context component.
        """
        # Create the mock context component
        context = super().setup()
        
        # Configure the mock context component with predefined responses
        for method, response in self.responses.items():
            getattr(context, method).return_value = response
        
        return context
