"""
Package loader for the template engine.

This module provides a loader for loading templates from Python packages.
"""

import os
import importlib.resources
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from pathlib import Path

from augment_adam.utils.templates.core.template import Template


class PackageLoader:
    """
    Loader for loading templates from Python packages.
    
    This class provides methods for loading templates from Python packages,
    including scanning packages for templates and loading individual templates.
    
    Attributes:
        package: The package containing the templates.
        templates_dir: The directory within the package containing the templates.
        templates: Dictionary of loaded templates, keyed by name.
    
    TODO(Issue #5): Add support for template inheritance
    TODO(Issue #5): Add support for template includes
    """
    
    def __init__(self, package: str, templates_dir: str = 'templates') -> None:
        """
        Initialize the package loader.
        
        Args:
            package: The package containing the templates.
            templates_dir: The directory within the package containing the templates.
        """
        self.package = package
        self.templates_dir = templates_dir
        self.templates: Dict[str, Template] = {}
    
    def load_template(self, template_name: str) -> Template:
        """
        Load a template from the package.
        
        Args:
            template_name: Name of the template file, relative to the templates directory.
            
        Returns:
            The loaded template.
            
        Raises:
            FileNotFoundError: If the template file doesn't exist.
        """
        template_path = os.path.join(self.templates_dir, template_name)
        
        try:
            with importlib.resources.open_text(self.package, template_path) as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        template = Template(
            name=template_name,
            path=template_path,
            content=content
        )
        
        self.templates[template_name] = template
        
        return template
    
    def load_templates(self, pattern: str = '*.j2') -> Dict[str, Template]:
        """
        Load all templates matching a pattern from the package.
        
        Args:
            pattern: Glob pattern for matching template files.
            
        Returns:
            Dictionary of loaded templates, keyed by name.
        """
        self.templates = {}
        
        # This is a simplified implementation
        # In a real implementation, you would use importlib.resources to scan the package
        # for templates matching the pattern
        
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
        Reload a template from the package.
        
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
        Reload all templates matching a pattern from the package.
        
        Args:
            pattern: Glob pattern for matching template files.
            
        Returns:
            Dictionary of reloaded templates, keyed by name.
        """
        return self.load_templates(pattern)
