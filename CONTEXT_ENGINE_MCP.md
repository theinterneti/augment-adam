# Context Engine with MCP

A high-performance context engine with Model Context Protocol (MCP) integration, built with Redis and Neo4j.

## Architecture

This context engine uses a hybrid approach combining:

1. **Redis with Vector Search**: For high-speed real-time vector similarity searches
2. **Neo4j with Vector Capabilities**: For graph relationships and background processing
3. **Tiered Memory Architecture**: To balance performance and resource usage
4. **Asynchronous Processing Framework**: For handling background tasks
5. **Model Context Protocol (MCP)**: For standardized tool access

## Key Features

- **Real-time Vector Search**: Sub-millisecond vector similarity search using Redis
- **Graph-aware Context**: Relationship-based context retrieval using Neo4j
- **Tiered Memory**: Hot, warm, and cold tiers for optimal performance and resource usage
- **Asynchronous Processing**: Background tasks for resource-intensive operations
- **MCP Integration**: Standardized tool interface for AI models

## MCP Tools

The context engine exposes the following MCP tools:

1. **vector_search**: Search for vectors similar to a query text
2. **vector_store**: Store a vector in the database
3. **code_index**: Index code in the database
4. **create_relationship**: Create a relationship between two vectors
5. **get_related_vectors**: Get vectors related to a vector

## Components

- **Redis Vector Database**: Optimized for real-time vector similarity search
- **Neo4j Graph Database**: Stores relationships and provides graph-aware context
- **MCP Server**: FastAPI-based MCP server for tool access
- **Worker Service**: Background processing for resource-intensive tasks

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+

### Installation

1. Clone the repository
2. Run the setup script:

```bash
chmod +x setup_context_engine.sh
./setup_context_engine.sh
```

### Testing

Run the test script to verify the installation:

```bash
python test_context_engine.py
```

### Using the Client Library

The context engine comes with a client library for easy integration:

```python
from context_engine_client import ContextEngineClient

# Initialize the client
client = ContextEngineClient("http://localhost:8080")

# Search for vectors
results = client.vector_search("function that prints hello world")

# Store a vector
result = client.vector_store(
    text="def hello_world():\n    print('Hello, world!')",
    metadata={"file_path": "hello.py", "language": "python"}
)

# Index code
result = client.code_index(
    code="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
    file_path="factorial.py"
)

# Create a relationship
result = client.create_relationship(
    from_id="vector_id_1",
    to_id="vector_id_2",
    relationship_type="RELATED_TO"
)

# Get related vectors
results = client.get_related_vectors(
    vector_id="vector_id_1",
    relationship_type="RELATED_TO"
)

# Index a repository
results = client.index_repository("/path/to/repository")
```

## MCP Integration

The context engine can be used with any MCP-compatible client:

```python
from mcp import MCPClient

# Initialize the MCP client
client = MCPClient("http://localhost:8080")

# Search for vectors
result = client.call_tool(
    "vector_search",
    {
        "query": "function that prints hello world",
        "k": 10,
        "include_metadata": True
    }
)

# Store a vector
result = client.call_tool(
    "vector_store",
    {
        "text": "def hello_world():\n    print('Hello, world!')",
        "metadata": {"file_path": "hello.py", "language": "python"},
        "tier": "hot"
    }
)
```

# MCP Server vs. Context Engine: Clarification

## Overview
This project uses both a Model Context Protocol (MCP) server and a context engine for memory and knowledge management. While they are related, they serve distinct roles and should not be confused.

## MCP Server
- The docker-mcp server provides a standardized API (Model Context Protocol) for accessing tools, memory, and knowledge graphs across different services and containers.
- It acts as a bridge, allowing external clients (including other containers, services, or agents) to connect and interact with the memory system via a well-defined protocol.
- The MCP server is typically started using `simple_mcp_server.py` or via Docker using `Dockerfile.mcp-context-engine` and the appropriate docker-compose file (e.g., `mcp-context-engine-docker-compose.yml`).
- **How to connect:**
  - From another container or service, connect to the MCP server using the network address and port defined in your docker-compose file (e.g., `localhost:8080` or the service name in Docker).
  - Use the MCP client (e.g., `mcp_context_engine_client.py`) to send requests following the MCP API (see `MCP_CONTEXT_ENGINE.md` for details).

## Context Engine
- The context engine is the core logic for managing memory, context, and knowledge within this project.
- It provides APIs and internal logic for storing, retrieving, and updating memory elements (e.g., working memory, episodic memory, semantic memory).
- The context engine is used directly by the assistant (Dukat), plugins, and other internal modules.
- It is not itself a network service, but can be exposed via the MCP server for remote access.
- Key files: `context_engine/` (core logic), `context_engine_client.py` (local client), `CONTEXT_ENGINE.md` (documentation).

## Memory Elements
- **Working Memory:** Short-term, session-based context (e.g., current conversation).
- **Episodic Memory:** Stores past interactions or events.
- **Semantic Memory:** Stores knowledge, facts, and embeddings (often using ChromaDB).
- These memory types are managed by the context engine and can be accessed locally or via the MCP server.

## Key Distinctions
- The **context engine** is the implementation of memory logic; the **MCP server** is a protocol/API layer for remote access.
- Use the context engine for direct, internal memory operations; use the MCP server for standardized, remote, or cross-container access.
- Keep configuration, documentation, and code for each clearly separated to avoid confusion.

## Performance Considerations

### Redis Configuration

Redis is configured for optimal vector search performance:

- HNSW algorithm for efficient approximate nearest neighbor search
- Multi-threading for concurrent searches
- Memory-optimized configuration for vector storage

### Neo4j Configuration

Neo4j is configured for optimal graph operations:

- Vector index for efficient similarity search
- Memory configuration for graph operations
- Performance tuning for concurrent transactions

## Background Processing

The worker service handles resource-intensive tasks in the background:

- Code indexing
- Knowledge graph updates
- Vector synchronization between Redis and Neo4j
- Vector pruning for optimal resource usage

## Integration with AI Models

The context engine can be integrated with AI models that support the MCP standard:

- **LangChain**: Use the MCP tools with LangChain agents
- **LlamaIndex**: Use the MCP tools with LlamaIndex agents
- **Custom Agents**: Use the MCP tools with custom agents

## Future Enhancements

Potential future enhancements:

- **Distributed Deployment**: Scale across multiple nodes for larger codebases
- **Advanced Caching**: More sophisticated caching strategies
- **Model Fine-tuning**: Fine-tune embedding models for specific codebases
- **Semantic Understanding**: Deeper semantic understanding of code
- **Tool Catalog**: Dynamic selection of MCP tools based on context
