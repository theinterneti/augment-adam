# Memory Client for Augment Adam

This package provides client implementations for interacting with the memory service via both REST API and MCP (Model Context Protocol).

## Features

- Connect to both REST API and MCP endpoints
- Support for all memory operations (add, get, search, update, delete)
- Handles authentication and error cases
- Provides both synchronous and asynchronous interfaces
- Context manager support for easy resource management

## Installation

The memory client is included as part of the Augment Adam package. To use the MCP client, you'll need to install the MCP dependencies:

```bash
pip install mcp
```

## Usage

### Asynchronous API

```python
import asyncio
from augment_adam.memory.client import MemoryClient, ClientType

async def main():
    # Create a REST API client
    rest_client = MemoryClient.create(
        ClientType.REST, 
        "http://localhost:8000", 
        api_key="your_api_key"
    )
    
    # Create an MCP client
    mcp_client = MemoryClient.create(
        ClientType.MCP, 
        "http://localhost:8001"
    )
    
    # Connect to the memory service
    await rest_client.connect()
    
    # Add a memory
    result = await rest_client.add_memory(
        text="This is a memory",
        metadata={"source": "example", "importance": 0.9}
    )
    
    # Get the memory ID
    memory_id = result["memory"]["id"]
    
    # Get the memory
    memory = await rest_client.get_memory(memory_id)
    
    # Update the memory
    updated = await rest_client.update_memory(
        memory_id=memory_id,
        text="This is an updated memory",
        metadata={"source": "example", "importance": 1.0}
    )
    
    # Search memories
    results = await rest_client.search_memories("example")
    
    # Delete the memory
    await rest_client.delete_memory(memory_id)
    
    # Disconnect from the memory service
    await rest_client.disconnect()

asyncio.run(main())
```

### Using Context Managers

```python
import asyncio
from augment_adam.memory.client import MemoryClient, ClientType

async def main():
    # Using a context manager automatically handles connect/disconnect
    async with MemoryClient.create(ClientType.REST, "http://localhost:8000") as client:
        result = await client.add_memory(
            text="This is a memory",
            metadata={"source": "example", "importance": 0.9}
        )
        print(f"Added memory: {result}")

asyncio.run(main())
```

### Synchronous API

```python
from augment_adam.memory.client import SyncMemoryClient, ClientType

# Create a REST API client
client = SyncMemoryClient.create(
    ClientType.REST, 
    "http://localhost:8000", 
    api_key="your_api_key"
)

# Connect to the memory service
client.connect()

# Add a memory
result = client.add_memory(
    text="This is a memory",
    metadata={"source": "example", "importance": 0.9}
)

# Get the memory ID
memory_id = result["memory"]["id"]

# Get the memory
memory = client.get_memory(memory_id)

# Update the memory
updated = client.update_memory(
    memory_id=memory_id,
    text="This is an updated memory",
    metadata={"source": "example", "importance": 1.0}
)

# Search memories
results = client.search_memories("example")

# Delete the memory
client.delete_memory(memory_id)

# Disconnect from the memory service
client.disconnect()
```

### Using Synchronous Context Managers

```python
from augment_adam.memory.client import SyncMemoryClient, ClientType

# Using a context manager automatically handles connect/disconnect
with SyncMemoryClient.create(ClientType.REST, "http://localhost:8000") as client:
    result = client.add_memory(
        text="This is a memory",
        metadata={"source": "example", "importance": 0.9}
    )
    print(f"Added memory: {result}")
```

## API Reference

### MemoryClient

Base class for memory clients.

#### Methods

- `add_memory(text, metadata=None)` - Add a new memory
- `get_memory(memory_id)` - Get a memory by ID
- `list_memories(limit=100, offset=0)` - List all memories
- `search_memories(query, limit=10)` - Search memories by query
- `update_memory(memory_id, text=None, metadata=None)` - Update a memory
- `delete_memory(memory_id)` - Delete a memory
- `connect()` - Connect to the memory service
- `disconnect()` - Disconnect from the memory service

### MemoryRESTClient

Client for interacting with the memory service via REST API.

### MemoryMCPClient

Client for interacting with the memory service via MCP.

### SyncMemoryClient

Synchronous wrapper for the memory client.

## Examples

See the `examples` directory for complete examples:

- `memory_client_demo.py` - Asynchronous client demo
- `memory_client_sync_demo.py` - Synchronous client demo
