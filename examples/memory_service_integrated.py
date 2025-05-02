#!/usr/bin/env python3
"""
Memory Service Example using Integrated MCP Approaches

This example demonstrates how to create a memory service that integrates all three MCP approaches:
1. FastAPI with FastAPI-MCP for direct API-to-MCP conversion
2. FastAPI with open-webui-mcp for secure, proxied MCP access
3. FastMCP with FastAPI generation for MCP-first design
"""

import logging
import os
import json
import subprocess
import tempfile
import threading
import asyncio
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from fastapi_mcp import FastApiMCP
from fastmcp import FastMCP, Client
from fastmcp.client.transports import FastMCPTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define models
class Memory(BaseModel):
    """A memory item"""
    id: str = Field(..., description="Unique identifier")
    text: str = Field(..., description="Text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class MemoryCreate(BaseModel):
    """Request to create a memory"""
    text: str = Field(..., description="Text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class MemoryResponse(BaseModel):
    """Response containing a memory"""
    memory: Memory = Field(..., description="The memory item")

class MemoriesResponse(BaseModel):
    """Response containing multiple memories"""
    memories: List[Memory] = Field(..., description="List of memory items")

# Define service implementation
class MemoryService:
    """Implementation of the Memory Service."""
    
    def __init__(self):
        """Initialize the service."""
        # In-memory storage for this example
        self.memories_db = {}
    
    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a new memory
        
        Args:
            text: The text content of the memory
            metadata: Additional metadata for the memory
        
        Returns:
            The created memory with ID
        """
        # Generate a simple ID
        memory_id = f"mem_{len(self.memories_db) + 1}"
        
        # Create memory object
        memory_obj = Memory(
            id=memory_id,
            text=text,
            metadata=metadata or {}
        )
        
        # Store in database
        self.memories_db[memory_id] = memory_obj
        
        logger.info(f"Added memory with ID: {memory_id}")
        return {"memory": memory_obj}
    
    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a memory by ID
        
        Args:
            memory_id: The ID of the memory to retrieve
        
        Returns:
            The memory with the specified ID
        """
        if memory_id not in self.memories_db:
            raise ValueError(f"Memory {memory_id} not found")
        
        memory = self.memories_db[memory_id]
        return {"memory": memory}
    
    async def list_memories(self) -> Dict[str, List[Memory]]:
        """List all memories
        
        Returns:
            List of all memories
        """
        memories = list(self.memories_db.values())
        return {"memories": memories}
    
    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory by ID
        
        Args:
            memory_id: The ID of the memory to delete
        
        Returns:
            Success message
        """
        if memory_id not in self.memories_db:
            raise ValueError(f"Memory {memory_id} not found")
        
        del self.memories_db[memory_id]
        return {"status": "success", "message": f"Memory {memory_id} deleted"}
    
    async def memory_resource(self, memory_id: str) -> Memory:
        """Get a memory by ID as a resource
        
        Args:
            memory_id: The ID of the memory to retrieve
        
        Returns:
            The memory with the specified ID
        """
        if memory_id not in self.memories_db:
            raise ValueError(f"Memory {memory_id} not found")
        
        return self.memories_db[memory_id]

# Create service instance
service = MemoryService()

#
# APPROACH 1: FastAPI with FastAPI-MCP
#

# Create FastAPI app for direct API-to-MCP conversion
fastapi_app = FastAPI(
    title="Memory Service Direct API",
    description="A service for managing memory storage and retrieval (Direct API-to-MCP)",
    version="0.1.0",
    docs_url="/direct/docs",
    openapi_url="/direct/openapi.json"
)

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router for direct API
direct_router = APIRouter(prefix="/direct")

# Define direct API endpoints
@direct_router.post("/memories", response_model=MemoryResponse, tags=["direct", "memories"])
async def direct_add_memory(memory: MemoryCreate):
    """Add a new memory (Direct API)"""
    try:
        return await service.add_memory(memory.text, memory.metadata)
    except Exception as e:
        logger.error(f"Error in direct_add_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@direct_router.get("/memories/{memory_id}", response_model=MemoryResponse, tags=["direct", "memories"])
async def direct_get_memory(memory_id: str):
    """Get a memory by ID (Direct API)"""
    try:
        return await service.get_memory(memory_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in direct_get_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@direct_router.get("/memories", response_model=MemoriesResponse, tags=["direct", "memories"])
async def direct_list_memories():
    """List all memories (Direct API)"""
    try:
        return await service.list_memories()
    except Exception as e:
        logger.error(f"Error in direct_list_memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@direct_router.delete("/memories/{memory_id}", tags=["direct", "memories"])
async def direct_delete_memory(memory_id: str):
    """Delete a memory by ID (Direct API)"""
    try:
        return await service.delete_memory(memory_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in direct_delete_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include direct router in app
fastapi_app.include_router(direct_router)

# Create MCP server from FastAPI app
direct_mcp = FastApiMCP(fastapi_app)

# Mount MCP server to FastAPI app
direct_mcp.mount()

#
# APPROACH 2: FastMCP with FastAPI Generation
#

# Create FastMCP server
fastmcp_server = FastMCP("Memory Service Native MCP")

# Define MCP tools
@fastmcp_server.tool()
async def native_add_memory(text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add a new memory (Native MCP)
    
    Args:
        text: The text content of the memory
        metadata: Additional metadata for the memory
    
    Returns:
        The created memory with ID
    """
    return await service.add_memory(text, metadata)

@fastmcp_server.tool()
async def native_get_memory(memory_id: str) -> Dict[str, Any]:
    """Get a memory by ID (Native MCP)
    
    Args:
        memory_id: The ID of the memory to retrieve
    
    Returns:
        The memory with the specified ID
    """
    return await service.get_memory(memory_id)

@fastmcp_server.tool()
async def native_list_memories() -> Dict[str, List[Memory]]:
    """List all memories (Native MCP)
    
    Returns:
        List of all memories
    """
    return await service.list_memories()

@fastmcp_server.tool()
async def native_delete_memory(memory_id: str) -> Dict[str, Any]:
    """Delete a memory by ID (Native MCP)
    
    Args:
        memory_id: The ID of the memory to delete
    
    Returns:
        Success message
    """
    return await service.delete_memory(memory_id)

# Define MCP resources
@fastmcp_server.resource("native+memory://{memory_id}")
async def native_memory_resource(memory_id: str) -> Memory:
    """Get a memory by ID (Native MCP)
    
    Args:
        memory_id: The ID of the memory to retrieve
    
    Returns:
        The memory with the specified ID
    """
    return await service.memory_resource(memory_id)

# Generate FastAPI app from FastMCP
native_app = FastMCP.from_fastmcp(fastmcp_server)
native_app.title = "Memory Service Native MCP API"
native_app.description = "A service for managing memory storage and retrieval (Native MCP-to-API)"
native_app.version = "0.1.0"
native_app.docs_url = "/native/docs"
native_app.openapi_url = "/native/openapi.json"

# Create router for native API
for route in native_app.routes:
    if hasattr(route, "path") and isinstance(route.path, str):
        route.path = "/native" + route.path

#
# APPROACH 3: FastAPI with open-webui-mcp
#

# Create FastAPI app for proxied API
proxy_app = FastAPI(
    title="Memory Service Proxied API",
    description="A service for managing memory storage and retrieval (Proxied API-to-MCP)",
    version="0.1.0",
    docs_url="/proxy/docs",
    openapi_url="/proxy/openapi.json"
)

# Add CORS middleware
proxy_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router for proxied API
proxy_router = APIRouter(prefix="/proxy")

# Define proxied API endpoints
@proxy_router.post("/memories", response_model=MemoryResponse, tags=["proxy", "memories"])
async def proxy_add_memory(memory: MemoryCreate):
    """Add a new memory (Proxied API)"""
    try:
        return await service.add_memory(memory.text, memory.metadata)
    except Exception as e:
        logger.error(f"Error in proxy_add_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@proxy_router.get("/memories/{memory_id}", response_model=MemoryResponse, tags=["proxy", "memories"])
async def proxy_get_memory(memory_id: str):
    """Get a memory by ID (Proxied API)"""
    try:
        return await service.get_memory(memory_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in proxy_get_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@proxy_router.get("/memories", response_model=MemoriesResponse, tags=["proxy", "memories"])
async def proxy_list_memories():
    """List all memories (Proxied API)"""
    try:
        return await service.list_memories()
    except Exception as e:
        logger.error(f"Error in proxy_list_memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@proxy_router.delete("/memories/{memory_id}", tags=["proxy", "memories"])
async def proxy_delete_memory(memory_id: str):
    """Delete a memory by ID (Proxied API)"""
    try:
        return await service.delete_memory(memory_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in proxy_delete_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include proxy router in app
proxy_app.include_router(proxy_router)

# Create MCP server script for open-webui-mcp
def create_mcp_server_script():
    """Create a Python script for the MCP server."""
    script_content = """#!/usr/bin/env python3
import json
import sys
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="mcp_server.log"
)
logger = logging.getLogger(__name__)

# Define MCP server
server_info = {
    "name": "Memory Service Proxied MCP",
    "version": "0.1.0"
}

# Define tools
tools = [
    {
        "name": "proxied_add_memory",
        "description": "Add a new memory (Proxied MCP)",
        "parameters": {
            "text": {
                "type": "string",
                "description": "The text content of the memory"
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata for the memory"
            }
        }
    },
    {
        "name": "proxied_get_memory",
        "description": "Get a memory by ID (Proxied MCP)",
        "parameters": {
            "memory_id": {
                "type": "string",
                "description": "The ID of the memory to retrieve"
            }
        }
    },
    {
        "name": "proxied_list_memories",
        "description": "List all memories (Proxied MCP)",
        "parameters": {}
    },
    {
        "name": "proxied_delete_memory",
        "description": "Delete a memory by ID (Proxied MCP)",
        "parameters": {
            "memory_id": {
                "type": "string",
                "description": "The ID of the memory to delete"
            }
        }
    }
]

# Define resources
resources = []

# Define prompts
prompts = []

# Initialize server
print(json.dumps({"type": "server_info", "server_info": server_info}))
sys.stdout.flush()

# API base URL
API_BASE_URL = "http://localhost:8000/proxy"

# Main loop
while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break
            
        request = json.loads(line)
        request_type = request.get("type")
        request_id = request.get("request_id")
        
        if request_type == "list_tools":
            response = {
                "type": "list_tools_response",
                "request_id": request_id,
                "tools": tools
            }
            print(json.dumps(response))
            sys.stdout.flush()
            
        elif request_type == "list_resources":
            response = {
                "type": "list_resources_response",
                "request_id": request_id,
                "resources": resources
            }
            print(json.dumps(response))
            sys.stdout.flush()
            
        elif request_type == "list_prompts":
            response = {
                "type": "list_prompts_response",
                "request_id": request_id,
                "prompts": prompts
            }
            print(json.dumps(response))
            sys.stdout.flush()
            
        elif request_type == "call_tool":
            tool_name = request.get("name")
            parameters = request.get("parameters", {})
            
            # Process tool call
            logger.info(f"Tool call: {tool_name} with parameters {parameters}")
            
            # Map MCP tool names to API endpoints
            tool_to_endpoint = {
                "proxied_add_memory": f"{API_BASE_URL}/memories",
                "proxied_get_memory": f"{API_BASE_URL}/memories/{parameters.get('memory_id', '')}",
                "proxied_list_memories": f"{API_BASE_URL}/memories",
                "proxied_delete_memory": f"{API_BASE_URL}/memories/{parameters.get('memory_id', '')}"
            }
            
            # Map MCP tool names to HTTP methods
            tool_to_method = {
                "proxied_add_memory": "POST",
                "proxied_get_memory": "GET",
                "proxied_list_memories": "GET",
                "proxied_delete_memory": "DELETE"
            }
            
            endpoint = tool_to_endpoint.get(tool_name)
            method = tool_to_method.get(tool_name)
            
            if endpoint and method:
                # Replace path parameters in the endpoint URL
                for param_name, param_value in parameters.items():
                    if "{" + param_name + "}" in endpoint:
                        endpoint = endpoint.replace("{" + param_name + "}", str(param_value))
                
                # Make the API request
                if method == "GET":
                    # For GET requests, add query parameters
                    query_params = {k: v for k, v in parameters.items() if "{" + k + "}" not in endpoint}
                    api_response = requests.get(endpoint, params=query_params)
                elif method == "POST":
                    api_response = requests.post(endpoint, json=parameters)
                elif method == "PUT":
                    api_response = requests.put(endpoint, json=parameters)
                elif method == "DELETE":
                    api_response = requests.delete(endpoint)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Check if the request was successful
                if api_response.status_code >= 200 and api_response.status_code < 300:
                    result = api_response.json()
                    
                    response = {
                        "type": "call_tool_response",
                        "request_id": request_id,
                        "result": result
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
                else:
                    error_msg = f"API request failed with status code {api_response.status_code}: {api_response.text}"
                    logger.error(error_msg)
                    response = {
                        "type": "error",
                        "request_id": request_id,
                        "error": error_msg
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
            else:
                response = {
                    "type": "error",
                    "request_id": request_id,
                    "error": f"Unknown tool: {tool_name}"
                }
                print(json.dumps(response))
                sys.stdout.flush()
                
        elif request_type == "ping":
            response = {
                "type": "pong",
                "request_id": request_id
            }
            print(json.dumps(response))
            sys.stdout.flush()
            
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        response = {
            "type": "error",
            "request_id": request_id if 'request_id' in locals() else None,
            "error": str(e)
        }
        print(json.dumps(response))
        sys.stdout.flush()
"""
    
    # Create a temporary file for the script
    fd, path = tempfile.mkstemp(suffix='.py')
    with os.fdopen(fd, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(path, 0o755)
    
    return path

# Create MCP config file
def create_mcp_config(script_path):
    """Create a config file for open-webui-mcp."""
    config = {
        "mcpServers": {
            "memory_service_proxied": {
                "command": "python",
                "args": [script_path]
            }
        }
    }
    
    # Create a temporary file for the config
    fd, path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w') as f:
        json.dump(config, f, indent=2)
    
    return path

#
# INTEGRATED APP
#

# Create the main FastAPI app that combines all approaches
app = FastAPI(
    title="Memory Service Integrated API",
    description="A service for managing memory storage and retrieval (Integrated API with all MCP approaches)",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router for the root API
root_router = APIRouter()

@root_router.get("/", tags=["root"])
async def root():
    """Root endpoint for the integrated API."""
    return {
        "name": "Memory Service Integrated API",
        "description": "A service for managing memory storage and retrieval (Integrated API with all MCP approaches)",
        "version": "0.1.0",
        "approaches": [
            {
                "name": "Direct API-to-MCP",
                "description": "FastAPI with FastAPI-MCP for direct API-to-MCP conversion",
                "api_prefix": "/direct",
                "docs_url": "/direct/docs",
                "mcp_port": 8001
            },
            {
                "name": "Native MCP-to-API",
                "description": "FastMCP with FastAPI generation for MCP-first design",
                "api_prefix": "/native",
                "docs_url": "/native/docs",
                "mcp_port": 8002
            },
            {
                "name": "Proxied API-to-MCP",
                "description": "FastAPI with open-webui-mcp for secure, proxied MCP access",
                "api_prefix": "/proxy",
                "docs_url": "/proxy/docs",
                "mcp_port": 8003
            }
        ]
    }

# Include the root router
app.include_router(root_router)

# Mount the direct API app
@app.middleware("http")
async def route_direct_requests(request: Request, call_next):
    """Route requests to the direct API app."""
    if request.url.path.startswith("/direct"):
        # Forward the request to the direct API app
        scope = request.scope.copy()
        scope["path"] = scope["path"][len("/direct"):]
        if scope["path"] == "":
            scope["path"] = "/"
        scope["raw_path"] = scope["path"].encode()
        
        response = await fastapi_app(scope, request._receive, request._send)
        return response
    
    # Continue with the normal request handling
    return await call_next(request)

# Mount the native API app
@app.middleware("http")
async def route_native_requests(request: Request, call_next):
    """Route requests to the native API app."""
    if request.url.path.startswith("/native"):
        # Forward the request to the native API app
        scope = request.scope.copy()
        scope["path"] = scope["path"][len("/native"):]
        if scope["path"] == "":
            scope["path"] = "/"
        scope["raw_path"] = scope["path"].encode()
        
        response = await native_app(scope, request._receive, request._send)
        return response
    
    # Continue with the normal request handling
    return await call_next(request)

# Mount the proxy API app
@app.middleware("http")
async def route_proxy_requests(request: Request, call_next):
    """Route requests to the proxy API app."""
    if request.url.path.startswith("/proxy"):
        # Forward the request to the proxy API app
        scope = request.scope.copy()
        scope["path"] = scope["path"][len("/proxy"):]
        if scope["path"] == "":
            scope["path"] = "/"
        scope["raw_path"] = scope["path"].encode()
        
        response = await proxy_app(scope, request._receive, request._send)
        return response
    
    # Continue with the normal request handling
    return await call_next(request)

# Start MCP servers
def start_direct_mcp_server():
    """Start the direct MCP server."""
    asyncio.run(direct_mcp.run_async(transport="sse", port=8001))

def start_native_mcp_server():
    """Start the native MCP server."""
    asyncio.run(fastmcp_server.run_async(transport="sse", port=8002))

def start_proxy_mcp_server(api_key: str = "top-secret", port: int = 8003):
    """Start the proxy MCP server using open-webui-mcp."""
    script_path = create_mcp_server_script()
    config_path = create_mcp_config(script_path)
    
    # Start the MCP server
    cmd = [
        "mcpo",
        "--port", str(port),
        "--api-key", api_key,
        "--config", config_path
    ]
    
    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    logger.info(f"Started proxy MCP server on port {port}")
    return process, script_path, config_path

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the integrated server.
    
    Args:
        host: Host to bind to
        port: Port to bind to for the main API
    """
    # Start direct MCP server in a separate thread
    direct_thread = threading.Thread(target=start_direct_mcp_server)
    direct_thread.daemon = True
    direct_thread.start()
    
    # Start native MCP server in a separate thread
    native_thread = threading.Thread(target=start_native_mcp_server)
    native_thread.daemon = True
    native_thread.start()
    
    # Start proxy MCP server in a separate process
    proxy_process, script_path, config_path = start_proxy_mcp_server(port=8003)
    
    try:
        # Start the main FastAPI server
        uvicorn.run(app, host=host, port=port)
    finally:
        # Clean up proxy MCP server process
        proxy_process.terminate()
        proxy_process.wait()
        
        # Clean up temporary files
        try:
            os.remove(script_path)
            os.remove(config_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")

if __name__ == "__main__":
    start_server()
