"""
Tagging utilities for testing.

This module provides utilities for working with the tagging system in tests,
including functions to reset the tag registry and safely create tags.
"""

from typing import Dict, List, Any, Optional, Union, TypeVar, Callable, ContextManager, cast
from contextlib import contextmanager

from augment_adam.utils.tagging.core import (
    Tag, TagCategory, TagRegistry, get_tag, get_or_create_tag, create_tag
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

    The decorator:
    1. Gets the current registry from the registry factory
    2. Parses the tag name to handle hierarchical tags (e.g., "memory.vector.faiss")
    3. Infers the tag category from the module name if possible
    4. Creates or retrieves the tag, handling any race conditions
    5. Updates the tag attributes
    6. Attaches the tag to the decorated object

    Args:
        tag_name: The name of the tag to apply. Can be a simple name ("memory")
            or a hierarchical path ("memory.vector.faiss").
        **attributes: Optional attributes for the tag. These will be set on the
            tag even if it already exists.

    Returns:
        The decorated class or function.

    Example:
        @safe_tag("memory.vector.faiss")
        class FAISSMemory:
            pass
    """
    def decorator(obj: Any) -> Any:
        """
        Decorator function that applies the tag to the decorated object.

        Args:
            obj: The object to decorate (class or function).

        Returns:
            The decorated object with the tag applied.
        """
        # Get the current registry
        registry = get_registry()

        # Get the tag
        tag_parts = tag_name.split(".")
        if len(tag_parts) == 1:
            # Single tag - not hierarchical
            # Try to infer the category from the module name
            category = _infer_category_from_module(obj)

            # Use the registry directly to avoid global state
            tag_obj = registry.get_tag(tag_name)
            if tag_obj is None:
                try:
                    # Create the tag if it doesn't exist
                    tag_obj = registry.create_tag(
                        name=tag_name,
                        category=category,
                        attributes=attributes,
                        force=True
                    )
                except ValueError:
                    # Tag might have been created by another thread, get it
                    tag_obj = registry.get_tag(tag_name)

            # Update attributes regardless of whether the tag was created or retrieved
            if tag_obj and attributes:
                for key, value in attributes.items():
                    tag_obj.set_attribute(key, value)
        else:
            # Hierarchical tag (e.g., "memory.vector.faiss")
            parent_name = tag_parts[0]

            # Try to infer the category from the module name
            category = _infer_category_from_module(obj)

            # Get or create the parent tag
            parent_tag = registry.get_tag(parent_name)
            if parent_tag is None:
                try:
                    # Create the parent tag if it doesn't exist
                    parent_tag = registry.create_tag(
                        name=parent_name,
                        category=category,
                        force=True
                    )
                except ValueError:
                    # Parent tag might have been created by another thread, get it
                    parent_tag = registry.get_tag(parent_name)
                    if parent_tag is None:
                        # If still not found, something is wrong
                        raise ValueError(
                            f"Failed to create or retrieve parent tag '{parent_name}'"
                        )

            # Create the rest of the hierarchy
            current_tag = parent_tag

            for i in range(1, len(tag_parts)):
                part = tag_parts[i]

                # Check if the child tag already exists in the parent's children
                child_found = False
                for child in current_tag.children:
                    if child.name == part:
                        current_tag = child
                        child_found = True
                        break

                if not child_found:
                    # Create the child tag if it doesn't exist
                    try:
                        child_tag = registry.create_tag(
                            name=part,
                            category=current_tag.category,
                            parent=current_tag,
                            force=True
                        )
                        current_tag = child_tag
                    except ValueError:
                        # Child tag might have been created by another thread,
                        # try to find it again
                        child_found = False
                        for child in current_tag.children:
                            if child.name == part:
                                current_tag = child
                                child_found = True
                                break

                        if not child_found:
                            # If still not found, try to get it directly from the registry
                            full_path = f"{current_tag.get_full_path()}.{part}"
                            direct_tag = registry.get_tag(full_path)
                            if direct_tag is not None:
                                current_tag = direct_tag
                            else:
                                # If still not found, something is wrong
                                # But don't raise an error, just create a new tag
                                try:
                                    child_tag = registry.create_tag(
                                        name=part,
                                        category=current_tag.category,
                                        parent=current_tag,
                                        force=True,
                                    )
                                    current_tag = child_tag
                                except Exception:
                                    # Last resort: just use the parent tag
                                    pass

            # The final tag is now in current_tag
            tag_obj = current_tag

            # Update attributes regardless of whether the tag was created or retrieved
            if tag_obj and attributes:
                for key, value in attributes.items():
                    tag_obj.set_attribute(key, value)

        # Add the tag to the object
        if not hasattr(obj, "__tags__"):
            obj.__tags__ = []
        obj.__tags__.append(tag_obj)

        return cast(Any, obj)

    return decorator


def _infer_category_from_module(obj: Any) -> TagCategory:
    """
    Infer the tag category from the module name of an object.

    This helper function examines the module name of the given object and
    returns the most appropriate TagCategory based on keywords in the module name.

    Args:
        obj: The object to infer the category from.

    Returns:
        TagCategory: The inferred category, defaulting to TagCategory.UTILITY
            if no specific category can be determined.
    """
    if hasattr(obj, "__module__"):
        module = obj.__module__
        if "memory" in module:
            return TagCategory.MEMORY
        elif "model" in module:
            return TagCategory.MODEL
        elif "agent" in module:
            return TagCategory.AGENT
        elif "context" in module:
            return TagCategory.CONTEXT
        elif "template" in module:
            return TagCategory.TEMPLATE
        elif "test" in module:
            return TagCategory.TEST
        elif "doc" in module or "documentation" in module:
            return TagCategory.DOCUMENTATION
        elif "web" in module:
            return TagCategory.WEB
        elif "api" in module:
            return TagCategory.API
        elif "plugin" in module:
            return TagCategory.PLUGIN
        elif "core" in module:
            return TagCategory.CORE
        elif "data" in module:
            return TagCategory.DATA
        elif "security" in module:
            return TagCategory.SECURITY
        elif "performance" in module:
            return TagCategory.PERFORMANCE
        elif "ui" in module:
            return TagCategory.UI

    # Default to utility if no specific category can be determined
    return TagCategory.UTILITY
