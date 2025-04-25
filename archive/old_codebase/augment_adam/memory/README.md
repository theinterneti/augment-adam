# Augment Adam Memory Module

This module provides memory systems for the Augment Adam assistant, allowing it to store and retrieve information efficiently.

## Overview

The memory module includes:

- A common interface for all memory systems
- FAISS-based memory implementation for efficient vector storage and retrieval
- Neo4j-based memory implementation for graph-based vector storage and retrieval
- A memory factory for creating different types of memory systems

## Memory Interface

All memory systems implement the `MemoryInterface`, which defines the following methods:

- `add`: Add a memory to a collection
- `retrieve`: Retrieve memories similar to a query
- `get_by_id`: Get a memory by ID
- `delete`: Delete a memory by ID
- `clear`: Clear all memories from a collection

## FAISS Memory

The FAISS memory implementation uses Facebook AI Similarity Search (FAISS) for efficient vector storage and retrieval. It provides:

- Fast similarity search for large collections of vectors
- Persistent storage of vectors and metadata
- Filtering based on metadata

## Neo4j Memory

The Neo4j memory implementation uses Neo4j graph database for graph-based vector storage and retrieval. It provides:

- Fast similarity search for large collections of vectors
- Graph-based relationships between memories
- Filtering based on metadata
- Advanced graph queries

## Memory Factory

The memory factory provides a simple way to create different types of memory systems:

```python
from augment_adam.memory.memory_factory import create_memory, get_default_memory

# Create a FAISS memory instance
faiss_memory = create_memory(
    memory_type="faiss",
    persist_dir="/path/to/memory",
    collection_name="my_collection"
)

# Create a Neo4j memory instance
neo4j_memory = create_memory(
    memory_type="neo4j",
    collection_name="my_collection"
)

# Get the default memory instance (based on settings)
default_memory = get_default_memory()
```

## Usage Example

```python
from augment_adam.memory.memory_factory import create_memory

# Create a memory instance
memory = create_memory(memory_type="faiss")

# Add a memory
memory_id = memory.add(
    text="Python is a programming language with simple syntax and powerful libraries.",
    metadata={"type": "note", "topic": "programming", "language": "python"}
)

# Retrieve memories
results = memory.retrieve(
    query="programming language",
    n_results=5,
    filter_metadata={"topic": "programming"}
)

# Process results
for memory, similarity in results:
    print(f"Memory: {memory['text']}")
    print(f"Similarity: {similarity}")
    print(f"Metadata: {memory}")
    print()

# Get a memory by ID
memory = memory.get_by_id(memory_id)

# Delete a memory
memory.delete(memory_id)

# Clear a collection
memory.clear()
```

## Configuration

Memory systems can be configured through the settings system:

```python
from augment_adam.core.settings import update_settings

# Configure the default memory backend
update_settings({
    "memory": {
        "default_memory_backend": "faiss"  # or "neo4j"
    }
})
```
