"""
Core components of the context engine.

This module provides the core components of the context engine, including
the Context class, ContextType enum, ContextEngine class, and ContextManager class.
"""

from augment_adam.context.core.base import (
    Context,
    ContextType,
    ContextEngine,
    ContextManager,
    get_context_manager,
)

__all__ = [
    "Context",
    "ContextType",
    "ContextEngine",
    "ContextManager",
    "get_context_manager",
]
