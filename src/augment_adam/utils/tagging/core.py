"""
Core tagging system for categorizing and organizing code for AI agent comprehension.

This module provides a tagging system optimized for AI agent understanding and reasoning.
It defines tag categories, hierarchies, relationships, and utilities for working with tags
in a way that facilitates AI comprehension of code structure, purpose, and relationships.

TODO(Issue #4): Add support for tag versioning
TODO(Issue #4): Implement tag validation against a schema
TODO(Issue #4): Add tag analytics to track usage and coverage
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Union, Any, Callable, TypeVar, cast, Tuple
from dataclasses import dataclass, field
import functools
import inspect
import re
from collections import defaultdict


class TagCategory(Enum):
    """
    Categories for tags.

    These categories represent the primary classification of tags and help
    organize them into logical groups for AI comprehension.
    """
    MEMORY = auto()  # Memory-related tags (storage, retrieval, management)
    MODEL = auto()  # Model-related tags (AI models, embeddings, inference)
    AGENT = auto()  # Agent-related tags (autonomous entities, behaviors)
    CONTEXT = auto()  # Context-related tags (information environment, state)
    UTILITY = auto()  # Utility-related tags (helper functions, tools)
    TEMPLATE = auto()  # Template-related tags (code generation, patterns)
    TEST = auto()  # Test-related tags (validation, verification)
    DOCUMENTATION = auto()  # Documentation-related tags (explanations, guides)
    WEB = auto()  # Web-related tags (HTTP, browsers, frontend/backend)
    API = auto()  # API-related tags (interfaces, endpoints, protocols)
    PLUGIN = auto()  # Plugin-related tags (extensions, add-ons)
    CORE = auto()  # Core functionality tags (essential components)
    DATA = auto()  # Data-related tags (processing, transformation)
    SECURITY = auto()  # Security-related tags (authentication, encryption)
    PERFORMANCE = auto()  # Performance-related tags (optimization, efficiency)
    UI = auto()  # User interface tags (interaction, display)


class TagRelationship(Enum):
    """
    Relationships between tags.

    These relationships define how tags are semantically connected beyond
    simple parent-child hierarchies, enabling richer AI reasoning about
    code components and their interactions.
    """
    USES = auto()  # Tag A uses functionality from Tag B
    IMPLEMENTS = auto()  # Tag A implements interface/contract defined by Tag B
    EXTENDS = auto()  # Tag A extends or enhances Tag B
    DEPENDS_ON = auto()  # Tag A depends on Tag B (stronger than USES)
    ALTERNATIVE_TO = auto()  # Tag A is an alternative implementation to Tag B
    COMPOSES = auto()  # Tag A is composed of Tag B components
    GENERATES = auto()  # Tag A generates Tag B artifacts
    CONFIGURES = auto()  # Tag A configures Tag B behavior
    PROCESSES = auto()  # Tag A processes Tag B data/objects
    COMMUNICATES_WITH = auto()  # Tag A communicates with Tag B
    PRECEDES = auto()  # Tag A precedes Tag B in a workflow/pipeline
    SUCCEEDS = auto()  # Tag A succeeds Tag B in a workflow/pipeline
    TESTS = auto()  # Tag A tests Tag B functionality
    DOCUMENTS = auto()  # Tag A documents Tag B
    OPTIMIZES = auto()  # Tag A optimizes Tag B
    SECURES = auto()  # Tag A provides security for Tag B


@dataclass
class Tag:
    """
    Represents a tag that can be applied to code for AI comprehension.

    Tags are used to categorize and organize code in a way that facilitates
    AI understanding and reasoning. They can be hierarchical, have relationships
    with other tags, and contain rich semantic information.

    Attributes:
        name: The name of the tag.
        category: The category of the tag.
        parent: Optional parent tag.
        attributes: Optional attributes for the tag.
        children: Child tags.
        description: Human and AI readable description of what this tag represents.
        examples: List of example usages to help AI understand the tag's purpose.
        relationships: Dictionary mapping related tags to their relationship types.
        synonyms: Alternative names or terms for this tag concept.
        importance: Numeric value (0-10) indicating the tag's importance in the system.
        created_at: When this tag was first created (ISO format date string).
        updated_at: When this tag was last updated (ISO format date string).

    TODO(Issue #4): Add support for tag versioning
    TODO(Issue #4): Add support for tag deprecation
    TODO(Issue #4): Add support for tag aliases
    TODO(Issue #4): Implement tag validation
    """

    name: str
    category: TagCategory
    parent: Optional['Tag'] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['Tag'] = field(default_factory=list)
    description: str = ""
    examples: List[str] = field(default_factory=list)
    relationships: Dict['Tag', List[TagRelationship]] = field(default_factory=dict)
    synonyms: List[str] = field(default_factory=list)
    importance: int = 5  # Default medium importance
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize the tag with parent-child relationship and timestamps."""
        from datetime import datetime

        # Set up parent-child relationship
        if self.parent:
            self.parent.children.append(self)

        # Set timestamps if not provided
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def __str__(self) -> str:
        """Return the string representation of the tag."""
        return self.name

    def __repr__(self) -> str:
        """Return the string representation of the tag."""
        return f"Tag({self.name}, {self.category})"

    def __hash__(self) -> int:
        """Return the hash of the tag."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Check if two tags are equal."""
        if not isinstance(other, Tag):
            return False
        return self.name == other.name

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

    def add_relationship(self, target: 'Tag', relationship: TagRelationship) -> None:
        """
        Add a relationship from this tag to another tag.

        Args:
            target: The target tag to relate to.
            relationship: The type of relationship.
        """
        if target not in self.relationships:
            self.relationships[target] = []

        if relationship not in self.relationships[target]:
            self.relationships[target].append(relationship)

    def remove_relationship(self, target: 'Tag', relationship: Optional[TagRelationship] = None) -> None:
        """
        Remove a relationship from this tag to another tag.

        Args:
            target: The target tag.
            relationship: The specific relationship to remove. If None, removes all relationships to the target.
        """
        if target not in self.relationships:
            return

        if relationship is None:
            # Remove all relationships to the target
            del self.relationships[target]
        else:
            # Remove the specific relationship
            if relationship in self.relationships[target]:
                self.relationships[target].remove(relationship)

            # If no relationships left, remove the target entry
            if not self.relationships[target]:
                del self.relationships[target]

    def has_relationship(self, target: 'Tag', relationship: Optional[TagRelationship] = None) -> bool:
        """
        Check if this tag has a relationship with another tag.

        Args:
            target: The target tag.
            relationship: The specific relationship to check. If None, checks if any relationship exists.

        Returns:
            True if the relationship exists, False otherwise.
        """
        if target not in self.relationships:
            return False

        if relationship is None:
            return True

        return relationship in self.relationships[target]

    def get_relationships(self, relationship_type: Optional[TagRelationship] = None) -> Dict['Tag', List[TagRelationship]]:
        """
        Get all relationships of this tag, optionally filtered by type.

        Args:
            relationship_type: Optional relationship type to filter by.

        Returns:
            Dictionary mapping related tags to their relationship types.
        """
        if relationship_type is None:
            return self.relationships

        result = {}
        for target, relationships in self.relationships.items():
            if relationship_type in relationships:
                result[target] = [relationship_type]

        return result

    def get_semantic_description(self) -> str:
        """
        Get a rich semantic description of this tag for AI comprehension.

        Returns:
            A detailed description of the tag including its relationships and attributes.
        """
        lines = [
            f"Tag: {self.name}",
            f"Category: {self.category.name}",
            f"Description: {self.description or 'No description provided.'}",
        ]

        if self.parent:
            lines.append(f"Parent: {self.parent.name}")

        if self.children:
            child_names = [child.name for child in self.children]
            lines.append(f"Children: {', '.join(child_names)}")

        if self.synonyms:
            lines.append(f"Synonyms: {', '.join(self.synonyms)}")

        if self.attributes:
            attr_lines = [f"  - {key}: {value}" for key, value in self.attributes.items()]
            lines.append("Attributes:")
            lines.extend(attr_lines)

        if self.relationships:
            rel_lines = []
            for target, relationships in self.relationships.items():
                rel_names = [rel.name for rel in relationships]
                rel_lines.append(f"  - {target.name}: {', '.join(rel_names)}")

            lines.append("Relationships:")
            lines.extend(rel_lines)

        if self.examples:
            lines.append("Examples:")
            for example in self.examples:
                lines.append(f"  - {example}")

        return "\n".join(lines)


class TagRegistry:
    """
    Registry for tags.

    The TagRegistry is responsible for creating, retrieving, and organizing tags.
    It maintains a hierarchical structure of tags and provides methods for
    filtering and searching tags.

    Attributes:
        tags: Dictionary of all tags, keyed by name.

    TODO(Issue #4): Add persistence support (save/load from database)
    TODO(Issue #4): Add tag recommendation based on code content
    TODO(Issue #4): Implement tag inference from code
    TODO(Issue #4): Add tag propagation through the codebase
    TODO(Issue #4): Add tag visualization capabilities
    """

    def __init__(self) -> None:
        """Initialize the tag registry."""
        self.tags: Dict[str, Tag] = {}
        self._initialize_tags()

    def _initialize_tags(self) -> None:
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
                  attributes: Optional[Dict[str, Any]] = None,
                  description: Optional[str] = None,
                  synonyms: Optional[List[str]] = None,
                  examples: Optional[List[str]] = None) -> Tag:
        """
        Create a new tag.

        Args:
            name: The name of the tag.
            category: The category of the tag.
            parent: Optional parent tag or parent tag name.
            attributes: Optional attributes for the tag.
            description: Optional description of the tag.
            synonyms: Optional list of synonyms for the tag.
            examples: Optional list of examples for the tag.

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

        tag = Tag(
            name=name,
            category=category,
            parent=parent_tag,
            attributes=attributes or {},
            description=description or "",
            synonyms=synonyms or [],
            examples=examples or []
        )
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
                         attributes: Optional[Dict[str, Any]] = None,
                         description: Optional[str] = None,
                         synonyms: Optional[List[str]] = None,
                         examples: Optional[List[str]] = None) -> Tag:
        """
        Get a tag by name or create it if it doesn't exist.

        Args:
            name: The name of the tag.
            category: The category of the tag.
            parent: Optional parent tag or parent tag name.
            attributes: Optional attributes for the tag.
            description: Optional description of the tag.
            synonyms: Optional list of synonyms for the tag.
            examples: Optional list of examples for the tag.

        Returns:
            The existing or created tag.
        """
        tag = self.get_tag(name)
        if tag:
            return tag
        return self.create_tag(
            name=name,
            category=category,
            parent=parent,
            attributes=attributes,
            description=description,
            synonyms=synonyms,
            examples=examples
        )

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

    def relate_tags(self, source_name: str, target_name: str, relationship: TagRelationship) -> None:
        """
        Create a relationship between two tags.

        Args:
            source_name: The name of the source tag.
            target_name: The name of the target tag.
            relationship: The type of relationship.

        Raises:
            ValueError: If either tag doesn't exist.
        """
        source = self.get_tag(source_name)
        target = self.get_tag(target_name)

        if source is None:
            raise ValueError(f"Source tag '{source_name}' does not exist")

        if target is None:
            raise ValueError(f"Target tag '{target_name}' does not exist")

        source.add_relationship(target, relationship)

    def get_related_tags(self, name: str, relationship: Optional[TagRelationship] = None) -> Dict[str, List[TagRelationship]]:
        """
        Get tags related to the specified tag.

        Args:
            name: The name of the tag.
            relationship: Optional relationship type to filter by.

        Returns:
            Dictionary mapping related tag names to their relationship types.

        Raises:
            ValueError: If the tag doesn't exist.
        """
        tag = self.get_tag(name)

        if tag is None:
            raise ValueError(f"Tag '{name}' does not exist")

        relationships = tag.get_relationships(relationship)

        # Convert to dictionary with tag names as keys
        return {target.name: relationships for target, relationships in relationships.items()}

    def find_tags(self, query: str, search_descriptions: bool = True,
                 search_attributes: bool = True, search_synonyms: bool = True) -> List[Tag]:
        """
        Find tags matching a search query.

        This method provides AI-friendly search capabilities, allowing for
        fuzzy matching and searching across various tag properties.

        Args:
            query: The search query.
            search_descriptions: Whether to search in tag descriptions.
            search_attributes: Whether to search in tag attributes.
            search_synonyms: Whether to search in tag synonyms.

        Returns:
            List of matching tags.
        """
        query = query.lower()
        results = []

        for tag in self.tags.values():
            # Check tag name
            if query in tag.name.lower():
                results.append(tag)
                continue

            # Check tag description
            if search_descriptions and tag.description and query in tag.description.lower():
                results.append(tag)
                continue

            # Check tag synonyms
            if search_synonyms and any(query in synonym.lower() for synonym in tag.synonyms):
                results.append(tag)
                continue

            # Check tag attributes
            if search_attributes and any(
                isinstance(value, str) and query in value.lower()
                for value in tag.attributes.values()
            ):
                results.append(tag)
                continue

        return results

    def get_tag_hierarchy(self, name: str) -> Dict[str, Any]:
        """
        Get the complete hierarchy for a tag.

        This method returns a nested dictionary representing the tag's
        position in the hierarchy, including all ancestors and descendants.

        Args:
            name: The name of the tag.

        Returns:
            Dictionary representing the tag hierarchy.

        Raises:
            ValueError: If the tag doesn't exist.
        """
        tag = self.get_tag(name)

        if tag is None:
            raise ValueError(f"Tag '{name}' does not exist")

        # Find the root ancestor
        current = tag
        while current.parent is not None:
            current = current.parent

        # Build the hierarchy from the root
        return self._build_hierarchy_dict(current)

    def _build_hierarchy_dict(self, tag: Tag) -> Dict[str, Any]:
        """
        Recursively build a dictionary representing a tag hierarchy.

        Args:
            tag: The tag to build the hierarchy for.

        Returns:
            Dictionary representing the tag hierarchy.
        """
        result = {
            "name": tag.name,
            "category": tag.category.name,
            "description": tag.description,
        }

        if tag.children:
            result["children"] = [self._build_hierarchy_dict(child) for child in tag.children]

        return result


# Import the registry factory
# Note: This is imported here to avoid circular imports
# The actual implementation is in registry_factory.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from augment_adam.utils.tagging.registry_factory import get_registry

# These functions will be replaced at runtime by the registry factory
# They are defined here for type checking and documentation purposes

def get_tag_registry() -> TagRegistry:
    """
    Get the current tag registry.

    This function is replaced at runtime by the registry factory.

    Returns:
        The current tag registry.
    """
    # This will be replaced at runtime
    pass

def get_tag(name: str) -> Optional[Tag]:
    """
    Get a tag by name.

    Args:
        name: The name of the tag.

    Returns:
        The tag or None if it doesn't exist.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    return get_registry().get_tag(name)

def create_tag(name: str, category: TagCategory,
              parent: Optional[Union[str, Tag]] = None,
              attributes: Optional[Dict[str, Any]] = None,
              description: Optional[str] = None,
              synonyms: Optional[List[str]] = None,
              examples: Optional[List[str]] = None) -> Tag:
    """
    Create a new tag.

    Args:
        name: The name of the tag.
        category: The category of the tag.
        parent: Optional parent tag or parent tag name.
        attributes: Optional attributes for the tag.
        description: Optional description of the tag.
        synonyms: Optional list of synonyms for the tag.
        examples: Optional list of examples for the tag.

    Returns:
        The created tag.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    return get_registry().create_tag(
        name=name,
        category=category,
        parent=parent,
        attributes=attributes,
        description=description,
        synonyms=synonyms,
        examples=examples
    )

def get_or_create_tag(name: str, category: TagCategory,
                     parent: Optional[Union[str, Tag]] = None,
                     attributes: Optional[Dict[str, Any]] = None,
                     description: Optional[str] = None,
                     synonyms: Optional[List[str]] = None,
                     examples: Optional[List[str]] = None) -> Tag:
    """
    Get a tag by name or create it if it doesn't exist.

    Args:
        name: The name of the tag.
        category: The category of the tag.
        parent: Optional parent tag or parent tag name.
        attributes: Optional attributes for the tag.
        description: Optional description of the tag.
        synonyms: Optional list of synonyms for the tag.
        examples: Optional list of examples for the tag.

    Returns:
        The existing or created tag.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    registry = get_registry()
    tag = registry.get_tag(name)
    if tag:
        return tag
    try:
        return registry.create_tag(
            name=name,
            category=category,
            parent=parent,
            attributes=attributes,
            description=description,
            synonyms=synonyms,
            examples=examples
        )
    except ValueError:
        # Tag might have been created by another thread
        return registry.get_tag(name)

def get_tags_by_category(category: TagCategory) -> List[Tag]:
    """
    Get tags by category.

    Args:
        category: The category to filter by.

    Returns:
        List of tags in the specified category.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    return get_registry().get_tags_by_category(category)


def relate_tags(source_name: str, target_name: str, relationship: TagRelationship) -> None:
    """
    Create a relationship between two tags.

    Args:
        source_name: The name of the source tag.
        target_name: The name of the target tag.
        relationship: The type of relationship.

    Raises:
        ValueError: If either tag doesn't exist.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    get_registry().relate_tags(source_name, target_name, relationship)


def get_related_tags(name: str, relationship: Optional[TagRelationship] = None) -> Dict[str, List[TagRelationship]]:
    """
    Get tags related to the specified tag.

    Args:
        name: The name of the tag.
        relationship: Optional relationship type to filter by.

    Returns:
        Dictionary mapping related tag names to their relationship types.

    Raises:
        ValueError: If the tag doesn't exist.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    return get_registry().get_related_tags(name, relationship)


def find_tags(query: str, search_descriptions: bool = True,
             search_attributes: bool = True, search_synonyms: bool = True) -> List[Tag]:
    """
    Find tags matching a search query.

    This method provides AI-friendly search capabilities, allowing for
    fuzzy matching and searching across various tag properties.

    Args:
        query: The search query.
        search_descriptions: Whether to search in tag descriptions.
        search_attributes: Whether to search in tag attributes.
        search_synonyms: Whether to search in tag synonyms.

    Returns:
        List of matching tags.
    """
    # This will use the registry factory at runtime
    from augment_adam.utils.tagging.registry_factory import get_registry
    return get_registry().find_tags(query, search_descriptions, search_attributes, search_synonyms)


def describe_tag(name: str) -> str:
    """
    Get a rich semantic description of a tag for AI comprehension.

    Args:
        name: The name of the tag.

    Returns:
        A detailed description of the tag including its relationships and attributes.

    Raises:
        ValueError: If the tag doesn't exist.
    """
    tag = get_tag(name)

    if tag is None:
        raise ValueError(f"Tag '{name}' does not exist")

    return tag.get_semantic_description()


# Type variable for generic decorator
T = TypeVar('T', bound=Callable[..., Any])

def tag(tag_name: str, **attributes: Any) -> Callable[[T], T]:
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
    # Use the safe_tag implementation from tag_utils
    # This avoids code duplication and ensures consistent behavior
    from augment_adam.testing.utils.tag_utils import safe_tag
    return safe_tag(tag_name, **attributes)


def get_tags(obj: Any) -> List[Tag]:
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
