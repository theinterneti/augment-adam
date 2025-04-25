"""
Prompt module for the context engine.

This module provides tools for managing prompts, including templates,
variables, and prompt generation.
"""

from augment_adam.context.prompt.base import (
    PromptTemplate,
    PromptManager,
    get_prompt_manager,
)

__all__ = [
    "PromptTemplate",
    "PromptManager",
    "get_prompt_manager",
]
