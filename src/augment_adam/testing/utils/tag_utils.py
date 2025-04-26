"""
Tagging utilities for testing.

This module provides utilities for working with the tagging system in tests,
including functions to reset the tag registry and safely create tags.
"""

from typing import Dict, List, Any, Optional, Union, TypeVar, Callable, ContextManager
from contextlib import contextmanager

from augment_adam.utils.tagging.core import (
    Tag, TagCategory, TagRegistry, get_tag, get_or_create_tag
)
from augment_adam.utils.tagging.registry_factory import (
    get_registry_factory, get_registry, IsolatedTagRegistry
)

def reset_tag_registry() -> None:
    """
    Reset the tag registry to its initial state.

    This function is useful for tests that need to start with a clean tag registry.
    It creates a new isolated registry for the current test.
    """
    # Enter test mode with a fresh registry
    get_registry_factory().enter_test_mode()

@contextmanager
def isolated_tag_registry() -> ContextManager[TagRegistry]:
    """
    Context manager for creating an isolated tag registry.

    This context manager is useful for tests that need to create tags
    without affecting the global tag registry.

    Example:
        with isolated_tag_registry():
            # Create tags in an isolated registry
            tag = create_tag("test_tag", TagCategory.TEST)

    Returns:
        A context manager that yields an isolated tag registry.
    """
    with IsolatedTagRegistry() as registry:
        yield registry

def safe_tag(tag_name: str, **attributes: Any) -> Callable:
    """
    A safer version of the tag decorator that handles duplicate tags gracefully.

    This decorator uses get_or_create_tag instead of create_tag to avoid errors
    when the same tag is applied multiple times. It also uses the registry factory
    to ensure thread safety and test isolation.

    Args:
        tag_name: The name of the tag to apply.
        **attributes: Optional attributes for the tag.

    Returns:
        The decorated class or function.

    Example:
        @safe_tag("memory.vector.faiss")
        class FAISSMemory:
            pass
    """
    def decorator(obj: Any) -> Any:
        # Get the current registry
        registry = get_registry()

        # Get the tag
        tag_parts = tag_name.split(".")
        if len(tag_parts) == 1:
            # Single tag
            # Try to infer the category
            if hasattr(obj, "__module__"):
                module = obj.__module__
                if "memory" in module:
                    category = TagCategory.MEMORY
                elif "model" in module:
                    category = TagCategory.MODEL
                elif "agent" in module:
                    category = TagCategory.AGENT
                elif "context" in module:
                    category = TagCategory.CONTEXT
                elif "template" in module:
                    category = TagCategory.TEMPLATE
                elif "test" in module:
                    category = TagCategory.TEST
                elif "doc" in module or "documentation" in module:
                    category = TagCategory.DOCUMENTATION
                elif "web" in module:
                    category = TagCategory.WEB
                elif "api" in module:
                    category = TagCategory.API
                elif "plugin" in module:
                    category = TagCategory.PLUGIN
                elif "core" in module:
                    category = TagCategory.CORE
                else:
                    category = TagCategory.UTILITY
            else:
                category = TagCategory.UTILITY

            # Use the registry directly to avoid global state
            tag_obj = registry.get_tag(tag_name)
            if tag_obj is None:
                try:
                    tag_obj = registry.create_tag(tag_name, category, attributes=attributes)
                except ValueError:
                    # Tag already exists, get it
                    tag_obj = registry.get_tag(tag_name)
        else:
            # Hierarchical tag
            parent_name = tag_parts[0]

            # Try to infer the category
            if hasattr(obj, "__module__"):
                module = obj.__module__
                if "memory" in module:
                    category = TagCategory.MEMORY
                elif "model" in module:
                    category = TagCategory.MODEL
                elif "agent" in module:
                    category = TagCategory.AGENT
                elif "context" in module:
                    category = TagCategory.CONTEXT
                elif "template" in module:
                    category = TagCategory.TEMPLATE
                elif "test" in module:
                    category = TagCategory.TEST
                elif "doc" in module or "documentation" in module:
                    category = TagCategory.DOCUMENTATION
                elif "web" in module:
                    category = TagCategory.WEB
                elif "api" in module:
                    category = TagCategory.API
                elif "plugin" in module:
                    category = TagCategory.PLUGIN
                elif "core" in module:
                    category = TagCategory.CORE
                else:
                    category = TagCategory.UTILITY
            else:
                category = TagCategory.UTILITY

            # Get or create the parent tag
            parent_tag = registry.get_tag(parent_name)
            if parent_tag is None:
                try:
                    parent_tag = registry.create_tag(parent_name, category)
                except ValueError:
                    # Tag already exists, get it
                    parent_tag = registry.get_tag(parent_name)

            # Create the rest of the hierarchy
            current_tag = parent_tag
            for i in range(1, len(tag_parts) - 1):
                part = tag_parts[i]
                child_tag = registry.get_tag(part)
                if child_tag is None:
                    try:
                        child_tag = registry.create_tag(part, current_tag.category, current_tag)
                    except ValueError:
                        # Tag already exists, get it
                        child_tag = registry.get_tag(part)
                current_tag = child_tag

            # Create the final tag
            final_part = tag_parts[-1]
            tag_obj = registry.get_tag(final_part)
            if tag_obj is None:
                try:
                    tag_obj = registry.create_tag(final_part, current_tag.category, current_tag, attributes=attributes)
                except ValueError:
                    # Tag already exists, get it
                    tag_obj = registry.get_tag(final_part)

        # Add the tag to the object
        if not hasattr(obj, "__tags__"):
            obj.__tags__ = []
        obj.__tags__.append(tag_obj)

        return obj

    return decorator
