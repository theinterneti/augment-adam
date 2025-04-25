"""
Template engine for generating code, documentation, and tests.

This module provides a sophisticated template engine with tagging support
for generating code, documentation, and tests. It extends the Jinja2 template
engine with additional features like tag management and template inheritance.
"""

import os
import json
import re
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

class Tag:
    """
    Represents a tag that can be applied to templates and code.
    
    Tags are used to categorize and filter templates and code. They can be
    hierarchical (e.g., "memory.vector.faiss") and can have attributes.
    
    Attributes:
        name: The name of the tag.
        attributes: Optional attributes for the tag.
        parent: Optional parent tag.
    """
    
    def __init__(self, name: str, attributes: Optional[Dict[str, Any]] = None, parent: Optional['Tag'] = None):
        """
        Initialize a tag.
        
        Args:
            name: The name of the tag.
            attributes: Optional attributes for the tag.
            parent: Optional parent tag.
        """
        self.name = name
        self.attributes = attributes or {}
        self.parent = parent
        self.children: List['Tag'] = []
        
        if parent:
            parent.children.append(self)
    
    def __str__(self) -> str:
        """Return the string representation of the tag."""
        return self.name
    
    def __repr__(self) -> str:
        """Return the string representation of the tag."""
        return f"Tag({self.name}, {self.attributes})"
    
    def get_full_path(self) -> str:
        """
        Get the full hierarchical path of the tag.
        
        Returns:
            The full path of the tag (e.g., "memory.vector.faiss").
        """
        if self.parent:
            return f"{self.parent.get_full_path()}.{self.name}"
        return self.name
    
    def has_attribute(self, key: str) -> bool:
        """
        Check if the tag has a specific attribute.
        
        Args:
            key: The attribute key to check.
            
        Returns:
            True if the tag has the attribute, False otherwise.
        """
        return key in self.attributes
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get the value of a tag attribute.
        
        Args:
            key: The attribute key.
            default: The default value to return if the attribute doesn't exist.
            
        Returns:
            The attribute value or the default value.
        """
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set the value of a tag attribute.
        
        Args:
            key: The attribute key.
            value: The attribute value.
        """
        self.attributes[key] = value
    
    def is_child_of(self, tag: Union[str, 'Tag']) -> bool:
        """
        Check if this tag is a child of another tag.
        
        Args:
            tag: The parent tag to check against.
            
        Returns:
            True if this tag is a child of the specified tag, False otherwise.
        """
        if isinstance(tag, str):
            tag_name = tag
        else:
            tag_name = tag.name
            
        if self.parent is None:
            return False
            
        if self.parent.name == tag_name:
            return True
            
        return self.parent.is_child_of(tag_name)


class TagManager:
    """
    Manages tags for templates and code.
    
    The TagManager is responsible for creating, retrieving, and organizing tags.
    It maintains a hierarchical structure of tags and provides methods for
    filtering and searching tags.
    
    Attributes:
        tags: Dictionary of all tags, keyed by name.
    """
    
    def __init__(self):
        """Initialize the tag manager."""
        self.tags: Dict[str, Tag] = {}
    
    def create_tag(self, name: str, attributes: Optional[Dict[str, Any]] = None, 
                  parent: Optional[Union[str, Tag]] = None) -> Tag:
        """
        Create a new tag.
        
        Args:
            name: The name of the tag.
            attributes: Optional attributes for the tag.
            parent: Optional parent tag or parent tag name.
            
        Returns:
            The created tag.
            
        Raises:
            ValueError: If a tag with the same name already exists.
        """
        if name in self.tags:
            raise ValueError(f"Tag '{name}' already exists")
        
        parent_tag = None
        if parent:
            if isinstance(parent, str):
                if parent not in self.tags:
                    raise ValueError(f"Parent tag '{parent}' does not exist")
                parent_tag = self.tags[parent]
            else:
                parent_tag = parent
        
        tag = Tag(name, attributes, parent_tag)
        self.tags[name] = tag
        return tag
    
    def get_tag(self, name: str) -> Optional[Tag]:
        """
        Get a tag by name.
        
        Args:
            name: The name of the tag.
            
        Returns:
            The tag or None if it doesn't exist.
        """
        return self.tags.get(name)
    
    def get_or_create_tag(self, name: str, attributes: Optional[Dict[str, Any]] = None, 
                         parent: Optional[Union[str, Tag]] = None) -> Tag:
        """
        Get a tag by name or create it if it doesn't exist.
        
        Args:
            name: The name of the tag.
            attributes: Optional attributes for the tag if it needs to be created.
            parent: Optional parent tag or parent tag name if it needs to be created.
            
        Returns:
            The existing or created tag.
        """
        tag = self.get_tag(name)
        if tag:
            return tag
        return self.create_tag(name, attributes, parent)
    
    def delete_tag(self, name: str) -> None:
        """
        Delete a tag by name.
        
        Args:
            name: The name of the tag.
            
        Raises:
            ValueError: If the tag doesn't exist.
        """
        if name not in self.tags:
            raise ValueError(f"Tag '{name}' does not exist")
        
        tag = self.tags[name]
        
        # Update parent's children list
        if tag.parent:
            tag.parent.children.remove(tag)
        
        # Recursively delete children
        for child in tag.children[:]:  # Create a copy to avoid modification during iteration
            self.delete_tag(child.name)
        
        # Remove the tag
        del self.tags[name]
    
    def get_tags_by_attribute(self, key: str, value: Optional[Any] = None) -> List[Tag]:
        """
        Get tags that have a specific attribute.
        
        Args:
            key: The attribute key.
            value: Optional attribute value to match.
            
        Returns:
            List of tags that have the specified attribute.
        """
        result = []
        for tag in self.tags.values():
            if tag.has_attribute(key):
                if value is None or tag.get_attribute(key) == value:
                    result.append(tag)
        return result
    
    def get_children(self, name: str) -> List[Tag]:
        """
        Get all children of a tag.
        
        Args:
            name: The name of the parent tag.
            
        Returns:
            List of child tags.
            
        Raises:
            ValueError: If the parent tag doesn't exist.
        """
        if name not in self.tags:
            raise ValueError(f"Tag '{name}' does not exist")
        
        return self.tags[name].children
    
    def get_all_tags(self) -> List[Tag]:
        """
        Get all tags.
        
        Returns:
            List of all tags.
        """
        return list(self.tags.values())
    
    def get_root_tags(self) -> List[Tag]:
        """
        Get all root tags (tags without parents).
        
        Returns:
            List of root tags.
        """
        return [tag for tag in self.tags.values() if tag.parent is None]
    
    def load_from_json(self, json_file: Union[str, Path]) -> None:
        """
        Load tags from a JSON file.
        
        Args:
            json_file: Path to the JSON file.
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist.
            json.JSONDecodeError: If the JSON file is invalid.
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # First pass: Create all tags without parents
        for name, info in data.items():
            attributes = info.get('attributes', {})
            self.get_or_create_tag(name, attributes)
        
        # Second pass: Set parent-child relationships
        for name, info in data.items():
            if 'parent' in info:
                parent_name = info['parent']
                tag = self.get_tag(name)
                parent_tag = self.get_tag(parent_name)
                
                if tag and parent_tag:
                    # Update parent reference
                    tag.parent = parent_tag
                    
                    # Update parent's children list
                    if tag not in parent_tag.children:
                        parent_tag.children.append(tag)
    
    def save_to_json(self, json_file: Union[str, Path]) -> None:
        """
        Save tags to a JSON file.
        
        Args:
            json_file: Path to the JSON file.
        """
        data = {}
        for name, tag in self.tags.items():
            info = {
                'attributes': tag.attributes
            }
            
            if tag.parent:
                info['parent'] = tag.parent.name
            
            data[name] = info
        
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)


class TemplateEngine:
    """
    Enhanced template engine with tagging support.
    
    This class extends the Jinja2 template engine with additional features
    like tag management and template inheritance. It provides methods for
    rendering templates with tags and managing template metadata.
    
    Attributes:
        env: The Jinja2 environment.
        tag_manager: The tag manager for template tags.
        templates_dir: The directory containing the templates.
    """
    
    def __init__(self, templates_dir: Optional[str] = None, tag_manager: Optional[TagManager] = None):
        """
        Initialize the template engine.
        
        Args:
            templates_dir: Directory containing the templates. If None, uses the default templates directory.
            tag_manager: Optional tag manager. If None, creates a new one.
        """
        if templates_dir is None:
            # Use the default templates directory
            package_dir = Path(__file__).parent.parent.parent
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
        
        self.tag_manager = tag_manager or TagManager()
        
        # Load template metadata
        self.template_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_template_metadata()
    
    def _load_template_metadata(self) -> None:
        """
        Load metadata for all templates.
        
        This method scans all template files and extracts metadata from
        the template comments.
        """
        for root, _, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.j2'):
                    template_path = os.path.join(root, file)
                    relative_path = os.path.relpath(template_path, self.templates_dir)
                    
                    with open(template_path, 'r') as f:
                        content = f.read()
                    
                    # Extract metadata from template comments
                    metadata = self._extract_metadata(content)
                    self.template_metadata[relative_path] = metadata
                    
                    # Create tags for the template
                    if 'tags' in metadata:
                        for tag_name in metadata['tags']:
                            self.tag_manager.get_or_create_tag(tag_name)
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from template content.
        
        Args:
            content: The template content.
            
        Returns:
            Dictionary of metadata.
        """
        metadata = {}
        
        # Extract metadata from template comments
        # Format: {# @key: value #}
        pattern = r'{#\s*@(\w+):\s*(.+?)\s*#}'
        for match in re.finditer(pattern, content):
            key, value = match.groups()
            
            # Handle special metadata types
            if key == 'tags':
                # Tags are comma-separated
                metadata[key] = [tag.strip() for tag in value.split(',')]
            elif key == 'variables':
                # Variables are comma-separated key:type pairs
                variables = {}
                for var in value.split(','):
                    var = var.strip()
                    if ':' in var:
                        var_name, var_type = var.split(':', 1)
                        variables[var_name.strip()] = var_type.strip()
                metadata[key] = variables
            else:
                metadata[key] = value
        
        return metadata
    
    def get_template_metadata(self, template_name: str) -> Dict[str, Any]:
        """
        Get metadata for a template.
        
        Args:
            template_name: The name of the template.
            
        Returns:
            Dictionary of template metadata.
        """
        return self.template_metadata.get(template_name, {})
    
    def get_templates_by_tag(self, tag_name: str) -> List[str]:
        """
        Get templates that have a specific tag.
        
        Args:
            tag_name: The name of the tag.
            
        Returns:
            List of template names.
        """
        result = []
        for template_name, metadata in self.template_metadata.items():
            if 'tags' in metadata and tag_name in metadata['tags']:
                result.append(template_name)
        return result
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered template.
            
        Raises:
            jinja2.exceptions.TemplateNotFound: If the template doesn't exist.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string_template(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with the given context.
        
        Args:
            template_string: Template string to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered template.
        """
        template = Template(template_string, environment=self.env)
        return template.render(**context)
    
    def get_docstring(self, docstring_type: str, summary: str, **kwargs) -> str:
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
    
    def render_code_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a code template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered code.
        """
        return self.render_template(f"code/{template_name}", context)
    
    def render_test_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a test template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered test.
        """
        return self.render_template(f"tests/{template_name}", context)
    
    def render_doc_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a documentation template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered documentation.
        """
        return self.render_template(f"docs/{template_name}", context)
    
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

def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render a template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered template.
    """
    return get_template_engine().render_template(template_name, context)

def render_code_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render a code template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered code.
    """
    return get_template_engine().render_code_template(template_name, context)

def render_test_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render a test template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered test.
    """
    return get_template_engine().render_test_template(template_name, context)

def render_doc_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render a documentation template with the given context.
    
    Args:
        template_name: Name of the template to render.
        context: Context to use for rendering the template.
        
    Returns:
        Rendered documentation.
    """
    return get_template_engine().render_doc_template(template_name, context)

def get_docstring(docstring_type: str, summary: str, **kwargs) -> str:
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
