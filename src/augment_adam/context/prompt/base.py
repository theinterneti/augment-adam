"""
Base classes for the prompt module.

This module provides the base classes for the prompt module, including
the PromptTemplate class and PromptManager class.
"""

import re
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.context.core.base import Context, ContextType


@tag("context.prompt")
class PromptTemplate:
    """
    Template for generating prompts.
    
    This class represents a template for generating prompts, including
    variables, context placeholders, and formatting options.
    
    Attributes:
        id: Unique identifier for the prompt template.
        name: The name of the prompt template.
        template: The template string.
        variables: Dictionary of variables used in the template.
        metadata: Additional metadata for the prompt template.
        created_at: When the prompt template was created.
        updated_at: When the prompt template was last updated.
        tags: List of tags for the prompt template.
    
    TODO(Issue #7): Add support for prompt template versioning
    TODO(Issue #7): Implement prompt template validation
    """
    
    def __init__(
        self,
        name: str,
        template: str,
        variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        Initialize the prompt template.
        
        Args:
            name: The name of the prompt template.
            template: The template string.
            variables: Dictionary of variables used in the template.
            metadata: Additional metadata for the prompt template.
            tags: List of tags for the prompt template.
            id: Unique identifier for the prompt template.
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.template = template
        self.variables = variables or {}
        self.metadata = metadata or {}
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.tags = tags or []
    
    def render(self, variables: Optional[Dict[str, Any]] = None, contexts: Optional[List[Context]] = None) -> str:
        """
        Render the prompt template with variables and contexts.
        
        Args:
            variables: Dictionary of variables to use for rendering.
            contexts: List of contexts to include in the prompt.
            
        Returns:
            Rendered prompt.
        """
        # Combine template variables with provided variables
        all_variables = self.variables.copy()
        if variables:
            all_variables.update(variables)
        
        # Render the template with variables
        rendered = self.template
        
        # Replace variable placeholders
        for key, value in all_variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        # Replace context placeholders
        if contexts:
            # Find all context placeholders
            context_placeholders = re.findall(r"{context:([^}]+)}", rendered)
            
            for placeholder in context_placeholders:
                # Parse placeholder options
                options = {}
                parts = placeholder.split(":")
                context_type_str = parts[0]
                
                for part in parts[1:]:
                    if "=" in part:
                        key, value = part.split("=", 1)
                        options[key] = value
                    else:
                        options[part] = True
                
                # Filter contexts by type
                try:
                    context_type = ContextType[context_type_str.upper()]
                    filtered_contexts = [c for c in contexts if c.context_type == context_type]
                except KeyError:
                    filtered_contexts = contexts
                
                # Apply additional filters
                if "source" in options:
                    filtered_contexts = [c for c in filtered_contexts if c.source == options["source"]]
                
                if "tag" in options:
                    filtered_contexts = [c for c in filtered_contexts if options["tag"] in c.tags]
                
                # Limit the number of contexts
                if "limit" in options:
                    try:
                        limit = int(options["limit"])
                        filtered_contexts = filtered_contexts[:limit]
                    except ValueError:
                        pass
                
                # Format contexts
                formatted_contexts = []
                for context in filtered_contexts:
                    if "format" in options:
                        format_str = options["format"]
                        formatted_context = format_str.format(
                            content=context.content,
                            id=context.id,
                            type=context.context_type.name,
                            source=context.source or "",
                            **context.metadata
                        )
                    else:
                        formatted_context = context.content
                    
                    formatted_contexts.append(formatted_context)
                
                # Join contexts with separator
                separator = options.get("separator", "\n\n")
                context_str = separator.join(formatted_contexts)
                
                # Replace placeholder with contexts
                rendered = rendered.replace(f"{{context:{placeholder}}}", context_str)
        
        return rendered
    
    def update(self, template: Optional[str] = None, variables: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the prompt template.
        
        Args:
            template: New template string.
            variables: New variables for the template.
            metadata: New metadata for the template.
        """
        if template is not None:
            self.template = template
        
        if variables is not None:
            self.variables.update(variables)
        
        if metadata is not None:
            self.metadata.update(metadata)
        
        self.updated_at = datetime.datetime.now().isoformat()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the prompt template.
        
        Args:
            tag: The tag to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.datetime.now().isoformat()
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the prompt template.
        
        Args:
            tag: The tag to remove.
            
        Returns:
            True if the tag was removed, False otherwise.
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.datetime.now().isoformat()
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the prompt template has a specific tag.
        
        Args:
            tag: The tag to check.
            
        Returns:
            True if the prompt template has the tag, False otherwise.
        """
        return tag in self.tags
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the prompt template to a dictionary.
        
        Returns:
            Dictionary representation of the prompt template.
        """
        return {
            "id": self.id,
            "name": self.name,
            "template": self.template,
            "variables": self.variables,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """
        Create a prompt template from a dictionary.
        
        Args:
            data: Dictionary representation of the prompt template.
            
        Returns:
            Prompt template.
        """
        template = cls(
            name=data.get("name", ""),
            template=data.get("template", ""),
            variables=data.get("variables", {}),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            id=data.get("id"),
        )
        
        template.created_at = data.get("created_at", template.created_at)
        template.updated_at = data.get("updated_at", template.updated_at)
        
        return template
    
    def to_json(self) -> str:
        """
        Convert the prompt template to a JSON string.
        
        Returns:
            JSON string representation of the prompt template.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PromptTemplate':
        """
        Create a prompt template from a JSON string.
        
        Args:
            json_str: JSON string representation of the prompt template.
            
        Returns:
            Prompt template.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


@tag("context.prompt")
class PromptManager:
    """
    Manager for prompt templates.
    
    This class manages prompt templates, providing methods for adding,
    retrieving, updating, and removing templates.
    
    Attributes:
        templates: Dictionary of prompt templates, keyed by ID.
        metadata: Additional metadata for the prompt manager.
    
    TODO(Issue #7): Add support for prompt template persistence
    TODO(Issue #7): Implement prompt template validation
    """
    
    def __init__(self) -> None:
        """Initialize the prompt manager."""
        self.templates: Dict[str, PromptTemplate] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_template(self, template: PromptTemplate) -> str:
        """
        Add a prompt template to the manager.
        
        Args:
            template: The prompt template to add.
            
        Returns:
            The ID of the added template.
        """
        self.templates[template.id] = template
        return template.id
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by ID.
        
        Args:
            template_id: The ID of the template to get.
            
        Returns:
            The prompt template, or None if it doesn't exist.
        """
        return self.templates.get(template_id)
    
    def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by name.
        
        Args:
            name: The name of the template to get.
            
        Returns:
            The prompt template, or None if it doesn't exist.
        """
        for template in self.templates.values():
            if template.name == name:
                return template
        return None
    
    def update_template(self, template_id: str, template: Optional[str] = None, variables: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[PromptTemplate]:
        """
        Update a prompt template.
        
        Args:
            template_id: The ID of the template to update.
            template: New template string.
            variables: New variables for the template.
            metadata: New metadata for the template.
            
        Returns:
            The updated prompt template, or None if it doesn't exist.
        """
        template_obj = self.get_template(template_id)
        if template_obj is None:
            return None
        
        template_obj.update(template, variables, metadata)
        return template_obj
    
    def remove_template(self, template_id: str) -> bool:
        """
        Remove a prompt template.
        
        Args:
            template_id: The ID of the template to remove.
            
        Returns:
            True if the template was removed, False otherwise.
        """
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False
    
    def get_templates_by_tag(self, tag: str) -> List[PromptTemplate]:
        """
        Get prompt templates by tag.
        
        Args:
            tag: The tag to filter by.
            
        Returns:
            List of prompt templates with the specified tag.
        """
        return [template for template in self.templates.values() if template.has_tag(tag)]
    
    def render_template(self, template_id: str, variables: Optional[Dict[str, Any]] = None, contexts: Optional[List[Context]] = None) -> Optional[str]:
        """
        Render a prompt template.
        
        Args:
            template_id: The ID of the template to render.
            variables: Dictionary of variables to use for rendering.
            contexts: List of contexts to include in the prompt.
            
        Returns:
            Rendered prompt, or None if the template doesn't exist.
        """
        template = self.get_template(template_id)
        if template is None:
            return None
        
        return template.render(variables, contexts)
    
    def render_template_by_name(self, name: str, variables: Optional[Dict[str, Any]] = None, contexts: Optional[List[Context]] = None) -> Optional[str]:
        """
        Render a prompt template by name.
        
        Args:
            name: The name of the template to render.
            variables: Dictionary of variables to use for rendering.
            contexts: List of contexts to include in the prompt.
            
        Returns:
            Rendered prompt, or None if the template doesn't exist.
        """
        template = self.get_template_by_name(name)
        if template is None:
            return None
        
        return template.render(variables, contexts)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the prompt manager.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the prompt manager.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the prompt manager to a dictionary.
        
        Returns:
            Dictionary representation of the prompt manager.
        """
        return {
            "templates": {template_id: template.to_dict() for template_id, template in self.templates.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptManager':
        """
        Create a prompt manager from a dictionary.
        
        Args:
            data: Dictionary representation of the prompt manager.
            
        Returns:
            Prompt manager.
        """
        manager = cls()
        manager.metadata = data.get("metadata", {})
        
        for template_data in data.get("templates", {}).values():
            template = PromptTemplate.from_dict(template_data)
            manager.add_template(template)
        
        return manager


# Singleton instance
_prompt_manager: Optional[PromptManager] = None

def get_prompt_manager() -> PromptManager:
    """
    Get the singleton instance of the prompt manager.
    
    Returns:
        The prompt manager instance.
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
