"""
Template metadata handling.

This module provides classes and utilities for handling template metadata,
including parsing metadata from template comments and validating metadata.
"""

import re
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from datetime import datetime

from augment_adam.utils.tagging import Tag, TagCategory, get_tag, get_or_create_tag


@dataclass
class TemplateMetadata:
    """
    Metadata for a template.
    
    This class represents the metadata for a template, including tags,
    description, variables, and other metadata extracted from template comments.
    
    Attributes:
        name: The name of the template.
        path: The path to the template file.
        tags: List of tags associated with the template.
        description: Description of the template.
        variables: Dictionary of variables used in the template, with their types.
        author: Author of the template.
        created_at: When the template was created.
        updated_at: When the template was last updated.
        version: Version of the template.
        examples: List of example usages of the template.
        related_templates: List of related templates.
        custom_metadata: Dictionary of custom metadata.
    
    TODO(Issue #5): Add validation for metadata
    TODO(Issue #5): Add support for metadata inheritance
    """
    
    name: str
    path: str
    tags: List[Tag] = field(default_factory=list)
    description: str = ""
    variables: Dict[str, str] = field(default_factory=dict)
    author: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: str = "1.0.0"
    examples: List[str] = field(default_factory=list)
    related_templates: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize the template metadata with timestamps."""
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def add_tag(self, tag_name: str) -> None:
        """
        Add a tag to the template.
        
        Args:
            tag_name: The name of the tag to add.
        """
        tag = get_tag(tag_name)
        if tag is None:
            # Try to infer the category
            if "code" in tag_name or "class" in tag_name or "function" in tag_name:
                category = TagCategory.TEMPLATE
            elif "test" in tag_name:
                category = TagCategory.TEST
            elif "doc" in tag_name or "documentation" in tag_name:
                category = TagCategory.DOCUMENTATION
            else:
                category = TagCategory.UTILITY
            
            tag = get_or_create_tag(tag_name, category)
        
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag_name: str) -> None:
        """
        Remove a tag from the template.
        
        Args:
            tag_name: The name of the tag to remove.
        """
        tag = get_tag(tag_name)
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag_name: str) -> bool:
        """
        Check if the template has a specific tag.
        
        Args:
            tag_name: The name of the tag to check.
            
        Returns:
            True if the template has the tag, False otherwise.
        """
        tag = get_tag(tag_name)
        return tag in self.tags
    
    def add_variable(self, name: str, type_hint: str) -> None:
        """
        Add a variable to the template.
        
        Args:
            name: The name of the variable.
            type_hint: The type hint for the variable.
        """
        self.variables[name] = type_hint
    
    def remove_variable(self, name: str) -> None:
        """
        Remove a variable from the template.
        
        Args:
            name: The name of the variable to remove.
        """
        if name in self.variables:
            del self.variables[name]
    
    def has_variable(self, name: str) -> bool:
        """
        Check if the template has a specific variable.
        
        Args:
            name: The name of the variable to check.
            
        Returns:
            True if the template has the variable, False otherwise.
        """
        return name in self.variables
    
    def get_variable_type(self, name: str) -> Optional[str]:
        """
        Get the type hint for a variable.
        
        Args:
            name: The name of the variable.
            
        Returns:
            The type hint for the variable, or None if the variable doesn't exist.
        """
        return self.variables.get(name)
    
    def add_example(self, example: str) -> None:
        """
        Add an example usage to the template.
        
        Args:
            example: The example usage to add.
        """
        if example not in self.examples:
            self.examples.append(example)
    
    def remove_example(self, example: str) -> None:
        """
        Remove an example usage from the template.
        
        Args:
            example: The example usage to remove.
        """
        if example in self.examples:
            self.examples.remove(example)
    
    def add_related_template(self, template_name: str) -> None:
        """
        Add a related template to the template.
        
        Args:
            template_name: The name of the related template to add.
        """
        if template_name not in self.related_templates:
            self.related_templates.append(template_name)
    
    def remove_related_template(self, template_name: str) -> None:
        """
        Remove a related template from the template.
        
        Args:
            template_name: The name of the related template to remove.
        """
        if template_name in self.related_templates:
            self.related_templates.remove(template_name)
    
    def set_custom_metadata(self, key: str, value: Any) -> None:
        """
        Set a custom metadata value.
        
        Args:
            key: The key for the custom metadata.
            value: The value for the custom metadata.
        """
        self.custom_metadata[key] = value
    
    def get_custom_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a custom metadata value.
        
        Args:
            key: The key for the custom metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The custom metadata value, or the default value if the key doesn't exist.
        """
        return self.custom_metadata.get(key, default)
    
    def remove_custom_metadata(self, key: str) -> None:
        """
        Remove a custom metadata value.
        
        Args:
            key: The key for the custom metadata to remove.
        """
        if key in self.custom_metadata:
            del self.custom_metadata[key]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template metadata to a dictionary.
        
        Returns:
            Dictionary representation of the template metadata.
        """
        return {
            "name": self.name,
            "path": self.path,
            "tags": [tag.name for tag in self.tags],
            "description": self.description,
            "variables": self.variables,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "examples": self.examples,
            "related_templates": self.related_templates,
            "custom_metadata": self.custom_metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """
        Create a template metadata object from a dictionary.
        
        Args:
            data: Dictionary representation of the template metadata.
            
        Returns:
            Template metadata object.
        """
        metadata = cls(
            name=data["name"],
            path=data["path"],
            description=data.get("description", ""),
            variables=data.get("variables", {}),
            author=data.get("author", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            version=data.get("version", "1.0.0"),
            examples=data.get("examples", []),
            related_templates=data.get("related_templates", []),
            custom_metadata=data.get("custom_metadata", {}),
        )
        
        # Add tags
        for tag_name in data.get("tags", []):
            metadata.add_tag(tag_name)
        
        return metadata


def extract_metadata_from_content(content: str, template_name: str, template_path: str) -> TemplateMetadata:
    """
    Extract metadata from template content.
    
    Args:
        content: The template content.
        template_name: The name of the template.
        template_path: The path to the template file.
        
    Returns:
        Template metadata object.
    """
    metadata = TemplateMetadata(name=template_name, path=template_path)
    
    # Extract metadata from template comments
    # Format: {# @key: value #}
    pattern = r'{#\s*@(\w+):\s*(.+?)\s*#}'
    for match in re.finditer(pattern, content):
        key, value = match.groups()
        
        # Handle special metadata types
        if key == "tags":
            # Tags are comma-separated
            for tag_name in value.split(","):
                metadata.add_tag(tag_name.strip())
        elif key == "variables":
            # Variables are comma-separated key:type pairs
            for var in value.split(","):
                var = var.strip()
                if ":" in var:
                    var_name, var_type = var.split(":", 1)
                    metadata.add_variable(var_name.strip(), var_type.strip())
        elif key == "examples":
            # Examples are separated by |
            for example in value.split("|"):
                metadata.add_example(example.strip())
        elif key == "related_templates":
            # Related templates are comma-separated
            for template in value.split(","):
                metadata.add_related_template(template.strip())
        elif key == "description":
            metadata.description = value
        elif key == "author":
            metadata.author = value
        elif key == "version":
            metadata.version = value
        else:
            # Custom metadata
            metadata.set_custom_metadata(key, value)
    
    return metadata
