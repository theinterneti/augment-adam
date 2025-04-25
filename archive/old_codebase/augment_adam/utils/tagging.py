"""
Tagging system for categorizing and organizing code.

This module provides a tagging system for categorizing and organizing code
in the augment_adam package. It defines tag categories, hierarchies, and
utilities for working with tags.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass, field


class TagCategory(Enum):
    """Categories for tags."""
    MEMORY = auto()  # Memory-related tags
    MODEL = auto()  # Model-related tags
    AGENT = auto()  # Agent-related tags
    CONTEXT = auto()  # Context-related tags
    UTILITY = auto()  # Utility-related tags
    TEMPLATE = auto()  # Template-related tags
    TEST = auto()  # Test-related tags
    DOCUMENTATION = auto()  # Documentation-related tags
    WEB = auto()  # Web-related tags
    API = auto()  # API-related tags
    PLUGIN = auto()  # Plugin-related tags
    CORE = auto()  # Core functionality tags


@dataclass
class Tag:
    """
    Represents a tag that can be applied to code.

    Tags are used to categorize and organize code. They can be hierarchical
    and belong to different categories.

    Attributes:
        name: The name of the tag.
        category: The category of the tag.
        parent: Optional parent tag.
        attributes: Optional attributes for the tag.
        children: Child tags.
    """

    name: str
    category: TagCategory
    parent: Optional['Tag'] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['Tag'] = field(default_factory=list)

    def __post_init__(self):
        """Initialize the tag."""
        if self.parent:
            self.parent.children.append(self)

    def __str__(self) -> str:
        """Return the string representation of the tag."""
        return self.name

    def __repr__(self) -> str:
        """Return the string representation of the tag."""
        return f"Tag({self.name}, {self.category})"

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


class TagRegistry:
    """
    Registry for tags.

    The TagRegistry is responsible for creating, retrieving, and organizing tags.
    It maintains a hierarchical structure of tags and provides methods for
    filtering and searching tags.

    Attributes:
        tags: Dictionary of all tags, keyed by name.
    """

    def __init__(self):
        """Initialize the tag registry."""
        self.tags: Dict[str, Tag] = {}
        self._initialize_tags()

    def _initialize_tags(self):
        """Initialize the predefined tags."""
        # Memory hierarchy
        self.create_tag("memory", TagCategory.MEMORY)
        self.create_tag("vector", TagCategory.MEMORY, "memory")
        self.create_tag("faiss", TagCategory.MEMORY, "vector")
        self.create_tag("neo4j", TagCategory.MEMORY, "memory")
        self.create_tag("graph", TagCategory.MEMORY, "memory")
        self.create_tag("episodic", TagCategory.MEMORY, "memory")
        self.create_tag("semantic", TagCategory.MEMORY, "memory")
        self.create_tag("working", TagCategory.MEMORY, "memory")

        # Model hierarchy
        self.create_tag("model", TagCategory.MODEL)
        self.create_tag("anthropic", TagCategory.MODEL, "model")
        self.create_tag("openai", TagCategory.MODEL, "model")
        self.create_tag("huggingface", TagCategory.MODEL, "model")
        self.create_tag("ollama", TagCategory.MODEL, "model")
        self.create_tag("embedding", TagCategory.MODEL, "model")

        # Agent hierarchy
        self.create_tag("agent", TagCategory.AGENT)
        self.create_tag("mcp", TagCategory.AGENT, "agent")
        self.create_tag("worker", TagCategory.AGENT, "agent")
        self.create_tag("coordination", TagCategory.AGENT, "agent")
        self.create_tag("team", TagCategory.AGENT, "coordination")
        self.create_tag("workflow", TagCategory.AGENT, "coordination")
        self.create_tag("reasoning", TagCategory.AGENT, "agent")
        self.create_tag("planning", TagCategory.AGENT, "reasoning")
        self.create_tag("reflection", TagCategory.AGENT, "reasoning")
        self.create_tag("decision", TagCategory.AGENT, "reasoning")
        self.create_tag("knowledge", TagCategory.AGENT, "reasoning")
        self.create_tag("chain_of_thought", TagCategory.AGENT, "reasoning")
        self.create_tag("smc", TagCategory.AGENT, "agent")
        self.create_tag("particle", TagCategory.AGENT, "smc")
        self.create_tag("sampler", TagCategory.AGENT, "smc")
        self.create_tag("potential", TagCategory.AGENT, "smc")

        # Context hierarchy
        self.create_tag("context", TagCategory.CONTEXT)
        self.create_tag("chunking", TagCategory.CONTEXT, "context")
        self.create_tag("composition", TagCategory.CONTEXT, "context")
        self.create_tag("retrieval", TagCategory.CONTEXT, "context")
        self.create_tag("prompt", TagCategory.CONTEXT, "context")

        # Utility hierarchy
        self.create_tag("utility", TagCategory.UTILITY)
        self.create_tag("template", TagCategory.UTILITY, "utility")
        self.create_tag("hardware", TagCategory.UTILITY, "utility")
        self.create_tag("jinja", TagCategory.UTILITY, "template")

        # Template hierarchy
        self.create_tag("template_type", TagCategory.TEMPLATE)
        self.create_tag("code", TagCategory.TEMPLATE, "template_type")
        self.create_tag("test", TagCategory.TEMPLATE, "template_type")
        self.create_tag("doc", TagCategory.TEMPLATE, "template_type")
        self.create_tag("memory_template", TagCategory.TEMPLATE, "template_type")

        # Test hierarchy
        self.create_tag("test_type", TagCategory.TEST)
        self.create_tag("unit", TagCategory.TEST, "test_type")
        self.create_tag("integration", TagCategory.TEST, "test_type")
        self.create_tag("e2e", TagCategory.TEST, "test_type")
        self.create_tag("performance", TagCategory.TEST, "test_type")
        self.create_tag("stress", TagCategory.TEST, "test_type")
        self.create_tag("compatibility", TagCategory.TEST, "test_type")

        # Documentation hierarchy
        self.create_tag("doc_type", TagCategory.DOCUMENTATION)
        self.create_tag("api", TagCategory.DOCUMENTATION, "doc_type")
        self.create_tag("guide", TagCategory.DOCUMENTATION, "doc_type")
        self.create_tag("tutorial", TagCategory.DOCUMENTATION, "doc_type")
        self.create_tag("reference", TagCategory.DOCUMENTATION, "doc_type")

        # Web hierarchy
        self.create_tag("web", TagCategory.WEB)
        self.create_tag("frontend", TagCategory.WEB, "web")
        self.create_tag("backend", TagCategory.WEB, "web")
        self.create_tag("api_endpoint", TagCategory.WEB, "web")

        # API hierarchy
        self.create_tag("api_type", TagCategory.API)
        self.create_tag("rest", TagCategory.API, "api_type")
        self.create_tag("graphql", TagCategory.API, "api_type")
        self.create_tag("websocket", TagCategory.API, "api_type")

        # Plugin hierarchy
        self.create_tag("plugin", TagCategory.PLUGIN)
        self.create_tag("file_manager", TagCategory.PLUGIN, "plugin")
        self.create_tag("web_search", TagCategory.PLUGIN, "plugin")
        self.create_tag("system_info", TagCategory.PLUGIN, "plugin")

        # Core hierarchy
        self.create_tag("core", TagCategory.CORE)
        self.create_tag("settings", TagCategory.CORE, "core")
        self.create_tag("errors", TagCategory.CORE, "core")
        self.create_tag("async", TagCategory.CORE, "core")
        self.create_tag("parallel", TagCategory.CORE, "core")
        self.create_tag("task", TagCategory.CORE, "core")

    def create_tag(self, name: str, category: TagCategory,
                  parent: Optional[Union[str, Tag]] = None,
                  attributes: Optional[Dict[str, Any]] = None) -> Tag:
        """
        Create a new tag.

        Args:
            name: The name of the tag.
            category: The category of the tag.
            parent: Optional parent tag or parent tag name.
            attributes: Optional attributes for the tag.

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

        tag = Tag(name, category, parent_tag, attributes or {})
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

    def get_or_create_tag(self, name: str, category: TagCategory,
                         parent: Optional[Union[str, Tag]] = None,
                         attributes: Optional[Dict[str, Any]] = None) -> Tag:
        """
        Get a tag by name or create it if it doesn't exist.

        Args:
            name: The name of the tag.
            category: The category of the tag.
            parent: Optional parent tag or parent tag name.
            attributes: Optional attributes for the tag.

        Returns:
            The existing or created tag.
        """
        tag = self.get_tag(name)
        if tag:
            return tag
        return self.create_tag(name, category, parent, attributes)

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

    def get_tags_by_category(self, category: TagCategory) -> List[Tag]:
        """
        Get tags by category.

        Args:
            category: The category to filter by.

        Returns:
            List of tags in the specified category.
        """
        return [tag for tag in self.tags.values() if tag.category == category]

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


# Singleton instance
_tag_registry: Optional[TagRegistry] = None

def get_tag_registry() -> TagRegistry:
    """
    Get the singleton instance of the tag registry.

    Returns:
        The tag registry instance.
    """
    global _tag_registry
    if _tag_registry is None:
        _tag_registry = TagRegistry()
    return _tag_registry

def get_tag(name: str) -> Optional[Tag]:
    """
    Get a tag by name.

    Args:
        name: The name of the tag.

    Returns:
        The tag or None if it doesn't exist.
    """
    return get_tag_registry().get_tag(name)

def create_tag(name: str, category: TagCategory,
              parent: Optional[Union[str, Tag]] = None,
              attributes: Optional[Dict[str, Any]] = None) -> Tag:
    """
    Create a new tag.

    Args:
        name: The name of the tag.
        category: The category of the tag.
        parent: Optional parent tag or parent tag name.
        attributes: Optional attributes for the tag.

    Returns:
        The created tag.
    """
    return get_tag_registry().create_tag(name, category, parent, attributes)

def get_or_create_tag(name: str, category: TagCategory,
                     parent: Optional[Union[str, Tag]] = None,
                     attributes: Optional[Dict[str, Any]] = None) -> Tag:
    """
    Get a tag by name or create it if it doesn't exist.

    Args:
        name: The name of the tag.
        category: The category of the tag.
        parent: Optional parent tag or parent tag name.
        attributes: Optional attributes for the tag.

    Returns:
        The existing or created tag.
    """
    return get_tag_registry().get_or_create_tag(name, category, parent, attributes)

def get_tags_by_category(category: TagCategory) -> List[Tag]:
    """
    Get tags by category.

    Args:
        category: The category to filter by.

    Returns:
        List of tags in the specified category.
    """
    return get_tag_registry().get_tags_by_category(category)


def tag(tag_name: str, **attributes):
    """
    Decorator for tagging classes and functions.

    Args:
        tag_name: The name of the tag to apply.
        **attributes: Optional attributes for the tag.

    Returns:
        The decorated class or function.

    Example:
        @tag("memory.vector.faiss")
        class FAISSMemory:
            pass
    """
    def decorator(obj):
        # Get the tag
        tag_parts = tag_name.split(".")
        if len(tag_parts) == 1:
            # Single tag
            tag_obj = get_tag(tag_name)
            if tag_obj is None:
                # Try to infer the category
                if hasattr(obj, "__module__"):
                    module = obj.__module__
                    if "memory" in module:
                        category = TagCategory.MEMORY
                    elif "model" in module:
                        category = TagCategory.MODEL
                    elif "agent" in module:
                        category = TagCategory.AGENT
                    elif "context" in module:
                        category = TagCategory.CONTEXT
                    elif "template" in module:
                        category = TagCategory.TEMPLATE
                    elif "test" in module:
                        category = TagCategory.TEST
                    elif "doc" in module or "documentation" in module:
                        category = TagCategory.DOCUMENTATION
                    elif "web" in module:
                        category = TagCategory.WEB
                    elif "api" in module:
                        category = TagCategory.API
                    elif "plugin" in module:
                        category = TagCategory.PLUGIN
                    elif "core" in module:
                        category = TagCategory.CORE
                    else:
                        category = TagCategory.UTILITY
                else:
                    category = TagCategory.UTILITY

                tag_obj = create_tag(tag_name, category, attributes=attributes)
            else:
                # Update attributes
                for key, value in attributes.items():
                    tag_obj.set_attribute(key, value)
        else:
            # Hierarchical tag
            parent_name = tag_parts[0]
            parent_tag = get_tag(parent_name)

            if parent_tag is None:
                # Try to infer the category
                if hasattr(obj, "__module__"):
                    module = obj.__module__
                    if "memory" in module:
                        category = TagCategory.MEMORY
                    elif "model" in module:
                        category = TagCategory.MODEL
                    elif "agent" in module:
                        category = TagCategory.AGENT
                    elif "context" in module:
                        category = TagCategory.CONTEXT
                    elif "template" in module:
                        category = TagCategory.TEMPLATE
                    elif "test" in module:
                        category = TagCategory.TEST
                    elif "doc" in module or "documentation" in module:
                        category = TagCategory.DOCUMENTATION
                    elif "web" in module:
                        category = TagCategory.WEB
                    elif "api" in module:
                        category = TagCategory.API
                    elif "plugin" in module:
                        category = TagCategory.PLUGIN
                    elif "core" in module:
                        category = TagCategory.CORE
                    else:
                        category = TagCategory.UTILITY
                else:
                    category = TagCategory.UTILITY

                parent_tag = create_tag(parent_name, category)

            # Create the rest of the hierarchy
            current_tag = parent_tag
            for i in range(1, len(tag_parts) - 1):
                part = tag_parts[i]
                child_tag = get_tag(part)
                if child_tag is None or child_tag.parent != current_tag:
                    child_tag = create_tag(part, current_tag.category, current_tag)
                current_tag = child_tag

            # Create the final tag
            final_part = tag_parts[-1]
            tag_obj = get_tag(final_part)
            if tag_obj is None or tag_obj.parent != current_tag:
                tag_obj = create_tag(final_part, current_tag.category, current_tag, attributes=attributes)
            else:
                # Update attributes
                for key, value in attributes.items():
                    tag_obj.set_attribute(key, value)

        # Add the tag to the object
        if not hasattr(obj, "__tags__"):
            obj.__tags__ = []
        obj.__tags__.append(tag_obj)

        return obj

    return decorator


def get_tags(obj) -> List[Tag]:
    """
    Get the tags applied to an object.

    Args:
        obj: The object to get tags for.

    Returns:
        List of tags applied to the object.
    """
    if hasattr(obj, "__tags__"):
        return obj.__tags__
    return []
