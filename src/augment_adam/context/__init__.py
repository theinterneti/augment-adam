"""
Intelligent Context Engine.

This module provides an intelligent context engine for better context management,
chunking, composition, retrieval, and prompt management. It integrates with
memory systems for efficient storage and retrieval of context.

TODO(Issue #7): Add context versioning support
TODO(Issue #7): Implement context validation against a schema
TODO(Issue #7): Add context analytics to track usage and performance
"""

from augment_adam.context.core.base import (
    Context,
    ContextType,
    ContextEngine,
    ContextManager,
    get_context_manager,
)

from augment_adam.context.chunking.base import (
    Chunker,
    TextChunker,
    CodeChunker,
    SemanticChunker,
)

from augment_adam.context.composition.base import (
    ContextComposer,
    SequentialComposer,
    HierarchicalComposer,
    SemanticComposer,
)

from augment_adam.context.retrieval.base import (
    ContextRetriever,
    VectorRetriever,
    GraphRetriever,
    HybridRetriever,
)

from augment_adam.context.prompt.base import (
    PromptTemplate,
    PromptManager,
    get_prompt_manager,
)

from augment_adam.context.storage.base import (
    ContextStorage,
    RedisStorage,
    ChromaStorage,
    HybridStorage,
)

from augment_adam.context.async_module.base import (
    AsyncContextBuilder,
    AsyncContextTask,
    AsyncContextManager,
    get_async_context_manager,
)

__all__ = [
    # Core
    "Context",
    "ContextType",
    "ContextEngine",
    "ContextManager",
    "get_context_manager",

    # Chunking
    "Chunker",
    "TextChunker",
    "CodeChunker",
    "SemanticChunker",

    # Composition
    "ContextComposer",
    "SequentialComposer",
    "HierarchicalComposer",
    "SemanticComposer",

    # Retrieval
    "ContextRetriever",
    "VectorRetriever",
    "GraphRetriever",
    "HybridRetriever",

    # Prompt
    "PromptTemplate",
    "PromptManager",
    "get_prompt_manager",

    # Storage
    "ContextStorage",
    "RedisStorage",
    "ChromaStorage",
    "HybridStorage",

    # Async
    "AsyncContextBuilder",
    "AsyncContextTask",
    "AsyncContextManager",
    "get_async_context_manager",
]
