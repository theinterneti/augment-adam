# Memory Service MCP Integration

This document provides guidance on integrating the Memory Service with the Model Context Protocol (MCP) to enable AI agents to access memory functionality.

## Overview

The Memory Service provides functionality for storing, retrieving, and managing memories. By integrating with MCP, we can expose this functionality to AI agents in a standardized way, allowing them to:

1. Store new memories
2. Retrieve memories by ID or query
3. Update existing memories
4. Delete memories

## Integration Options

We have implemented three different approaches for integrating the Memory Service with MCP:

1. **FastAPI with FastAPI-MCP**: Using FastAPI for the REST API and FastAPI-MCP to expose the same endpoints as MCP tools
2. **FastAPI with open-webui-mcp**: Using FastAPI for the REST API and open-webui-mcp as a proxy to expose MCP tools
3. **FastMCP with FastAPI Generation**: Using FastMCP to define MCP tools and resources, then generating a FastAPI application

For a detailed comparison of these approaches, see [MCP Integration Options](mcp_integration_options.md).

## Example Implementations

We provide example implementations for all three approaches:

### FastAPI with FastAPI-MCP

This approach uses FastAPI for the REST API and FastAPI-MCP to expose the same endpoints as MCP tools.

```python
# examples/memory_service_fastapi_mcp.py
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI(title="Memory Service")

@app.post("/memories")
async def add_memory(text: str, metadata: dict = None):
    # Implementation
    return {"memory": {"id": "mem_123", "text": text, "metadata": metadata}}

# Create MCP server from FastAPI app
mcp = FastApiMCP(app)
mcp.mount()
```

To run this example:

```bash
pip install fastapi uvicorn fastapi-mcp
python examples/memory_service_fastapi_mcp.py
```

### FastAPI with open-webui-mcp

This approach uses FastAPI for the REST API and open-webui-mcp as a proxy to expose MCP tools.

```python
# examples/memory_service_openwebui_mcp.py
from fastapi import FastAPI
import subprocess

app = FastAPI(title="Memory Service")

@app.post("/memories")
async def add_memory(text: str, metadata: dict = None):
    # Implementation
    return {"memory": {"id": "mem_123", "text": text, "metadata": metadata}}

# Create and start MCP server using open-webui-mcp
def start_mcp_server():
    # Create MCP script that calls the API
    script_path = create_mcp_server_script()
    config_path = create_mcp_config(script_path)
    
    # Start open-webui-mcp
    process = subprocess.Popen([
        "mcpo",
        "--port", "8001",
        "--api-key", "top-secret",
        "--config", config_path
    ])
    
    return process
```

To run this example:

```bash
pip install fastapi uvicorn mcpo
python examples/memory_service_openwebui_mcp.py
```

### FastMCP with FastAPI Generation

This approach uses FastMCP to define MCP tools and resources, then generates a FastAPI application.

```python
# examples/memory_service_fastmcp.py
from fastmcp import FastMCP
from fastapi import FastAPI
import threading
import asyncio

# Create FastMCP server
mcp = FastMCP("Memory Service")

# Define service implementation
class MemoryService:
    async def add_memory(self, text: str, metadata: dict = None):
        # Implementation
        return {"memory": {"id": "mem_123", "text": text, "metadata": metadata}}

service = MemoryService()

# Define MCP tool
@mcp.tool()
async def add_memory(text: str, metadata: dict = None):
    """Add a new memory."""
    return await service.add_memory(text, metadata)

# Generate FastAPI app from FastMCP
app = FastMCP.from_fastmcp(mcp)

# Start both servers
def start_server():
    # Start MCP server in a thread
    threading.Thread(
        target=lambda: asyncio.run(mcp.run_async(port=8001))
    ).start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

To run this example:

```bash
pip install fastapi uvicorn fastmcp
python examples/memory_service_fastmcp.py
```

## Using the Templates

We provide templates for all three approaches that you can use to generate code for your own services:

1. `templates/code/python/fastapi_mcp_service.py.j2` - FastAPI with FastAPI-MCP
2. `templates/code/python/openwebui_mcp_service.py.j2` - FastAPI with open-webui-mcp
3. `templates/code/python/fastmcp_service.py.j2` - FastMCP with FastAPI generation

You can generate code from these templates using our template engine:

```python
from augment_adam.utils.templates import render_code_template

# Define your service
service_definition = {
    "service_name": "Memory Service",
    "service_description": "A service for managing memory storage and retrieval",
    "endpoints": [
        {
            "name": "add_memory",
            "path": "/memories",
            "method": "POST",
            "description": "Add a new memory",
            "parameters": [
                {"name": "text", "type": "str", "description": "The text content of the memory"},
                {"name": "metadata", "type": "dict", "description": "Additional metadata for the memory"}
            ],
            "returns": {"type": "dict", "description": "The created memory with ID"}
        }
    ],
    "models": [
        {
            "name": "Memory",
            "description": "A memory item",
            "fields": [
                {"name": "id", "type": "str", "required": True, "description": "Unique identifier"},
                {"name": "text", "type": "str", "required": True, "description": "Text content"},
                {"name": "metadata", "type": "dict", "required": False, "description": "Additional metadata"}
            ]
        }
    ],
    "version": "0.1.0"
}

# Generate code using your preferred approach
code = render_code_template("fastapi_mcp_service.py.j2", service_definition)
```

## Recommendation

For the Memory Service, we recommend using the **FastMCP with FastAPI Generation** approach because:

1. It provides a clean, Pythonic interface for defining tools and resources
2. It allows for shared implementation between MCP and API
3. It gives full control over both MCP and API behavior
4. It's well-suited for new services where MCP is a primary concern

However, any of the three approaches would work well depending on your specific requirements and constraints.

## Next Steps

1. Choose the integration approach that best fits your needs
2. Implement the Memory Service using the provided templates and examples
3. Test the integration with AI agents
4. Deploy the service to your environment

For more information on MCP, see the [Model Context Protocol documentation](https://modelcontextprotocol.io).
