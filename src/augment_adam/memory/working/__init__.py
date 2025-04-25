"""
Working memory system.

This module provides a working memory system for temporary storage of
information during ongoing tasks.
"""

from augment_adam.memory.working.base import WorkingMemory, WorkingMemoryItem

__all__ = [
    "WorkingMemory",
    "WorkingMemoryItem",
]