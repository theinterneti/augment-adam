# Intelligent Context Engine

## Overview

This module provides an intelligent context engine for better context management, chunking, composition, retrieval, and prompt management. It integrates with memory systems for efficient storage and retrieval of context.

## Components

### Core

The core components of the context engine include:

- **Context**: Class representing a context for AI models
- **ContextType**: Enum defining the types of context
- **ContextEngine**: Engine for managing context
- **ContextManager**: Manager for multiple context engines

### Chunking

The chunking module provides tools for breaking down content into smaller chunks:

- **Chunker**: Base class for content chunkers
- **TextChunker**: Chunker for text content
- **CodeChunker**: Chunker for code content
- **SemanticChunker**: Chunker for semantic content

### Composition

The composition module provides tools for combining multiple contexts:

- **ContextComposer**: Base class for context composers
- **SequentialComposer**: Composer for sequential composition
- **HierarchicalComposer**: Composer for hierarchical composition
- **SemanticComposer**: Composer for semantic composition

### Retrieval

The retrieval module provides tools for finding relevant contexts:

- **ContextRetriever**: Base class for context retrievers
- **VectorRetriever**: Retriever for vector-based retrieval
- **GraphRetriever**: Retriever for graph-based retrieval
- **HybridRetriever**: Retriever for hybrid retrieval

### Prompt

The prompt module provides tools for managing prompts:

- **PromptTemplate**: Template for generating prompts
- **PromptManager**: Manager for prompt templates

### Storage

The storage module provides backends for storing contexts:

- **ContextStorage**: Base class for context storage backends
- **RedisStorage**: Redis-based context storage
- **ChromaStorage**: Chroma-based context storage
- **HybridStorage**: Hybrid context storage

### Async

The async module provides tools for asynchronous context building:

- **AsyncContextBuilder**: Base class for async context builders
- **AsyncContextTask**: Task for asynchronous context building
- **AsyncContextManager**: Manager for asynchronous context building

## Usage

### Creating a Context Engine

```python
from augment_adam.context import (
    ContextEngine,
    TextChunker,
    SequentialComposer,
    VectorRetriever,
    RedisStorage,
)

# Create components
chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
composer = SequentialComposer(separator="\n\n")
retriever = VectorRetriever(vector_store=my_vector_store, embedding_model="my_model")
storage = RedisStorage(redis_client=my_redis_client)

# Create context engine
engine = ContextEngine(
    name="my_engine",
    chunker=chunker,
    composer=composer,
    retriever=retriever,
    storage=storage,
)
```

### Adding Context

```python
from augment_adam.context import Context, ContextType

# Create a context
context = Context(
    content="This is a test context",
    context_type=ContextType.TEXT,
    metadata={"source": "user", "type": "text"},
    importance=0.8,
    tags=["test", "example"],
)

# Add the context to the engine
context_id = engine.add_context(context)
```

### Chunking Content

```python
# Chunk content
chunks = engine.chunk_content(
    content="This is a long text that needs to be chunked...",
    context_type=ContextType.TEXT,
    chunk_size=500,
    chunk_overlap=100,
)

# Add chunks to the engine
for chunk in chunks:
    engine.add_context(chunk)
```

### Composing Contexts

```python
# Get contexts to compose
contexts = [engine.get_context(context_id) for context_id in context_ids]

# Compose contexts
composed_context = engine.compose_context(
    contexts=contexts,
    separator="\n\n",
    include_metadata=True,
)

# Add the composed context to the engine
composed_id = engine.add_context(composed_context)
```

### Retrieving Contexts

```python
# Retrieve contexts based on a query
results = engine.retrieve_context(
    query="test query",
    limit=5,
    context_type=ContextType.TEXT,
)

# Process results
for context in results:
    print(f"ID: {context.id}")
    print(f"Content: {context.content}")
    print(f"Importance: {context.importance}")
    print("---")
```

### Using the Context Manager

```python
from augment_adam.context import get_context_manager

# Get the context manager
manager = get_context_manager()

# Register engines
manager.register_engine(engine1)
manager.register_engine(engine2)

# Add a context to an engine
context_id = manager.add_context("engine1", context)

# Retrieve a context
context = manager.get_context("engine1", context_id)

# Chunk content using an engine
chunks = manager.chunk_content("engine1", content, ContextType.TEXT)

# Compose contexts using an engine
composed = manager.compose_context("engine1", contexts)

# Retrieve contexts using an engine
results = manager.retrieve_context("engine1", query, limit=5)
```

### Using Prompt Templates

```python
from augment_adam.context import PromptTemplate, get_prompt_manager

# Create a prompt template
template = PromptTemplate(
    name="my_template",
    template="System: {system}\n\nUser: {user}\n\nContext: {context:TEXT:limit=3:separator=\\n\\n}",
    variables={"system": "You are a helpful assistant."},
)

# Get the prompt manager
manager = get_prompt_manager()

# Add the template to the manager
template_id = manager.add_template(template)

# Render the template
prompt = manager.render_template(
    template_id,
    variables={"user": "Tell me about context engines."},
    contexts=contexts,
)
```

### Using Async Context Building

```python
from augment_adam.context import AsyncContextBuilder, get_async_context_manager

# Create a custom context builder
class MyContextBuilder(AsyncContextBuilder):
    def build(self, engine, parameters):
        # Build a context based on parameters
        content = parameters.get("content", "")
        context_type = parameters.get("context_type", ContextType.TEXT)
        
        # Process content
        processed_content = process_content(content)
        
        # Create context
        context = Context(
            content=processed_content,
            context_type=context_type,
            metadata={"builder": self.name},
        )
        
        return context

# Register the builder
builder = MyContextBuilder(name="my_builder")
manager = get_async_context_manager()
manager.register_engine(engine)
manager.register_builder(builder)

# Submit a task
task_id = manager.submit_task(
    engine_name="my_engine",
    builder_name="my_builder",
    parameters={"content": "Raw content to process", "context_type": ContextType.TEXT},
)

# Check task status
task = manager.get_task(task_id)
print(f"Task status: {task.status.name}")

# Get task result
context, error = manager.get_result(task_id)
if error:
    print(f"Error: {error}")
else:
    print(f"Context ID: {context.id}")
    print(f"Content: {context.content}")
```

## TODOs

- Add context versioning support (Issue #7)
- Implement context validation against a schema (Issue #7)
- Add context analytics to track usage and performance (Issue #7)
- Add support for more embedding models (Issue #7)
- Implement more sophisticated chunking strategies (Issue #7)
- Add support for more storage backends (Issue #7)
- Implement more advanced retrieval methods (Issue #7)
