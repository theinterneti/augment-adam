# Tagging System API

This document provides a reference for the Tagging System API in Augment Adam.

## Core Classes

### Tag

The `Tag` class represents a tag that can be applied to code, templates, and other resources.

```python
from augment_adam.utils.tagging import Tag, TagCategory

# Create a tag
tag = Tag(
    name="faiss",
    category=TagCategory.MEMORY,
    parent=memory_tag,
    description="FAISS-based vector memory",
    examples=["FAISSMemory class", "faiss_search function"],
    synonyms=["facebook ai similarity search", "vector database"]
)
```

#### Properties

| Property | Description |
| -------- | ----------- |
| `name` | The name of the tag |
| `category` | The category of the tag |
| `parent` | Optional parent tag |
| `attributes` | Optional attributes for the tag |
| `children` | Child tags |
| `description` | Human and AI readable description of what this tag represents |
| `examples` | List of example usages to help AI understand the tag's purpose |
| `relationships` | Dictionary mapping related tags to their relationship types |
| `synonyms` | Alternative names or terms for this tag concept |
| `importance` | Numeric value (0-10) indicating the tag's importance in the system |
| `created_at` | When this tag was first created (ISO format date string) |
| `updated_at` | When this tag was last updated (ISO format date string) |

#### Methods

| Method | Description |
| ------ | ----------- |
| `add_child(tag)` | Add a child tag |
| `add_relationship(tag, relationship)` | Add a relationship to another tag |
| `get_relationships()` | Get all relationships for this tag |
| `get_related_tags(relationship)` | Get tags related to this tag by relationship |
| `get_attribute(key)` | Get the value of a tag attribute |
| `set_attribute(key, value)` | Set the value of a tag attribute |
| `is_child_of(tag)` | Check if this tag is a child of another tag |
| `get_ancestors()` | Get all ancestors of this tag |
| `get_descendants()` | Get all descendants of this tag |
| `get_semantic_description()` | Get a rich semantic description of this tag |

### TagCategory

The `TagCategory` enum defines the categories for tags.

```python
from augment_adam.utils.tagging import TagCategory

# Use a tag category
category = TagCategory.MEMORY
```

#### Values

| Value | Description |
| ----- | ----------- |
| `MEMORY` | Memory-related tags (storage, retrieval, management) |
| `MODEL` | Model-related tags (AI models, embeddings, inference) |
| `AGENT` | Agent-related tags (autonomous entities, behaviors) |
| `CONTEXT` | Context-related tags (information environment, state) |
| `UTILITY` | Utility-related tags (helper functions, tools) |
| `TEMPLATE` | Template-related tags (code generation, patterns) |
| `TEST` | Test-related tags (validation, verification) |
| `DOCUMENTATION` | Documentation-related tags (explanations, guides) |
| `WEB` | Web-related tags (HTTP, browsers, frontend/backend) |
| `API` | API-related tags (interfaces, endpoints, protocols) |
| `PLUGIN` | Plugin-related tags (extensions, add-ons) |
| `CORE` | Core functionality tags (essential components) |
| `DATA` | Data-related tags (processing, transformation) |
| `SECURITY` | Security-related tags (authentication, encryption) |
| `PERFORMANCE` | Performance-related tags (optimization, efficiency) |
| `UI` | User interface tags (interaction, display) |

### TagRelationship

The `TagRelationship` enum defines the semantic relationships between tags.

```python
from augment_adam.utils.tagging import TagRelationship

# Use a tag relationship
relationship = TagRelationship.USES
```

#### Values

| Value | Description |
| ----- | ----------- |
| `USES` | Tag A uses functionality from Tag B |
| `IMPLEMENTS` | Tag A implements interface/contract defined by Tag B |
| `EXTENDS` | Tag A extends or enhances Tag B |
| `DEPENDS_ON` | Tag A depends on Tag B (stronger than USES) |
| `ALTERNATIVE_TO` | Tag A is an alternative implementation to Tag B |
| `COMPOSES` | Tag A is composed of Tag B components |
| `GENERATES` | Tag A generates Tag B artifacts |
| `CONFIGURES` | Tag A configures Tag B behavior |
| `PROCESSES` | Tag A processes Tag B data/objects |
| `COMMUNICATES_WITH` | Tag A communicates with Tag B |
| `PRECEDES` | Tag A precedes Tag B in a workflow/pipeline |
| `SUCCEEDS` | Tag A succeeds Tag B in a workflow/pipeline |
| `TESTS` | Tag A tests Tag B functionality |
| `DOCUMENTS` | Tag A documents Tag B |
| `OPTIMIZES` | Tag A optimizes Tag B |
| `SECURES` | Tag A provides security for Tag B |

### TagRegistry

The `TagRegistry` class is responsible for creating, retrieving, and organizing tags.

```python
from augment_adam.utils.tagging import TagRegistry, TagCategory

# Create a tag registry
registry = TagRegistry()

# Create a tag
tag = registry.create_tag("faiss", TagCategory.MEMORY, "vector")
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `create_tag(name, category, parent, attributes)` | Create a new tag |
| `get_tag(name)` | Get a tag by name |
| `get_or_create_tag(name, category, parent, attributes)` | Get a tag by name or create it if it doesn't exist |
| `get_tags_by_category(category)` | Get tags by category |
| `get_tags_by_attribute(key, value)` | Get tags by attribute |
| `get_tags_by_parent(parent)` | Get tags by parent |
| `get_tags_by_relationship(tag, relationship)` | Get tags by relationship |
| `get_tag_hierarchy(tag)` | Get the complete hierarchy for a tag |
| `relate_tags(tag1, tag2, relationship)` | Create a relationship between two tags |
| `find_tags(query, search_descriptions, search_attributes, search_synonyms)` | Find tags matching a search query |

## Utility Functions

### Tag Management

```python
from augment_adam.utils.tagging import get_tag, create_tag, get_or_create_tag

# Get a tag by name
tag = get_tag("faiss")

# Create a new tag
tag = create_tag("chroma", TagCategory.MEMORY, "vector")

# Get a tag by name or create it if it doesn't exist
tag = get_or_create_tag("redis", TagCategory.MEMORY, "vector")
```

### Tag Filtering

```python
from augment_adam.utils.tagging import get_tags_by_category, get_related_tags

# Get tags by category
memory_tags = get_tags_by_category(TagCategory.MEMORY)

# Get related tags
related_tags = get_related_tags("faiss", TagRelationship.ALTERNATIVE_TO)
```

### Tag Search

```python
from augment_adam.utils.tagging import find_tags

# Find tags matching a search query
vector_tags = find_tags("vector")

# Find tags with "embedding" in their description
embedding_tags = find_tags("embedding", search_descriptions=True)
```

### Tag Description

```python
from augment_adam.utils.tagging import describe_tag

# Get a rich semantic description of a tag
description = describe_tag("faiss")
```

### Tag Decoration

```python
from augment_adam.utils.tagging import tag

# Decorate a class with a tag
@tag("memory.vector.faiss")
class FAISSMemory:
    """FAISS-based vector memory."""
    pass

# Decorate a function with a tag
@tag("memory.vector.faiss.search")
def faiss_search(query, k=5):
    """Search for similar vectors in FAISS."""
    pass
```

### Tag Inspection

```python
from augment_adam.utils.tagging import get_tags

# Get tags applied to an object
tags = get_tags(FAISSMemory)
```

## Tag Hierarchies

The tagging system defines several tag hierarchies:

### Memory Hierarchy

```
memory
├── vector
│   ├── faiss
│   └── chroma
├── neo4j
├── graph
├── episodic
├── semantic
└── working
```

### Model Hierarchy

```
model
├── anthropic
├── openai
├── huggingface
├── ollama
└── embedding
```

### Agent Hierarchy

```
agent
├── mcp
├── worker
├── coordination
│   ├── team
│   └── workflow
├── reasoning
│   ├── planning
│   ├── reflection
│   ├── decision
│   ├── knowledge
│   └── chain_of_thought
└── smc
    ├── particle
    ├── sampler
    └── potential
```

### Context Hierarchy

```
context
├── chunking
├── composition
├── retrieval
└── prompt
```

### Utility Hierarchy

```
utility
├── template
│   └── jinja
└── hardware
```

### Template Hierarchy

```
template_type
├── code
├── test
├── doc
└── memory_template
```

### Test Hierarchy

```
test_type
├── unit
├── integration
├── e2e
├── performance
├── stress
└── compatibility
```

### Documentation Hierarchy

```
doc_type
├── api
├── guide
├── tutorial
└── reference
```

### Web Hierarchy

```
web
├── frontend
├── backend
└── api_endpoint
```

### API Hierarchy

```
api_type
├── rest
├── graphql
└── websocket
```

### Plugin Hierarchy

```
plugin
├── file_manager
├── web_search
└── system_info
```

### Core Hierarchy

```
core
├── settings
├── errors
├── async
├── parallel
└── task
```

## Examples

### Creating and Using Tags

```python
from augment_adam.utils.tagging import create_tag, TagCategory, TagRelationship

# Create a memory tag
memory_tag = create_tag("memory", TagCategory.MEMORY)

# Create a vector tag as a child of memory
vector_tag = create_tag("vector", TagCategory.MEMORY, "memory")

# Create a faiss tag as a child of vector
faiss_tag = create_tag("faiss", TagCategory.MEMORY, "vector")

# Create a chroma tag as a child of vector
chroma_tag = create_tag("chroma", TagCategory.MEMORY, "vector")

# Create a relationship between faiss and chroma
from augment_adam.utils.tagging import relate_tags
relate_tags("faiss", "chroma", TagRelationship.ALTERNATIVE_TO)
```

### Tagging Code

```python
from augment_adam.utils.tagging import tag

# Tag a class
@tag("memory.vector.faiss")
class FAISSMemory:
    """FAISS-based vector memory."""
    
    def __init__(self, path="./data/faiss"):
        """Initialize the FAISS memory."""
        self.path = path
        
    def search(self, query, k=5):
        """Search for similar vectors in FAISS."""
        pass

# Tag a function
@tag("memory.vector.faiss.search")
def faiss_search(query, k=5):
    """Search for similar vectors in FAISS."""
    pass
```

### Finding Tags

```python
from augment_adam.utils.tagging import find_tags, get_tags_by_category, TagCategory

# Find tags matching a search query
vector_tags = find_tags("vector")
print(f"Vector tags: {[tag.name for tag in vector_tags]}")

# Find tags with "embedding" in their description
embedding_tags = find_tags("embedding", search_descriptions=True)
print(f"Embedding tags: {[tag.name for tag in embedding_tags]}")

# Get all memory-related tags
memory_tags = get_tags_by_category(TagCategory.MEMORY)
print(f"Memory tags: {[tag.name for tag in memory_tags]}")
```

### Getting Related Tags

```python
from augment_adam.utils.tagging import get_related_tags, TagRelationship

# Get tags related to the memory tag
related_to_memory = get_related_tags("memory")
print(f"Tags related to memory: {[tag.name for tag in related_to_memory]}")

# Get tags that the memory tag uses
memory_uses = get_related_tags("memory", TagRelationship.USES)
print(f"Tags that memory uses: {[tag.name for tag in memory_uses]}")

# Get alternatives to faiss
faiss_alternatives = get_related_tags("faiss", TagRelationship.ALTERNATIVE_TO)
print(f"Alternatives to faiss: {[tag.name for tag in faiss_alternatives]}")
```

### Getting Semantic Descriptions

```python
from augment_adam.utils.tagging import describe_tag

# Get a detailed description of the memory tag
memory_description = describe_tag("memory")
print(f"Memory description: {memory_description}")

# Get a detailed description of the faiss tag
faiss_description = describe_tag("faiss")
print(f"FAISS description: {faiss_description}")
```

### Inspecting Tagged Objects

```python
from augment_adam.utils.tagging import get_tags

# Get tags applied to a class
tags = get_tags(FAISSMemory)
print(f"Tags applied to FAISSMemory: {[tag.name for tag in tags]}")

# Get tags applied to a function
tags = get_tags(faiss_search)
print(f"Tags applied to faiss_search: {[tag.name for tag in tags]}")
```
