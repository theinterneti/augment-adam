"""
Model management for the AI coding agent.

This package provides tools for managing and interacting with
local LLM models for code generation, documentation, and testing.
"""

from dukat.ai_agent.models.manager import ModelManager
from dukat.ai_agent.models.prompts import CodePromptTemplates

__all__ = ["ModelManager", "CodePromptTemplates"]
