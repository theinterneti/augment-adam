"""Prompt Composer for the Context Engine.

This module provides a composer for creating prompts with context.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextWindow

logger = logging.getLogger(__name__)


class PromptComposer:
    """Prompt Composer for the Context Engine.
    
    This class composes prompts with context for different types of tasks.
    
    Attributes:
        templates: Dictionary of prompt templates for different types of tasks
        default_template: The default template to use
    """
    
    def __init__(
        self,
        templates: Optional[Dict[str, str]] = None,
        default_template: Optional[str] = None
    ):
        """Initialize the Prompt Composer.
        
        Args:
            templates: Dictionary of prompt templates for different types of tasks
            default_template: The default template to use
        """
        self.templates = templates or {}
        
        # Set default template if not provided
        if default_template:
            self.default_template = default_template
        else:
            self.default_template = (
                "You are a helpful assistant. Use the following context to answer the question.\n\n"
                "Context:\n{context}\n\n"
                "Question: {query}\n\n"
                "Answer:"
            )
        
        # Add default template if not in templates
        if "default" not in self.templates:
            self.templates["default"] = self.default_template
        
        logger.info("Prompt Composer initialized")
    
    def add_template(self, name: str, template: str) -> None:
        """Add a prompt template.
        
        Args:
            name: The name of the template
            template: The template string
        """
        self.templates[name] = template
        logger.info(f"Added prompt template: {name}")
    
    def compose(
        self,
        query: str,
        window: ContextWindow,
        template_name: str = "default"
    ) -> str:
        """Compose a prompt with context.
        
        Args:
            query: The query to compose a prompt for
            window: The context window to use
            template_name: The name of the template to use
            
        Returns:
            The composed prompt
        """
        try:
            # Get template
            template = self.templates.get(template_name, self.default_template)
            
            # Get context content
            context = window.get_content()
            
            # Format template
            prompt = template.format(context=context, query=query)
            
            logger.info(f"Composed prompt with template: {template_name}")
            return prompt
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to compose prompt",
                category=ErrorCategory.RESOURCE,
                details={"template_name": template_name, "query": query},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple prompt
            return f"Context:\n{window.get_content()}\n\nQuestion: {query}\n\nAnswer:"
