#!/usr/bin/env python3
"""
Memory Service Example using FastAPI and open-webui-mcp

This example demonstrates how to create a memory service that exposes
functionality as both REST API endpoints and MCP tools using FastAPI and open-webui-mcp.
"""

import logging
import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Memory Service",
    description="A service for managing memory storage and retrieval",
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

# Create router
router = APIRouter()

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

# In-memory storage for this example
memories_db = {}

# Define endpoints
@router.post("/memories", response_model=MemoryResponse, tags=["memories"])
async def add_memory(memory: MemoryCreate):
    """Add a new memory
    
    Args:
        memory: The memory to add
    
    Returns:
        The created memory with ID
    """
    try:
        # Generate a simple ID
        memory_id = f"mem_{len(memories_db) + 1}"
        
        # Create memory object
        memory_obj = Memory(
            id=memory_id,
            text=memory.text,
            metadata=memory.metadata
        )
        
        # Store in database
        memories_db[memory_id] = memory_obj
        
        logger.info(f"Added memory with ID: {memory_id}")
        return {"memory": memory_obj}
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memories/{memory_id}", response_model=MemoryResponse, tags=["memories"])
async def get_memory(memory_id: str):
    """Get a memory by ID
    
    Args:
        memory_id: ID of the memory to retrieve
    
    Returns:
        The memory with the specified ID
    """
    try:
        if memory_id not in memories_db:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        
        memory = memories_db[memory_id]
        return {"memory": memory}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memories", response_model=MemoriesResponse, tags=["memories"])
async def list_memories():
    """List all memories
    
    Returns:
        List of all memories
    """
    try:
        memories = list(memories_db.values())
        return {"memories": memories}
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/memories/{memory_id}", tags=["memories"])
async def delete_memory(memory_id: str):
    """Delete a memory by ID
    
    Args:
        memory_id: ID of the memory to delete
    
    Returns:
        Success message
    """
    try:
        if memory_id not in memories_db:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        
        del memories_db[memory_id]
        return {"status": "success", "message": f"Memory {memory_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router in app
app.include_router(router)

# Create MCP server script
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
    "name": "Memory Service MCP",
    "version": "0.1.0"
}

# Define tools
tools = [
    {
        "name": "add_memory",
        "description": "Add a new memory",
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
        "name": "get_memory",
        "description": "Get a memory by ID",
        "parameters": {
            "memory_id": {
                "type": "string",
                "description": "The ID of the memory to retrieve"
            }
        }
    },
    {
        "name": "list_memories",
        "description": "List all memories",
        "parameters": {}
    },
    {
        "name": "delete_memory",
        "description": "Delete a memory by ID",
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
API_BASE_URL = "http://localhost:8000"

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
                "add_memory": f"{API_BASE_URL}/memories",
                "get_memory": f"{API_BASE_URL}/memories/{parameters.get('memory_id', '')}",
                "list_memories": f"{API_BASE_URL}/memories",
                "delete_memory": f"{API_BASE_URL}/memories/{parameters.get('memory_id', '')}"
            }
            
            # Map MCP tool names to HTTP methods
            tool_to_method = {
                "add_memory": "POST",
                "get_memory": "GET",
                "list_memories": "GET",
                "delete_memory": "DELETE"
            }
            
            endpoint = tool_to_endpoint.get(tool_name)
            method = tool_to_method.get(tool_name)
            
            if endpoint and method:
                # Make the API request
                if method == "GET":
                    api_response = requests.get(endpoint)
                elif method == "POST":
                    api_response = requests.post(endpoint, json=parameters)
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
            "memory_service": {
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

# Start MCP server
def start_mcp_server(api_key: str = "top-secret", port: int = 8001):
    """Start the MCP server using open-webui-mcp.
    
    Args:
        api_key: API key for the MCP server
        port: Port for the MCP server
    """
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
    
    logger.info(f"Started MCP server on port {port}")
    return process, script_path, config_path

def start_server(host: str = "0.0.0.0", port: int = 8000, mcp_port: int = 8001, api_key: str = "top-secret"):
    """Start the server.
    
    Args:
        host: Host to bind to
        port: Port to bind to for the REST API
        mcp_port: Port to bind to for the MCP server
        api_key: API key for the MCP server
    """
    # Start MCP server in a separate process
    mcp_process, script_path, config_path = start_mcp_server(api_key=api_key, port=mcp_port)
    
    try:
        # Start FastAPI server
        uvicorn.run(app, host=host, port=port)
    finally:
        # Clean up MCP server process
        mcp_process.terminate()
        mcp_process.wait()
        
        # Clean up temporary files
        try:
            os.remove(script_path)
            os.remove(config_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")

if __name__ == "__main__":
    start_server()
