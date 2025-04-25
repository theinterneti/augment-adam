# MCP-Enabled Context Engine

A high-performance context engine with Model Context Protocol (MCP) integration, built with Redis and Neo4j.

## Overview

This context engine uses a hybrid approach combining Redis for real-time vector search and Neo4j for graph relationships, providing a powerful system for code context retrieval and knowledge graph navigation. It exposes its capabilities through the Model Context Protocol (MCP), enabling AI models to interact with the context engine in a standardized way.

## Features

- **Real-time Vector Search**: Sub-millisecond vector similarity search using Redis
- **Graph-aware Context**: Relationship-based context retrieval using Neo4j
- **Tiered Memory**: Hot, warm, and cold tiers for optimal performance and resource usage
- **Asynchronous Processing**: Background tasks for resource-intensive operations
- **MCP Integration**: Standardized tool interface for AI models
- **Sophisticated Tagging System**: Hierarchical tagging for better organization and retrieval
- **Enhanced Template Engine**: Generate code, tests, and documentation with a powerful template engine
- **Google-Style Docstrings**: All code includes comprehensive Google-style docstrings
- **Type Hints**: Extensive use of type hints for better code quality and IDE support

## Architecture

The context engine consists of the following components:

1. **Redis Vector Database**: Optimized for high-performance vector similarity search
2. **Neo4j Graph Database**: Stores relationships and provides graph-aware context
3. **FastAPI MCP Server**: Exposes the context engine's capabilities as MCP tools
4. **Background Worker**: Handles resource-intensive tasks in the background
5. **Tagging System**: Hierarchical tagging for better organization and retrieval
6. **Template Engine**: Generate code, tests, and documentation with a powerful template engine

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+

### Installation

1. Clone the repository
2. Run the setup script:

```bash
chmod +x setup_mcp_context_engine.sh
./setup_mcp_context_engine.sh
```

### Testing

Run the test script to verify the installation:

```bash
python tests/test_mcp_context_engine.py
```

## API Endpoints

The context engine exposes the following API endpoints:

1. **Vector Search**: `/api/vector/search`
2. **Vector Store**: `/api/vector/store`
3. **Code Index**: `/api/code/index`
4. **Create Relationship**: `/api/graph/relationship`
5. **Get Related Vectors**: `/api/graph/related`

## MCP Tools

The context engine exposes the following MCP tools:

1. **vector_search**: Search for vectors similar to a query text
2. **vector_store**: Store a vector in the database
3. **code_index**: Index code in the database
4. **create_relationship**: Create a relationship between two vectors
5. **get_related_vectors**: Get vectors related to a vector

## Client Library

The context engine comes with a client library for easy integration:

```python
from mcp_context_engine.client.mcp_context_engine_client import MCPContextEngineClient

# Initialize the client
client = MCPContextEngineClient("http://localhost:8080", "test-api-key")

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
from mcp.client.session import ClientSession

async def main():
    # Connect to the MCP server
    async with ClientSession("http://localhost:8080/mcp") as session:
        # Initialize the session
        await session.initialize()

        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {tools}")

        # Call the vector_search tool
        result = await session.call_tool("vector_search", {
            "query": "function that prints hello world",
            "k": 10,
            "include_metadata": True
        })
        print(f"Search results: {result}")
```

## Documentation

For more detailed information, see the following documentation:

- [MCP Context Engine](MCP_CONTEXT_ENGINE.md): Detailed documentation of the context engine
- [Tagging System](TAGGING_SYSTEM.md): Documentation of the tagging system
- [Template Engine](TEMPLATE_ENGINE.md): Documentation of the template engine
- [Guidelines](.augment.guidelines.yaml): Guidelines for using and extending the context engine

## License

This project is licensed under the MIT License - see the LICENSE file for details.
