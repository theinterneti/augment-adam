"""Context Engine for the Augment Adam assistant.

This module provides a sophisticated context engine for managing context windows,
retrieving relevant information, and optimizing prompts for LLMs.

Version: 0.1.0
Created: 2025-04-26
"""

from augment_adam.context_engine.context_manager import ContextManager, get_context_manager

__all__ = [
    "ContextManager",
    "get_context_manager",
]