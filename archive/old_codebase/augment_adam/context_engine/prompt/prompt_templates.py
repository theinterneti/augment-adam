"""Prompt Templates for the Context Engine.

This module provides templates for different types of prompts.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class PromptTemplates:
    """Prompt Templates for the Context Engine.
    
    This class provides templates for different types of prompts.
    
    Attributes:
        templates: Dictionary of prompt templates
    """
    
    def __init__(self):
        """Initialize the Prompt Templates."""
        self.templates = {}
        self._initialize_default_templates()
        
        logger.info("Prompt Templates initialized")
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates."""
        # General QA template
        self.templates["qa"] = (
            "You are a helpful assistant. Use the following context to answer the question.\n\n"
            "Context:\n{context}\n\n"
            "Question: {query}\n\n"
            "Answer:"
        )
        
        # Summarization template
        self.templates["summarize"] = (
            "You are a helpful assistant. Summarize the following context.\n\n"
            "Context:\n{context}\n\n"
            "Instructions: {query}\n\n"
            "Summary:"
        )
        
        # Code generation template
        self.templates["code"] = (
            "You are a helpful coding assistant. Use the following context to write code.\n\n"
            "Context:\n{context}\n\n"
            "Task: {query}\n\n"
            "Code:"
        )
        
        # Creative writing template
        self.templates["creative"] = (
            "You are a creative writing assistant. Use the following context for inspiration.\n\n"
            "Context:\n{context}\n\n"
            "Creative task: {query}\n\n"
            "Creative output:"
        )
        
        # Analysis template
        self.templates["analyze"] = (
            "You are an analytical assistant. Analyze the following context.\n\n"
            "Context:\n{context}\n\n"
            "Analysis task: {query}\n\n"
            "Analysis:"
        )
        
        # Default template
        self.templates["default"] = self.templates["qa"]
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a prompt template by name.
        
        Args:
            name: The name of the template
            
        Returns:
            The template string, or None if not found
        """
        return self.templates.get(name)
    
    def add_template(self, name: str, template: str) -> None:
        """Add a prompt template.
        
        Args:
            name: The name of the template
            template: The template string
        """
        self.templates[name] = template
        logger.info(f"Added prompt template: {name}")
    
    def remove_template(self, name: str) -> bool:
        """Remove a prompt template.
        
        Args:
            name: The name of the template
            
        Returns:
            True if the template was removed, False if it wasn't found
        """
        if name in self.templates:
            del self.templates[name]
            logger.info(f"Removed prompt template: {name}")
            return True
        return False
    
    def get_all_templates(self) -> Dict[str, str]:
        """Get all prompt templates.
        
        Returns:
            Dictionary of all prompt templates
        """
        return self.templates.copy()
