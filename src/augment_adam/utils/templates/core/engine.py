"""
Template engine for generating code, documentation, and tests.

This module provides a sophisticated template engine with tagging support
for generating code, documentation, and tests. It extends the Jinja2 template
engine with additional features like tag management and template inheritance.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Set, Union, Tuple, Callable
from pathlib import Path
import jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template as Jinja2Template

from augment_adam.utils.tagging import Tag, TagCategory, get_tag, get_or_create_tag
from augment_adam.utils.templates.core.metadata import TemplateMetadata, extract_metadata_from_content
from augment_adam.utils.templates.core.template import Template, TemplateContext


class TemplateEngine:
    """
    Enhanced template engine with tagging support.
    
    This class extends the Jinja2 template engine with additional features
    like tag management and template inheritance. It provides methods for
    rendering templates with tags and managing template metadata.
    
    Attributes:
        env: The Jinja2 environment.
        templates_dir: The directory containing the templates.
        templates: Dictionary of loaded templates, keyed by name.
        template_metadata: Dictionary of template metadata, keyed by name.
    
    TODO(Issue #5): Add support for template versioning
    TODO(Issue #5): Add support for template validation
    TODO(Issue #5): Add support for template analytics
    """
    
    def __init__(self, templates_dir: Optional[str] = None) -> None:
        """
        Initialize the template engine.
        
        Args:
            templates_dir: Directory containing the templates. If None, uses the default templates directory.
        """
        if templates_dir is None:
            # Use the default templates directory
            package_dir = Path(__file__).parent.parent.parent.parent.parent
            templates_dir = os.path.join(package_dir, "templates")
        
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['tojson'] = lambda obj: json.dumps(obj)
        self.env.filters['to_camel_case'] = self._to_camel_case
        self.env.filters['to_snake_case'] = self._to_snake_case
        self.env.filters['to_pascal_case'] = self._to_pascal_case
        self.env.filters['to_kebab_case'] = self._to_kebab_case
        
        # Add custom globals
        self.env.globals['get_docstring'] = self.get_docstring
        
        # Load templates
        self.templates: Dict[str, Template] = {}
        self.template_metadata: Dict[str, TemplateMetadata] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """
        Load all templates from the templates directory.
        
        This method scans all template files and loads them into memory,
        extracting metadata from the template comments.
        """
        for root, _, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.j2') or file.endswith('.jinja2'):
                    template_path = os.path.join(root, file)
                    relative_path = os.path.relpath(template_path, self.templates_dir)
                    
                    try:
                        template = Template.from_file(template_path, self.env)
                        self.templates[relative_path] = template
                        self.template_metadata[relative_path] = template.metadata
                    except Exception as e:
                        print(f"Error loading template {template_path}: {e}")
    
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
    
    def get_template_metadata(self, template_name: str) -> TemplateMetadata:
        """
        Get metadata for a template.
        
        Args:
            template_name: The name of the template.
            
        Returns:
            The template metadata.
            
        Raises:
            ValueError: If the template doesn't exist.
        """
        if template_name not in self.template_metadata:
            raise ValueError(f"Template not found: {template_name}")
        
        return self.template_metadata[template_name]
    
    def get_templates_by_tag(self, tag_name: str) -> List[str]:
        """
        Get templates that have a specific tag.
        
        Args:
            tag_name: The name of the tag.
            
        Returns:
            List of template names.
        """
        result = []
        tag = get_tag(tag_name)
        
        if tag is None:
            return result
        
        for template_name, metadata in self.template_metadata.items():
            if tag in metadata.tags:
                result.append(template_name)
        
        return result
    
    def render_template(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered template.
            
        Raises:
            ValueError: If the template doesn't exist.
        """
        template = self.get_template(template_name)
        return template.render(context)
    
    def render_string_template(self, template_string: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template string with the given context.
        
        Args:
            template_string: Template string to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered template.
        """
        if isinstance(context, TemplateContext):
            context_dict = context.to_dict()
        else:
            context_dict = context
        
        template = self.env.from_string(template_string)
        return template.render(**context_dict)
    
    def get_docstring(self, docstring_type: str, summary: str, **kwargs: Any) -> str:
        """
        Generate a Google-style docstring.
        
        Args:
            docstring_type: Type of docstring to generate (e.g., "function", "class", "module").
            summary: Summary of the docstring.
            **kwargs: Additional context for the docstring.
            
        Returns:
            Generated docstring.
        """
        context = {
            "docstring_type": docstring_type,
            "summary": summary,
            **kwargs
        }
        return self.render_template("docstring_template.j2", context)
    
    def render_code_template(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a code template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered code.
        """
        return self.render_template(f"code/{template_name}", context)
    
    def render_test_template(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a test template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered test.
        """
        return self.render_template(f"tests/{template_name}", context)
    
    def render_doc_template(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a documentation template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered documentation.
        """
        return self.render_template(f"docs/{template_name}", context)
    
    def reload_templates(self) -> None:
        """Reload all templates from the templates directory."""
        self.templates = {}
        self.template_metadata = {}
        self._load_templates()
    
    def add_filter(self, name: str, filter_func: Callable) -> None:
        """
        Add a custom filter to the template engine.
        
        Args:
            name: The name of the filter.
            filter_func: The filter function.
        """
        self.env.filters[name] = filter_func
    
    def add_global(self, name: str, value: Any) -> None:
        """
        Add a global variable to the template engine.
        
        Args:
            name: The name of the global variable.
            value: The value of the global variable.
        """
        self.env.globals[name] = value
    
    @staticmethod
    def _to_camel_case(s: str) -> str:
        """
        Convert a string to camelCase.
        
        Args:
            s: The input string.
            
        Returns:
            The string in camelCase.
        """
        s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
        words = s.split()
        if not words:
            return ''
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    @staticmethod
    def _to_snake_case(s: str) -> str:
        """
        Convert a string to snake_case.
        
        Args:
            s: The input string.
            
        Returns:
            The string in snake_case.
        """
        s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
        return '_'.join(word.lower() for word in s.split())
    
    @staticmethod
    def _to_pascal_case(s: str) -> str:
        """
        Convert a string to PascalCase.
        
        Args:
            s: The input string.
            
        Returns:
            The string in PascalCase.
        """
        s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
        return ''.join(word.capitalize() for word in s.split())
    
    @staticmethod
    def _to_kebab_case(s: str) -> str:
        """
        Convert a string to kebab-case.
        
        Args:
            s: The input string.
            
        Returns:
            The string in kebab-case.
        """
        s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
        return '-'.join(word.lower() for word in s.split())


# Singleton instance
_template_engine: Optional[TemplateEngine] = None

def get_template_engine() -> TemplateEngine:
    """
    Get the singleton instance of the template engine.
    
    Returns:
        The template engine instance.
    """
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
    return _template_engine

def render_template(template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
    """
    Render a template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered template.
    """
    return get_template_engine().render_template(template_name, context)

def render_string_template(template_string: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
    """
    Render a template string with the given context.
    
    Args:
        template_string: Template string to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered template.
    """
    return get_template_engine().render_string_template(template_string, context)

def render_code_template(template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
    """
    Render a code template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered code.
    """
    return get_template_engine().render_code_template(template_name, context)

def render_test_template(template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
    """
    Render a test template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered test.
    """
    return get_template_engine().render_test_template(template_name, context)

def render_doc_template(template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
    """
    Render a documentation template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered documentation.
    """
    return get_template_engine().render_doc_template(template_name, context)

def get_docstring(docstring_type: str, summary: str, **kwargs: Any) -> str:
    """
    Generate a Google-style docstring.
    
    Args:
        docstring_type: Type of docstring to generate (e.g., "function", "class", "module").
        summary: Summary of the docstring.
        **kwargs: Additional context for the docstring.
        
    Returns:
        Generated docstring.
    """
    return get_template_engine().get_docstring(docstring_type, summary, **kwargs)
