"""
Filesystem loader for the template engine.

This module provides a loader for loading templates from the filesystem.
"""

import os
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from pathlib import Path

from augment_adam.utils.templates.core.template import Template


class FileSystemLoader:
    """
    Loader for loading templates from the filesystem.
    
    This class provides methods for loading templates from the filesystem,
    including scanning directories for templates and loading individual templates.
    
    Attributes:
        templates_dir: The directory containing the templates.
        templates: Dictionary of loaded templates, keyed by name.
    
    TODO(Issue #5): Add support for template inheritance
    TODO(Issue #5): Add support for template includes
    """
    
    def __init__(self, templates_dir: Union[str, Path]) -> None:
        """
        Initialize the filesystem loader.
        
        Args:
            templates_dir: Directory containing the templates.
        """
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Template] = {}
    
    def load_template(self, template_path: Union[str, Path]) -> Template:
        """
        Load a template from the filesystem.
        
        Args:
            template_path: Path to the template file, relative to the templates directory.
            
        Returns:
            The loaded template.
            
        Raises:
            FileNotFoundError: If the template file doesn't exist.
        """
        template_path = Path(template_path)
        full_path = self.templates_dir / template_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Template file not found: {full_path}")
        
        template = Template.from_file(full_path)
        self.templates[str(template_path)] = template
        
        return template
    
    def load_templates(self, pattern: str = '*.j2') -> Dict[str, Template]:
        """
        Load all templates matching a pattern from the templates directory.
        
        Args:
            pattern: Glob pattern for matching template files.
            
        Returns:
            Dictionary of loaded templates, keyed by name.
        """
        self.templates = {}
        
        for template_file in self.templates_dir.glob(f'**/{pattern}'):
            relative_path = template_file.relative_to(self.templates_dir)
            try:
                template = Template.from_file(template_file)
                self.templates[str(relative_path)] = template
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
        
        return self.templates
    
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
            # Try to load the template
            try:
                return self.load_template(template_name)
            except FileNotFoundError:
                raise ValueError(f"Template not found: {template_name}")
        
        return self.templates[template_name]
    
    def get_template_names(self) -> List[str]:
        """
        Get the names of all loaded templates.
        
        Returns:
            List of template names.
        """
        return list(self.templates.keys())
    
    def reload_template(self, template_name: str) -> Template:
        """
        Reload a template from the filesystem.
        
        Args:
            template_name: The name of the template.
            
        Returns:
            The reloaded template.
            
        Raises:
            ValueError: If the template doesn't exist.
        """
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
        
        return self.load_template(template_name)
    
    def reload_templates(self, pattern: str = '*.j2') -> Dict[str, Template]:
        """
        Reload all templates matching a pattern from the templates directory.
        
        Args:
            pattern: Glob pattern for matching template files.
            
        Returns:
            Dictionary of reloaded templates, keyed by name.
        """
        return self.load_templates(pattern)
