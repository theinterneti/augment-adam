"""
Tag Registry Factory.

This module provides a factory for creating tag registries, allowing for better
isolation in tests and thread safety.
"""

import threading
from typing import Dict, Optional, Any

from augment_adam.utils.tagging.core import TagRegistry

# Thread-local storage for registries
_thread_local = threading.local()

class TagRegistryFactory:
    """
    Factory for creating and managing tag registries.
    
    This class provides methods for creating, retrieving, and managing tag registries.
    It supports thread-local registries and test isolation.
    """
    
    def __init__(self):
        """Initialize the tag registry factory."""
        self._default_registry = TagRegistry()
        self._test_mode = False
        self._test_registry = None
    
    def get_registry(self) -> TagRegistry:
        """
        Get the current tag registry.
        
        Returns:
            The current tag registry.
        """
        # If in test mode, return the test registry
        if self._test_mode and self._test_registry is not None:
            return self._test_registry
        
        # Check for thread-local registry
        if hasattr(_thread_local, 'registry'):
            return _thread_local.registry
        
        # Return the default registry
        return self._default_registry
    
    def create_thread_local_registry(self) -> TagRegistry:
        """
        Create a thread-local registry.
        
        Returns:
            The created registry.
        """
        _thread_local.registry = TagRegistry()
        return _thread_local.registry
    
    def clear_thread_local_registry(self) -> None:
        """Clear the thread-local registry."""
        if hasattr(_thread_local, 'registry'):
            delattr(_thread_local, 'registry')
    
    def enter_test_mode(self) -> TagRegistry:
        """
        Enter test mode with an isolated registry.
        
        Returns:
            The test registry.
        """
        self._test_mode = True
        self._test_registry = TagRegistry()
        return self._test_registry
    
    def exit_test_mode(self) -> None:
        """Exit test mode."""
        self._test_mode = False
        self._test_registry = None

# Singleton instance of the factory
_factory = TagRegistryFactory()

def get_registry_factory() -> TagRegistryFactory:
    """
    Get the singleton instance of the tag registry factory.
    
    Returns:
        The tag registry factory.
    """
    return _factory

def get_registry() -> TagRegistry:
    """
    Get the current tag registry.
    
    Returns:
        The current tag registry.
    """
    return get_registry_factory().get_registry()

class IsolatedTagRegistry:
    """
    Context manager for creating an isolated tag registry.
    
    This context manager is useful for tests that need to create tags
    without affecting the global tag registry.
    
    Example:
        with IsolatedTagRegistry():
            # Create tags in an isolated registry
            tag = create_tag("test_tag", TagCategory.TEST)
    """
    
    def __init__(self, thread_local: bool = False):
        """
        Initialize the isolated tag registry.
        
        Args:
            thread_local: Whether to use a thread-local registry.
        """
        self.thread_local = thread_local
        self.factory = get_registry_factory()
        self.previous_test_mode = None
        self.previous_test_registry = None
    
    def __enter__(self) -> TagRegistry:
        """
        Enter the context and create an isolated registry.
        
        Returns:
            The isolated registry.
        """
        if self.thread_local:
            return self.factory.create_thread_local_registry()
        else:
            self.previous_test_mode = self.factory._test_mode
            self.previous_test_registry = self.factory._test_registry
            return self.factory.enter_test_mode()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context and restore the previous registry."""
        if self.thread_local:
            self.factory.clear_thread_local_registry()
        else:
            self.factory._test_mode = self.previous_test_mode
            self.factory._test_registry = self.previous_test_registry
