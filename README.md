# Augment Adam

An intelligent assistant with advanced memory capabilities.

## Features

- **Multiple Memory Systems**: FAISS, Neo4j, and working memory integration
- **Memory Interface**: Common interface for all memory systems
- **Memory Factory**: Easy creation of different memory systems
- **AI Agent**: Flexible AI agent architecture with model management
- **Context Engine**: Advanced context management with vector search and knowledge graphs
- **Plugin System**: Extensible plugin architecture
- **Web Interface**: Interactive web interface for visualization and management

## Installation

```bash
# Basic installation
pip install augment-adam

# With Neo4j support
pip install augment-adam[neo4j]

# With development tools
pip install augment-adam[dev]
```

## Quick Start

```python
from augment_adam.memory import create_memory

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
```

## Memory Systems

Augment Adam provides multiple memory systems with a common interface:

- **FAISS Memory**: Vector-based memory using Facebook AI Similarity Search

  - Fast similarity search for large collections of vectors
  - Persistent storage of vectors and metadata
  - Filtering based on metadata

- **Neo4j Memory**: Graph-based memory using Neo4j
  - Graph-based relationships between memories
  - Advanced graph queries
  - Filtering based on metadata

## Memory Factory

The memory factory provides a simple way to create different types of memory systems:

```python
from augment_adam.memory import create_memory, get_default_memory

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

## Documentation

For more detailed documentation, see the [docs](docs/) directory.

## License

MIT
