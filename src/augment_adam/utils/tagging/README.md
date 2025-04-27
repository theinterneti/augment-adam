# AI-Optimized Tagging System

## Overview

This module provides a tagging system optimized for AI agent understanding and reasoning. It defines tag categories, hierarchies, relationships, and utilities for working with tags in a way that facilitates AI comprehension of code structure, purpose, and relationships.

## Components

### Tag

The `Tag` class represents a tag that can be applied to code, templates, and other resources. Tags have the following properties:

- **Name**: The name of the tag
- **Category**: The category of the tag
- **Parent**: Optional parent tag
- **Attributes**: Optional attributes for the tag
- **Children**: Child tags
- **Description**: Human and AI readable description of what this tag represents
- **Examples**: List of example usages to help AI understand the tag's purpose
- **Relationships**: Dictionary mapping related tags to their relationship types
- **Synonyms**: Alternative names or terms for this tag concept
- **Importance**: Numeric value (0-10) indicating the tag's importance in the system
- **Created/Updated**: Timestamps for when the tag was created and last updated

### TagCategory

The `TagCategory` enum defines the categories for tags:

- **MEMORY**: Memory-related tags (storage, retrieval, management)
- **MODEL**: Model-related tags (AI models, embeddings, inference)
- **AGENT**: Agent-related tags (autonomous entities, behaviors)
- **CONTEXT**: Context-related tags (information environment, state)
- **UTILITY**: Utility-related tags (helper functions, tools)
- **TEMPLATE**: Template-related tags (code generation, patterns)
- **TEST**: Test-related tags (validation, verification)
- **DOCUMENTATION**: Documentation-related tags (explanations, guides)
- **WEB**: Web-related tags (HTTP, browsers, frontend/backend)
- **API**: API-related tags (interfaces, endpoints, protocols)
- **PLUGIN**: Plugin-related tags (extensions, add-ons)
- **CORE**: Core functionality tags (essential components)
- **DATA**: Data-related tags (processing, transformation)
- **SECURITY**: Security-related tags (authentication, encryption)
- **PERFORMANCE**: Performance-related tags (optimization, efficiency)
- **UI**: User interface tags (interaction, display)

### TagRelationship

The `TagRelationship` enum defines the semantic relationships between tags:

- **USES**: Tag A uses functionality from Tag B
- **IMPLEMENTS**: Tag A implements interface/contract defined by Tag B
- **EXTENDS**: Tag A extends or enhances Tag B
- **DEPENDS_ON**: Tag A depends on Tag B (stronger than USES)
- **ALTERNATIVE_TO**: Tag A is an alternative implementation to Tag B
- **COMPOSES**: Tag A is composed of Tag B components
- **GENERATES**: Tag A generates Tag B artifacts
- **CONFIGURES**: Tag A configures Tag B behavior
- **PROCESSES**: Tag A processes Tag B data/objects
- **COMMUNICATES_WITH**: Tag A communicates with Tag B
- **PRECEDES**: Tag A precedes Tag B in a workflow/pipeline
- **SUCCEEDS**: Tag A succeeds Tag B in a workflow/pipeline
- **TESTS**: Tag A tests Tag B functionality
- **DOCUMENTS**: Tag A documents Tag B
- **OPTIMIZES**: Tag A optimizes Tag B
- **SECURES**: Tag A provides security for Tag B

### TagRegistry

The `TagRegistry` class is responsible for creating, retrieving, and organizing tags. It maintains a hierarchical structure of tags and provides methods for filtering and searching tags.

## Usage

### Tagging Code

You can tag code using the `@tag` decorator:

```python
from augment_adam.utils.tagging import tag, TagCategory

@tag("memory.vector.faiss")
class FAISSMemory:
    """FAISS-based vector memory."""
    pass
```

### Creating Relationships Between Tags

You can create relationships between tags:

```python
from augment_adam.utils.tagging import relate_tags, TagRelationship

# Indicate that the memory system uses the embedding model
relate_tags("memory", "embedding", TagRelationship.USES)

# Indicate that the FAISS implementation is an alternative to the Chroma implementation
relate_tags("faiss", "chroma", TagRelationship.ALTERNATIVE_TO)
```

### Finding Tags

You can search for tags using various criteria:

```python
from augment_adam.utils.tagging import find_tags

# Find tags related to vector databases
vector_tags = find_tags("vector")

# Find tags with "embedding" in their description
embedding_tags = find_tags("embedding", search_descriptions=True)
```

### Getting Related Tags

You can get tags related to a specific tag:

```python
from augment_adam.utils.tagging import get_related_tags, TagRelationship

# Get all tags related to the memory tag
related_to_memory = get_related_tags("memory")

# Get tags that the memory tag uses
memory_uses = get_related_tags("memory", TagRelationship.USES)
```

### Getting Semantic Descriptions

You can get rich semantic descriptions of tags:

```python
from augment_adam.utils.tagging import describe_tag

# Get a detailed description of the memory tag
memory_description = describe_tag("memory")
```

## Thread Safety

The tagging system is designed to be thread-safe, with features to handle concurrent tag creation and access:

- The `force` parameter in `create_tag` allows for safe retrieval of existing tags
- The `safe_tag` decorator handles race conditions in hierarchical tag creation
- Thread-local registries can be used for isolation
- The `IsolatedTagRegistry` context manager provides test isolation

### Testing with Tags

For testing, use the `IsolatedTagRegistry` context manager to create an isolated tag registry:

```python
from augment_adam.testing.utils.tag_utils import IsolatedTagRegistry

def test_something():
    with IsolatedTagRegistry():
        # Create and use tags without affecting the global registry
        tag = create_tag("test_tag", TagCategory.TEST)
```

## TODOs

- Add support for tag versioning (Issue #4)
- Implement tag validation against a schema (Issue #4)
- Add tag analytics to track usage and coverage (Issue #4)
- Add persistence support (save/load from database) (Issue #4)
- Add tag recommendation based on code content (Issue #4)
- Implement tag inference from code (Issue #4)
- Add tag propagation through the codebase (Issue #4)
- Add tag visualization capabilities (Issue #4)
