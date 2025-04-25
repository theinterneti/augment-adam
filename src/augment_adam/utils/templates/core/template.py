"""
Template class for the template engine.

This module provides the Template class, which represents a template
in the template engine.
"""

import os
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from pathlib import Path
import jinja2

from augment_adam.utils.templates.core.metadata import TemplateMetadata, extract_metadata_from_content


@dataclass
class TemplateContext:
    """
    Context for rendering a template.
    
    This class represents the context for rendering a template, including
    variables, filters, and other context information.
    
    Attributes:
        variables: Dictionary of variables to use for rendering.
        filters: Dictionary of custom filters to use for rendering.
        globals: Dictionary of global variables to use for rendering.
        extensions: List of Jinja2 extensions to use for rendering.
        custom_context: Dictionary of custom context information.
    
    TODO(Issue #5): Add validation for context variables against template metadata
    TODO(Issue #5): Add support for context inheritance
    """
    
    variables: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    globals: Dict[str, Any] = field(default_factory=dict)
    extensions: List[str] = field(default_factory=list)
    custom_context: Dict[str, Any] = field(default_factory=dict)
    
    def add_variable(self, name: str, value: Any) -> None:
        """
        Add a variable to the context.
        
        Args:
            name: The name of the variable.
            value: The value of the variable.
        """
        self.variables[name] = value
    
    def remove_variable(self, name: str) -> None:
        """
        Remove a variable from the context.
        
        Args:
            name: The name of the variable to remove.
        """
        if name in self.variables:
            del self.variables[name]
    
    def has_variable(self, name: str) -> bool:
        """
        Check if the context has a specific variable.
        
        Args:
            name: The name of the variable to check.
            
        Returns:
            True if the context has the variable, False otherwise.
        """
        return name in self.variables
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get the value of a variable.
        
        Args:
            name: The name of the variable.
            default: The default value to return if the variable doesn't exist.
            
        Returns:
            The value of the variable, or the default value if the variable doesn't exist.
        """
        return self.variables.get(name, default)
    
    def add_filter(self, name: str, filter_func: Any) -> None:
        """
        Add a filter to the context.
        
        Args:
            name: The name of the filter.
            filter_func: The filter function.
        """
        self.filters[name] = filter_func
    
    def remove_filter(self, name: str) -> None:
        """
        Remove a filter from the context.
        
        Args:
            name: The name of the filter to remove.
        """
        if name in self.filters:
            del self.filters[name]
    
    def has_filter(self, name: str) -> bool:
        """
        Check if the context has a specific filter.
        
        Args:
            name: The name of the filter to check.
            
        Returns:
            True if the context has the filter, False otherwise.
        """
        return name in self.filters
    
    def get_filter(self, name: str, default: Any = None) -> Any:
        """
        Get a filter function.
        
        Args:
            name: The name of the filter.
            default: The default value to return if the filter doesn't exist.
            
        Returns:
            The filter function, or the default value if the filter doesn't exist.
        """
        return self.filters.get(name, default)
    
    def add_global(self, name: str, value: Any) -> None:
        """
        Add a global variable to the context.
        
        Args:
            name: The name of the global variable.
            value: The value of the global variable.
        """
        self.globals[name] = value
    
    def remove_global(self, name: str) -> None:
        """
        Remove a global variable from the context.
        
        Args:
            name: The name of the global variable to remove.
        """
        if name in self.globals:
            del self.globals[name]
    
    def has_global(self, name: str) -> bool:
        """
        Check if the context has a specific global variable.
        
        Args:
            name: The name of the global variable to check.
            
        Returns:
            True if the context has the global variable, False otherwise.
        """
        return name in self.globals
    
    def get_global(self, name: str, default: Any = None) -> Any:
        """
        Get the value of a global variable.
        
        Args:
            name: The name of the global variable.
            default: The default value to return if the global variable doesn't exist.
            
        Returns:
            The value of the global variable, or the default value if the global variable doesn't exist.
        """
        return self.globals.get(name, default)
    
    def add_extension(self, extension: str) -> None:
        """
        Add an extension to the context.
        
        Args:
            extension: The name of the extension to add.
        """
        if extension not in self.extensions:
            self.extensions.append(extension)
    
    def remove_extension(self, extension: str) -> None:
        """
        Remove an extension from the context.
        
        Args:
            extension: The name of the extension to remove.
        """
        if extension in self.extensions:
            self.extensions.remove(extension)
    
    def has_extension(self, extension: str) -> bool:
        """
        Check if the context has a specific extension.
        
        Args:
            extension: The name of the extension to check.
            
        Returns:
            True if the context has the extension, False otherwise.
        """
        return extension in self.extensions
    
    def set_custom_context(self, key: str, value: Any) -> None:
        """
        Set a custom context value.
        
        Args:
            key: The key for the custom context.
            value: The value for the custom context.
        """
        self.custom_context[key] = value
    
    def get_custom_context(self, key: str, default: Any = None) -> Any:
        """
        Get a custom context value.
        
        Args:
            key: The key for the custom context.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The custom context value, or the default value if the key doesn't exist.
        """
        return self.custom_context.get(key, default)
    
    def remove_custom_context(self, key: str) -> None:
        """
        Remove a custom context value.
        
        Args:
            key: The key for the custom context to remove.
        """
        if key in self.custom_context:
            del self.custom_context[key]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary for rendering.
        
        Returns:
            Dictionary representation of the context.
        """
        return {**self.variables, **self.custom_context}


class Template:
    """
    Template for the template engine.
    
    This class represents a template in the template engine, including
    its content, metadata, and rendering capabilities.
    
    Attributes:
        name: The name of the template.
        path: The path to the template file.
        content: The content of the template.
        metadata: The metadata for the template.
        jinja_template: The Jinja2 template object.
    
    TODO(Issue #5): Add support for template inheritance
    TODO(Issue #5): Add support for template includes
    TODO(Issue #5): Add support for template macros
    """
    
    def __init__(self, name: str, path: str, content: str, 
                environment: Optional[jinja2.Environment] = None) -> None:
        """
        Initialize the template.
        
        Args:
            name: The name of the template.
            path: The path to the template file.
            content: The content of the template.
            environment: Optional Jinja2 environment to use for rendering.
        """
        self.name = name
        self.path = path
        self.content = content
        self.metadata = extract_metadata_from_content(content, name, path)
        
        # Create Jinja2 template
        if environment is None:
            environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(path)),
                autoescape=jinja2.select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
        
        self.jinja_template = environment.from_string(content)
    
    def render(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render the template with the given context.
        
        Args:
            context: The context to use for rendering.
            
        Returns:
            The rendered template.
        """
        if isinstance(context, TemplateContext):
            context_dict = context.to_dict()
        else:
            context_dict = context
        
        return self.jinja_template.render(**context_dict)
    
    def validate_context(self, context: Union[Dict[str, Any], TemplateContext]) -> List[str]:
        """
        Validate the context against the template metadata.
        
        Args:
            context: The context to validate.
            
        Returns:
            List of validation errors, or an empty list if the context is valid.
        """
        errors = []
        
        # Convert context to dictionary if it's a TemplateContext
        if isinstance(context, TemplateContext):
            context_dict = context.variables
        else:
            context_dict = context
        
        # Check for required variables
        for var_name, var_type in self.metadata.variables.items():
            if var_name not in context_dict:
                errors.append(f"Missing required variable: {var_name}")
        
        return errors
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path], 
                 environment: Optional[jinja2.Environment] = None) -> 'Template':
        """
        Create a template from a file.
        
        Args:
            file_path: The path to the template file.
            environment: Optional Jinja2 environment to use for rendering.
            
        Returns:
            Template object.
            
        Raises:
            FileNotFoundError: If the template file doesn't exist.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        return cls(
            name=file_path.stem,
            path=str(file_path),
            content=content,
            environment=environment
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template to a dictionary.
        
        Returns:
            Dictionary representation of the template.
        """
        return {
            "name": self.name,
            "path": self.path,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
        }
