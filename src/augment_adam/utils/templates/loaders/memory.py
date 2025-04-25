"""
Memory loader for the template engine.

This module provides a loader for loading templates from memory.
"""

from typing import Dict, List, Any, Optional, Set, Union, Tuple

from augment_adam.utils.templates.core.template import Template


class MemoryLoader:
    """
    Loader for loading templates from memory.
    
    This class provides methods for loading templates from memory,
    including adding templates to memory and retrieving them.
    
    Attributes:
        templates: Dictionary of loaded templates, keyed by name.
    
    TODO(Issue #5): Add support for template inheritance
    TODO(Issue #5): Add support for template includes
    """
    
    def __init__(self) -> None:
        """Initialize the memory loader."""
        self.templates: Dict[str, Template] = {}
    
    def add_template(self, name: str, content: str) -> Template:
        """
        Add a template to memory.
        
        Args:
            name: The name of the template.
            content: The content of the template.
            
        Returns:
            The added template.
        """
        template = Template(
            name=name,
            path=name,
            content=content
        )
        
        self.templates[name] = template
        
        return template
    
    def get_template(self, template_name: str) -> Template:
        """
        Get a template by name.
        
        Args:
            template_name: The name of the template.
            
        Returns:
            The template.
            
        Raises:
            ValueError: If the template doesn't exist.
        """
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
        
        return self.templates[template_name]
    
    def get_template_names(self) -> List[str]:
        """
        Get the names of all loaded templates.
        
        Returns:
            List of template names.
        """
        return list(self.templates.keys())
    
    def remove_template(self, template_name: str) -> None:
        """
        Remove a template from memory.
        
        Args:
            template_name: The name of the template to remove.
            
        Raises:
            ValueError: If the template doesn't exist.
        """
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
        
        del self.templates[template_name]
    
    def clear_templates(self) -> None:
        """Remove all templates from memory."""
        self.templates = {}
