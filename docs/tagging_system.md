# Tagging System Documentation

## Overview

The tagging system in Augment Adam provides a flexible and powerful way to categorize and organize components, models, and other entities in the system. It enables better discoverability, organization, and integration of components.

## Core Concepts

### Tags

A tag is a named entity with attributes and relationships. Tags can be organized hierarchically, allowing for a rich taxonomy of concepts.

Key properties of tags:
- **Name**: A unique identifier for the tag
- **Category**: The category the tag belongs to (e.g., MEMORY, MODEL, AGENT)
- **Parent**: Optional parent tag for hierarchical organization
- **Attributes**: Key-value pairs for additional metadata
- **Description**: A human-readable description of the tag
- **Synonyms**: Alternative names for the tag
- **Examples**: Example usages of the tag

### Tag Registry

The tag registry is a central repository for all tags in the system. It provides methods for creating, retrieving, and organizing tags.

Key features of the tag registry:
- Thread-safe tag creation and retrieval
- Support for hierarchical tag organization
- Methods for searching and filtering tags
- Support for test isolation

## Usage

### Tagging Classes and Functions

The most common use of the tagging system is to tag classes and functions using the `@tag` decorator:

```python
from augment_adam.utils.tagging import tag, TagCategory

@tag("memory.vector.faiss")
class FAISSMemory:
    """A memory implementation using FAISS."""
    pass

@tag("model.embedding", dimension=768, metric="cosine")
class EmbeddingModel:
    """An embedding model."""
    pass
```

### Creating Tags Programmatically

Tags can also be created programmatically:

```python
from augment_adam.utils.tagging import create_tag, TagCategory

# Create a simple tag
tag = create_tag("my_tag", TagCategory.UTILITY)

# Create a hierarchical tag
parent_tag = create_tag("parent", TagCategory.UTILITY)
child_tag = create_tag("child", TagCategory.UTILITY, parent=parent_tag)

# Create a tag with attributes
tag_with_attrs = create_tag(
    "config",
    TagCategory.UTILITY,
    attributes={"version": "1.0", "author": "Augment Adam Team"}
)
```

### Retrieving Tags

Tags can be retrieved using various methods:

```python
from augment_adam.utils.tagging import get_tag, get_tags_by_category, find_tags

# Get a tag by name
tag = get_tag("memory.vector.faiss")

# Get tags by category
memory_tags = get_tags_by_category(TagCategory.MEMORY)

# Find tags matching a query
vector_tags = find_tags("vector")
```

### Working with Tag Relationships

Tags can have relationships with other tags:

```python
from augment_adam.utils.tagging import relate_tags, TagRelationship

# Create a relationship between tags
relate_tags("model.embedding", "memory.vector", TagRelationship.USES)

# Get related tags
related_tags = get_related_tags("model.embedding")
```

## Testing with Tags

The tagging system provides utilities for testing:

```python
from augment_adam.testing.utils.tag_utils import IsolatedTagRegistry

# Use an isolated tag registry for tests
with IsolatedTagRegistry():
    # Create and use tags without affecting the global registry
    tag = create_tag("test_tag", TagCategory.TEST)
```

## Thread Safety

The tagging system is designed to be thread-safe, with features to handle concurrent tag creation and access:

- The `force` parameter in `create_tag` allows for safe retrieval of existing tags
- The `safe_tag` decorator handles race conditions in hierarchical tag creation
- Thread-local registries can be used for isolation

## Best Practices

1. **Use Hierarchical Tags**: Organize tags hierarchically (e.g., "memory.vector.faiss") for better organization
2. **Add Descriptive Attributes**: Include relevant attributes to provide additional context
3. **Use Consistent Categories**: Stick to the predefined TagCategory values
4. **Document Tags**: Add descriptions and examples to make tags more discoverable
5. **Use Relationships**: Create relationships between tags to express dependencies and connections
