# MCP Integration Options

This document outlines different approaches for exposing services as both MCP tools and RESTful APIs.

## Overview

The Model Context Protocol (MCP) is a standardized way to provide context and tools to LLMs. When building services for Augment Adam, you may want to expose your functionality as both traditional RESTful APIs and MCP tools. This document presents different approaches to achieve this integration.

## Option 1: FastAPI with FastAPI-MCP

This approach uses FastAPI for the REST API and FastAPI-MCP to expose the same endpoints as MCP tools.

### Advantages

- Simple integration with minimal code
- Single codebase for both API and MCP
- Automatic conversion of FastAPI routes to MCP tools
- Leverages FastAPI's validation, documentation, and dependency injection

### Implementation

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# Create FastAPI app
app = FastAPI(title="Memory Service")

# Define your FastAPI endpoints
@app.post("/memories")
async def add_memory(text: str, metadata: dict = None):
    # Implementation
    return {"id": "mem_123", "text": text, "metadata": metadata}

# Create MCP server from FastAPI app
mcp = FastApiMCP(app)

# Mount MCP server to FastAPI app
mcp.mount()

# Start server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### When to Use

- When you already have a FastAPI application
- When you want a simple, low-maintenance solution
- When your API endpoints map cleanly to MCP tools

## Option 2: FastAPI with open-webui-mcp

This approach uses FastAPI for the REST API and open-webui-mcp as a proxy to expose MCP tools that call your API endpoints.

### Advantages

- Separation between API and MCP layers
- Can expose existing APIs as MCP without modifying them
- Adds security and authentication to MCP tools
- Provides OpenAPI documentation for MCP tools

### Implementation

```python
# 1. Create your FastAPI application
from fastapi import FastAPI
app = FastAPI(title="Memory Service")

@app.post("/memories")
async def add_memory(text: str, metadata: dict = None):
    # Implementation
    return {"id": "mem_123", "text": text, "metadata": metadata}

# 2. Create an MCP server script that calls your API
mcp_script = """
#!/usr/bin/env python3
import json
import sys
import requests

# Define tools
tools = [
    {
        "name": "add_memory",
        "description": "Add a new memory",
        "parameters": {
            "text": {"type": "string", "description": "Memory content"},
            "metadata": {"type": "object", "description": "Additional metadata"}
        }
    }
]

# Main loop
while True:
    line = sys.stdin.readline()
    if not line:
        break

    request = json.loads(line)
    if request["type"] == "call_tool" and request["name"] == "add_memory":
        # Call the API endpoint
        response = requests.post(
            "http://localhost:8000/memories",
            json=request["parameters"]
        )
        result = response.json()

        print(json.dumps({
            "type": "call_tool_response",
            "request_id": request["request_id"],
            "result": result
        }))
        sys.stdout.flush()
"""

# 3. Use open-webui-mcp to expose the script as an OpenAPI server
# mcpo --port 8001 --api-key "secret" -- python mcp_script.py
```

### When to Use

- When you have existing APIs you want to expose as MCP
- When you need additional security or authentication
- When you want to expose MCP tools to web clients

## Option 3: FastMCP with FastAPI Generation

This approach uses FastMCP to define MCP tools and resources, then generates a FastAPI application from them.

### Advantages

- MCP-first design
- Clean, Pythonic interface for defining tools and resources
- Shared implementation between MCP and API
- Full control over both MCP and API behavior

### Implementation

```python
from fastmcp import FastMCP
from fastapi import FastAPI

# Create FastMCP server
mcp = FastMCP("Memory Service")

# Define service implementation
class MemoryService:
    async def add_memory(self, text: str, metadata: dict = None):
        # Implementation
        return {"id": "mem_123", "text": text, "metadata": metadata}

service = MemoryService()

# Define MCP tool
@mcp.tool()
async def add_memory(text: str, metadata: dict = None):
    """Add a new memory."""
    return await service.add_memory(text, metadata)

# Generate FastAPI app from FastMCP
app = FastMCP.from_fastmcp(mcp)

# Start both servers
if __name__ == "__main__":
    import uvicorn
    import threading
    import asyncio

    # Start MCP server in a thread
    threading.Thread(
        target=lambda: asyncio.run(mcp.run_async(port=8001))
    ).start()

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### When to Use

- When designing new services from scratch
- When MCP is the primary interface
- When you need fine-grained control over both interfaces
- When you want to leverage FastMCP's advanced features

## Option 4: Integrated MCP Architecture

This approach combines all three previous approaches into a single integrated system, providing the benefits of each approach while mitigating their individual limitations.

### Advantages

- Flexibility to use different approaches for different scenarios
- Comprehensive solution that meets a wide range of requirements
- Ability to leverage the strengths of each approach
- Consistent implementation across all interfaces

### Implementation

```python
# Create a shared service implementation
class MemoryService:
    async def add_memory(self, text: str, metadata: dict = None):
        # Implementation
        return {"id": "mem_123", "text": text, "metadata": metadata}

service = MemoryService()

# 1. FastAPI with FastAPI-MCP
direct_app = FastAPI(title="Direct API")
@direct_app.post("/memories")
async def direct_add_memory(text: str, metadata: dict = None):
    return await service.add_memory(text, metadata)
direct_mcp = FastApiMCP(direct_app)
direct_mcp.mount()

# 2. FastMCP with FastAPI Generation
native_mcp = FastMCP("Native MCP")
@native_mcp.tool()
async def native_add_memory(text: str, metadata: dict = None):
    return await service.add_memory(text, metadata)
native_app = FastMCP.from_fastmcp(native_mcp)

# 3. FastAPI with open-webui-mcp
proxy_app = FastAPI(title="Proxy API")
@proxy_app.post("/memories")
async def proxy_add_memory(text: str, metadata: dict = None):
    return await service.add_memory(text, metadata)
# Create proxy MCP server script and config...

# 4. Integrated App
app = FastAPI(title="Integrated API")
# Mount all three apps with appropriate routing...
```

For a complete implementation, see the [Integrated MCP Architecture](integrated_mcp_architecture.md) document and the [example implementation](../examples/memory_service_integrated.py).

### When to Use

- When you need to support multiple client types with different requirements
- When you want to provide different security levels for different operations
- When you need both simplicity for some operations and advanced features for others
- When you're building a platform that needs to be flexible and future-proof

## Comparison

| Feature | FastAPI-MCP | open-webui-mcp | FastMCP | Integrated |
|---------|-------------|----------------|---------|------------|
| Complexity | Low | Medium | Medium | High |
| Separation of Concerns | Low | High | Medium | High |
| Control | Limited | Medium | High | High |
| Security | Basic | Enhanced | Basic | Configurable |
| Documentation | FastAPI Docs | OpenAPI Docs | FastAPI Docs | All Types |
| Deployment | Single Service | Multiple Services | Single Service | Multiple Services |
| Best For | Simple APIs | Existing APIs | New Services | Complex Systems |
| Flexibility | Low | Medium | Medium | High |
| Maintenance | Easy | Moderate | Moderate | Complex |

## Recommendation

- For simple services or existing FastAPI applications, use **FastAPI-MCP**
- For exposing existing APIs as MCP without modifying them, use **open-webui-mcp**
- For new services where MCP is a primary concern, use **FastMCP**
- For complex systems with diverse requirements, use the **Integrated MCP Architecture**

## Templates

We provide templates for all approaches:

- `templates/code/python/fastapi_mcp_service.py.j2` - FastAPI with FastAPI-MCP
- `templates/code/python/openwebui_mcp_service.py.j2` - FastAPI with open-webui-mcp
- `templates/code/python/fastmcp_service.py.j2` - FastMCP with FastAPI generation
- `templates/code/python/integrated_mcp_service.py.j2` - Integrated MCP Architecture

You can generate code from these templates using our template engine:

```python
from augment_adam.utils.templates import render_code_template

# Define your service
service_definition = {
    "service_name": "Memory Service",
    "service_description": "A service for managing memory storage and retrieval",
    "endpoints": [...],  # For FastAPI-MCP and open-webui-mcp
    "tools": [...],      # For FastMCP
    "resources": [...],  # For FastMCP
    "version": "0.1.0"
}

# Generate code using your preferred approach
code = render_code_template("fastapi_mcp_service.py.j2", service_definition)
# or
code = render_code_template("openwebui_mcp_service.py.j2", service_definition)
# or
code = render_code_template("fastmcp_service.py.j2", service_definition)
# or
code = render_code_template("integrated_mcp_service.py.j2", service_definition)
```
