# FAISS-Based Memory System

The Dukat project includes a FAISS-based memory system for efficient vector storage and retrieval. This document provides guidance on using the FAISS-based memory system.

## Overview

The FAISS-based memory system allows you to:

1. Store and retrieve vector embeddings efficiently
2. Perform similarity searches on large datasets
3. Filter results based on metadata
4. Manage episodic and semantic memory

## FAISSMemory

The `FAISSMemory` class is the core component of the FAISS-based memory system.

```python
from dukat.memory.faiss_memory import FAISSMemory, get_faiss_memory

# Create a FAISS memory instance
memory = FAISSMemory(
    persist_dir="/path/to/memory",
    collection_name="my_collection",
    embedding_model="all-MiniLM-L6-v2"
)

# Or get the default instance
memory = get_faiss_memory()

# Add a memory
memory_id = memory.add(
    text="This is a test memory",
    metadata={"type": "note", "tags": ["test", "example"]},
    collection_name="main",
    id_prefix="mem"
)

# Retrieve memories
results = memory.retrieve(
    query="test memory",
    n_results=5,
    filter_metadata={"type": "note"},
    collection_name="main"
)

# Get a memory by ID
memory = memory.get_by_id("mem_12345678")

# Delete a memory
success = memory.delete("mem_12345678")

# Clear a collection
success = memory.clear()
```

## FAISSEpisodicMemory

The `FAISSEpisodicMemory` class provides episodic memory functionality using FAISS.

```python
from dukat.memory.faiss_episodic import FAISSEpisodicMemory, Episode

# Create a FAISS episodic memory instance
memory = FAISSEpisodicMemory(
    persist_dir="/path/to/memory",
    collection_name="my_episodes",
    embedding_model="all-MiniLM-L6-v2"
)

# Add an episode
episode = memory.add_episode(
    content="User: Hello\nAssistant: Hi there!",
    title="Greeting Conversation",
    metadata={"topic": "greeting", "sentiment": "positive"}
)

# Get an episode by ID
episode = memory.get_episode("ep_12345678")

# Search for episodes
episodes = memory.search_episodes(
    query="greeting conversation",
    n_results=5,
    filter_metadata={"topic": "greeting"}
)

# Get recent episodes
episodes = memory.get_recent_episodes(
    n=5,
    filter_metadata={"sentiment": "positive"}
)

# Get episodes in a time range
episodes = memory.get_episodes_in_timerange(
    start_time=1000,
    end_time=2000,
    filter_metadata={"topic": "greeting"}
)

# Delete an episode
success = memory.delete_episode("ep_12345678")

# Clear all episodes
success = memory.clear()
```

## FAISSSemanticMemory

The `FAISSSemanticMemory` class provides semantic memory functionality using FAISS.

```python
from dukat.memory.faiss_semantic import FAISSSemanticMemory, Concept

# Create a FAISS semantic memory instance
memory = FAISSSemanticMemory(
    persist_dir="/path/to/memory",
    collection_name="my_concepts",
    embedding_model="all-MiniLM-L6-v2"
)

# Add a concept
concept = memory.add_concept(
    name="Python",
    description="A programming language",
    content="Python is a high-level programming language...",
    metadata={"type": "language", "paradigm": "multi-paradigm"}
)

# Get a concept by ID
concept = memory.get_concept("con_12345678")

# Get a concept by name
concept = memory.get_concept_by_name("Python", exact_match=True)

# Search for concepts
concepts = memory.search_concepts(
    query="programming language",
    n_results=5,
    filter_metadata={"type": "language"}
)

# Delete a concept
success = memory.delete_concept("con_12345678")

# Clear all concepts
success = memory.clear()
```

## Integration with Working Memory

The FAISS-based memory system can be integrated with the working memory system:

```python
from dukat.memory.working import WorkingMemory, Message
from dukat.memory.faiss_episodic import FAISSEpisodicMemory
from dukat.memory.faiss_semantic import FAISSSemanticMemory

# Create memory instances
working_memory = WorkingMemory()
episodic_memory = FAISSEpisodicMemory()
semantic_memory = FAISSSemanticMemory()

# Add messages to working memory
working_memory.add_message(Message(role="user", content="What is Python?"))
working_memory.add_message(Message(
    role="assistant",
    content="Python is a high-level programming language..."
))

# Get conversation history
history = working_memory.format_history()

# Store in episodic memory
episode = episodic_memory.add_episode(
    content=history,
    title="Python Discussion",
    metadata={"topic": "programming"}
)

# Extract concepts and store in semantic memory
concept = semantic_memory.add_concept(
    name="Python",
    description="A programming language",
    content="Python is a high-level programming language...",
    metadata={"type": "language"}
)
```

## Performance Considerations

### Embedding Models

The FAISS-based memory system uses SentenceTransformer models for creating embeddings. The default model is `all-MiniLM-L6-v2`, which provides a good balance between performance and quality. You can use other models by specifying the `embedding_model` parameter when creating memory instances.

### Memory Usage

FAISS is designed to be memory-efficient, but large indices can still consume significant memory. Consider the following:

- Use smaller embedding models for large datasets
- Implement pagination for large result sets
- Use appropriate FAISS index types for your use case

### Persistence

The FAISS-based memory system persists data to disk, allowing it to be reloaded between sessions. The data is stored in the following files:

- `index.faiss`: The FAISS index
- `metadata.json`: Metadata for each document
- `ids.json`: Document IDs

## Comparison with ChromaDB

The FAISS-based memory system provides an alternative to the ChromaDB-based memory system. Here are some key differences:

| Feature | FAISS | ChromaDB |
|---------|-------|----------|
| Speed | Faster for large datasets | Good for small to medium datasets |
| Memory Usage | More efficient | Can be memory-intensive |
| Filtering | Basic metadata filtering | Advanced filtering capabilities |
| Persistence | Simple file-based | Database-like persistence |
| Embedding | External (SentenceTransformer) | Built-in |

## Best Practices

1. **Choose the Right Embedding Model**: Select an embedding model that balances performance and quality for your use case.

2. **Use Metadata Effectively**: Add relevant metadata to memories to enable effective filtering.

3. **Implement Regular Maintenance**: Periodically clean up old or irrelevant memories to maintain performance.

4. **Backup Data**: Regularly backup the FAISS index and metadata files to prevent data loss.

5. **Monitor Memory Usage**: Keep an eye on memory usage, especially for large datasets.

## References

- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [SentenceTransformer Documentation](https://www.sbert.net/)
- [Vector Search Guide](https://www.pinecone.io/learn/vector-search-guide/)
