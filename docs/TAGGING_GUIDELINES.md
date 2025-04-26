# Tagging Guidelines

This document provides detailed guidelines for using the tagging system in the Augment Adam project. The tagging system is a core component of the project and is used to organize and categorize code, documentation, and other resources.

## Tagging Format

Tags in the Augment Adam project follow a hierarchical dot notation format. This format allows for the creation of a tree-like structure of tags, which makes it easier to organize and navigate the codebase.

### Format

```
category.subcategory.specific_item
```

For example:
- `memory.vector.faiss`
- `agent.coordination.orchestrator`
- `testing.unit.memory`

### Required Categories

The following top-level categories are required for all tags:

- `core`: Core components of the system
- `memory`: Memory-related components
- `agent`: Agent-related components
- `context`: Context-related components
- `template`: Template-related components
- `testing`: Testing-related components
- `documentation`: Documentation-related components

Additional categories can be created as needed, but they should be discussed and agreed upon by the team before being used.

## Using Tags in Code

Tags are applied to code using the `@tag` decorator. This decorator can be applied to classes, functions, and methods.

### Example

```python
from augment_adam.utils.tagging import tag

@tag("memory.vector.faiss")
class FAISSMemory:
    """
    A memory implementation using FAISS for vector storage and retrieval.
    """
    pass
```

### Multiple Tags

Multiple tags can be applied to a single item by using multiple `@tag` decorators.

```python
@tag("memory.vector.faiss")
@tag("memory.persistent")
class FAISSMemory:
    """
    A memory implementation using FAISS for vector storage and retrieval.
    """
    pass
```

### Tag Attributes

Tags can have attributes that provide additional information about the tagged item.

```python
@tag("memory.vector.faiss", dimensions=1536, metric="cosine")
class FAISSMemory:
    """
    A memory implementation using FAISS for vector storage and retrieval.
    """
    pass
```

## Registry Isolation

The tagging system supports registry isolation, which allows for the creation of separate tag registries for different contexts. This is particularly useful for testing, where we want to ensure that tests don't interfere with each other.

### Testing Isolation

For testing, registry isolation is required. This means that each test should use its own isolated tag registry.

```python
from augment_adam.testing.utils.tag_utils import isolated_tag_registry, reset_tag_registry

def setUp(self):
    """Set up the test case."""
    # Reset the tag registry to avoid conflicts
    reset_tag_registry()
    
    # Use an isolated tag registry for this test
    with isolated_tag_registry():
        # Create test objects
        self.memory = FAISSMemory()
```

### Development Isolation

For development, registry isolation is recommended but not required. This means that developers should consider using isolated registries when working on features that might interfere with each other.

```python
from augment_adam.utils.tagging.registry_factory import get_registry_factory

# Get the registry factory
factory = get_registry_factory()

# Enter development mode with a fresh registry
factory.enter_development_mode()

# Do development work
# ...

# Exit development mode
factory.exit_development_mode()
```

## Tag Discovery and Querying

The tagging system provides tools for discovering and querying tags. These tools can be used to find tagged items, explore the tag hierarchy, and understand the relationships between tags.

### Finding Tagged Items

```python
from augment_adam.utils.tagging import get_tagged_items

# Get all items tagged with "memory.vector.faiss"
faiss_items = get_tagged_items("memory.vector.faiss")

# Get all items tagged with any "memory.vector" tag
vector_items = get_tagged_items("memory.vector.*")
```

### Exploring the Tag Hierarchy

```python
from augment_adam.utils.tagging import get_tag_hierarchy

# Get the entire tag hierarchy
hierarchy = get_tag_hierarchy()

# Get the "memory" branch of the hierarchy
memory_hierarchy = get_tag_hierarchy("memory")
```

### Understanding Tag Relationships

```python
from augment_adam.utils.tagging import get_related_tags

# Get tags related to "memory.vector.faiss"
related_tags = get_related_tags("memory.vector.faiss")
```

## Best Practices

### Be Specific

Tags should be as specific as possible while still being general enough to be useful. For example, `memory.vector.faiss` is better than just `memory` or `faiss`.

### Use Consistent Naming

Tag names should be consistent across the codebase. For example, if you're using `memory.vector.faiss` in one place, don't use `memory.faiss.vector` in another.

### Document Tags

Tags should be documented in the codebase. This can be done in docstrings, comments, or dedicated documentation files.

### Use Tags for Navigation

Tags can be used to navigate the codebase. For example, you can use the tag hierarchy to find all memory-related components.

### Use Tags for Documentation

Tags can be used to generate documentation. For example, you can generate a list of all memory implementations by querying for items tagged with `memory.*`.

## Conclusion

The tagging system is a powerful tool for organizing and navigating the Augment Adam codebase. By following these guidelines, we can ensure that tags are used consistently and effectively across the project.
