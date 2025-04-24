# Memory System in Dukat

This document describes the memory system in Dukat, including the core memory management, working memory, episodic memory, and semantic memory.

## Overview

Dukat implements a comprehensive memory system that provides:

1. **Core memory management** for storing and retrieving information
2. **Working memory** for managing the current conversation
3. **Episodic memory** for storing and retrieving past conversations
4. **Semantic memory** for storing and retrieving concepts and knowledge

## Core Memory Management

The core memory management system is implemented in `dukat.core.memory` and provides the foundation for storing and retrieving information:

```python
from dukat.core.memory import Memory, get_memory

# Create a new memory instance
memory = Memory(
    persist_dir="/path/to/memory",
    collection_name="dukat_memory",
)

# Or get the default instance
memory = get_memory()
```

### Key Features

- **Vector storage** using ChromaDB for efficient similarity search
- **Metadata filtering** for advanced queries
- **Error handling** with retry and circuit breaker patterns
- **Settings integration** for configurable memory behavior

### Methods

#### `add(text, metadata=None, collection_name="main", id_prefix="mem")`

Add a memory to the specified collection:

```python
memory_id = memory.add(
    text="This is a test memory",
    metadata={"type": "note", "tags": ["test", "example"]},
)
```

#### `retrieve(query, n_results=5, collection_name="main", filter_metadata=None)`

Retrieve memories based on a query:

```python
results = memory.retrieve(
    query="test memory",
    n_results=5,
    filter_metadata={"type": "note"},
)
```

#### `get_by_id(memory_id, collection_name="main")`

Retrieve a specific memory by ID:

```python
memory = memory.get_by_id("mem_20250425123456")
```

#### `delete(memory_id, collection_name="main")`

Delete a memory by ID:

```python
success = memory.delete("mem_20250425123456")
```

#### `clear(collection_name="main")`

Clear all memories from a collection:

```python
success = memory.clear()
```

## Working Memory

Working memory is implemented in `dukat.memory.working` and manages the current conversation:

```python
from dukat.memory.working import WorkingMemory, Message

# Create a new working memory instance
memory = WorkingMemory(
    max_messages=100,
    conversation_id="conv_12345",
)
```

### Key Features

- **Message history** for the current conversation
- **Context storage** for conversation-specific information
- **Formatting utilities** for different LLM formats
- **Persistence** for saving and loading conversations

### Methods

#### `add_message(content, role, metadata=None)`

Add a message to the conversation:

```python
message = memory.add_message(
    content="Hello, world!",
    role="user",
    metadata={"sentiment": "positive"},
)
```

#### `get_messages(n=None, roles=None)`

Get messages from the conversation:

```python
# Get the last 5 messages
messages = memory.get_messages(n=5)

# Get only user messages
user_messages = memory.get_messages(roles=["user"])
```

#### `format_history(format="text")`

Format the conversation history for different LLM formats:

```python
# Format as text
text_history = memory.format_history(format="text")

# Format for OpenAI
openai_messages = memory.get_openai_messages()
```

## Episodic Memory

Episodic memory is implemented in `dukat.memory.episodic` and stores past conversations:

```python
from dukat.memory.episodic import EpisodicMemory, Episode

# Create a new episodic memory instance
memory = EpisodicMemory(
    persist_dir="/path/to/memory",
    collection_name="dukat_episodes",
)
```

### Key Features

- **Episode storage** for past conversations
- **Semantic search** for finding relevant episodes
- **Temporal queries** for finding episodes in a time range
- **Metadata filtering** for advanced queries

### Methods

#### `add_episode(content, title=None, metadata=None)`

Add an episode to memory:

```python
episode = memory.add_episode(
    content="User: Hello\nAssistant: Hi there!",
    title="Greeting Conversation",
    metadata={"topic": "greeting", "sentiment": "positive"},
)
```

#### `get_episode(episode_id)`

Get a specific episode by ID:

```python
episode = memory.get_episode("ep_20250425123456")
```

#### `search_episodes(query, n_results=5, filter_metadata=None)`

Search for episodes based on a query:

```python
episodes = memory.search_episodes(
    query="greeting conversation",
    n_results=5,
    filter_metadata={"topic": "greeting"},
)
```

## Semantic Memory

Semantic memory is implemented in `dukat.memory.semantic` and stores concepts and knowledge:

```python
from dukat.memory.semantic import SemanticMemory, Concept

# Create a new semantic memory instance
memory = SemanticMemory(
    persist_dir="/path/to/memory",
    collection_name="dukat_concepts",
)
```

### Key Features

- **Concept storage** for knowledge and information
- **Semantic search** for finding relevant concepts
- **Related concepts** for finding connections between concepts
- **Metadata filtering** for advanced queries

### Methods

#### `add_concept(name, description, content=None, metadata=None)`

Add a concept to memory:

```python
concept = memory.add_concept(
    name="Python",
    description="A high-level programming language",
    content="Python is a high-level, interpreted programming language...",
    metadata={"category": "programming", "tags": ["language", "coding"]},
)
```

#### `get_concept(concept_id)`

Get a specific concept by ID:

```python
concept = memory.get_concept("con_20250425123456")
```

#### `search_concepts(query, n_results=5, filter_metadata=None)`

Search for concepts based on a query:

```python
concepts = memory.search_concepts(
    query="programming language",
    n_results=5,
    filter_metadata={"category": "programming"},
)
```

## Error Handling

The memory system implements robust error handling using the Dukat error handling framework:

```python
from dukat.core.errors import (
    DatabaseError, ResourceError, NotFoundError,
    wrap_error, log_error, retry, CircuitBreaker
)
```

### Retry Pattern

The memory system uses the retry pattern for transient failures:

```python
@retry(max_attempts=2, delay=1.0)
def add(self, text, metadata=None, collection_name="main", id_prefix="mem"):
    # This method will be retried up to 2 times if it fails
    pass
```

### Circuit Breaker Pattern

The memory system uses the circuit breaker pattern to prevent cascading failures:

```python
# Create a circuit breaker for memory retrieval
_retrieve_circuit = CircuitBreaker(
    name="memory_retrieval",
    failure_threshold=3,
    recovery_timeout=30.0,
)

@retry(max_attempts=2, delay=1.0)
@_retrieve_circuit
def retrieve(self, query, n_results=5, collection_name="main", filter_metadata=None):
    # This method is protected by the circuit breaker
    pass
```

### Error Classification

The memory system classifies errors into specific categories:

```python
# Wrap the exception in a DatabaseError
error = wrap_error(
    e,
    message="Error retrieving memories",
    category=ErrorCategory.DATABASE,
    details={
        "collection_name": collection_name,
        "query_length": len(query),
        "n_results": n_results,
    },
)
```

## Settings Integration

The memory system integrates with the Dukat settings system:

```python
from dukat.core.settings import get_settings

# Get settings for memory configuration
settings = get_settings()
memory_settings = settings.memory

# Use settings for memory configuration
working_memory_size = memory_settings.working_memory_size
semantic_memory_enabled = memory_settings.semantic_memory_enabled
episodic_memory_enabled = memory_settings.episodic_memory_enabled
```

## Best Practices

1. **Use the appropriate memory type**: Use working memory for the current conversation, episodic memory for past conversations, and semantic memory for concepts and knowledge.
2. **Add metadata**: Always add metadata to memories to enable advanced filtering and retrieval.
3. **Handle errors**: Handle memory errors gracefully to prevent cascading failures.
4. **Use settings**: Use settings to configure memory behavior instead of hardcoding values.
5. **Clean up**: Regularly clean up old or irrelevant memories to maintain performance.

## Example: Conversation with Memory

```python
from dukat.core.memory import get_memory
from dukat.memory.working import WorkingMemory, Message
from dukat.memory.episodic import EpisodicMemory
from dukat.memory.semantic import SemanticMemory, Concept

# Create memory instances
core_memory = get_memory()
working_memory = WorkingMemory()
episodic_memory = EpisodicMemory()
semantic_memory = SemanticMemory()

# Add a user message to working memory
working_memory.add_message(
    content="What is Python?",
    role="user",
)

# Check if we have a concept for Python
python_concepts = semantic_memory.search_concepts("Python programming language")
if python_concepts:
    # Use the concept to generate a response
    concept, score = python_concepts[0]
    response = f"Python is {concept.description}. {concept.content}"
else:
    # Generate a response without a concept
    response = "Python is a high-level programming language known for its readability."
    
    # Add the concept to semantic memory
    semantic_memory.add_concept(
        name="Python",
        description="a high-level programming language",
        content="Python is known for its readability and versatility.",
        metadata={"category": "programming", "tags": ["language", "coding"]},
    )

# Add the assistant's response to working memory
working_memory.add_message(
    content=response,
    role="assistant",
)

# Save the conversation to episodic memory
conversation_history = working_memory.format_history()
episodic_memory.add_episode(
    content=conversation_history,
    title="Python Discussion",
    metadata={"topic": "programming", "language": "python"},
)
```

## Conclusion

Dukat's memory system provides a robust foundation for storing and retrieving information across conversations. By using different types of memory and integrating with the error handling and settings systems, Dukat can provide a more personalized and reliable experience.
