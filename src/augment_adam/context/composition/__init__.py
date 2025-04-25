"""
Composition module for the context engine.

This module provides composers for combining multiple contexts into a single
coherent context for more effective AI interactions.
"""

from augment_adam.context.composition.base import (
    ContextComposer,
    SequentialComposer,
    HierarchicalComposer,
    SemanticComposer,
)

__all__ = [
    "ContextComposer",
    "SequentialComposer",
    "HierarchicalComposer",
    "SemanticComposer",
]
