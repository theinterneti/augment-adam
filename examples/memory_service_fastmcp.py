#!/usr/bin/env python3
"""
Memory Service Example using FastMCP and FastAPI

This example demonstrates how to create a memory service that exposes
functionality as both MCP tools and REST API endpoints using FastMCP and FastAPI.
"""

import logging
import asyncio
import threading
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from fastmcp import FastMCP, Client
from fastmcp.client.transports import FastMCPTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Memory Service")

# Create FastAPI app
app = FastAPI(
    title="Memory Service API",
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
        memory_obj = {
            "id": memory_id,
            "text": text,
            "metadata": metadata or {}
        }

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

    async def list_memories(self) -> Dict[str, List[Dict[str, Any]]]:
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

# Create service instance
service = MemoryService()

# Define MCP tools
@mcp.tool()
async def add_memory(text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add a new memory

    Args:
        text: The text content of the memory
        metadata: Additional metadata for the memory

    Returns:
        The created memory with ID
    """
    return await service.add_memory(text, metadata)

@mcp.tool()
async def get_memory(memory_id: str) -> Dict[str, Any]:
    """Get a memory by ID

    Args:
        memory_id: The ID of the memory to retrieve

    Returns:
        The memory with the specified ID
    """
    return await service.get_memory(memory_id)

@mcp.tool()
async def list_memories() -> Dict[str, List[Dict[str, Any]]]:
    """List all memories

    Returns:
        List of all memories
    """
    return await service.list_memories()

@mcp.tool()
async def delete_memory(memory_id: str) -> Dict[str, Any]:
    """Delete a memory by ID

    Args:
        memory_id: The ID of the memory to delete

    Returns:
        Success message
    """
    return await service.delete_memory(memory_id)

# Define MCP resources
@mcp.resource("memory://{memory_id}")
async def memory_resource(memory_id: str) -> Dict[str, Any]:
    """Get a memory by ID

    Args:
        memory_id: The ID of the memory to retrieve

    Returns:
        The memory with the specified ID
    """
    result = await service.get_memory(memory_id)
    return result["memory"]

# Define API endpoints
@router.post("/memories", response_model=MemoryResponse, tags=["memories"])
async def api_add_memory(memory: MemoryCreate):
    """Add a new memory"""
    try:
        result = await service.add_memory(memory.text, memory.metadata)
        return result
    except Exception as e:
        logger.error(f"Error in add_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memories/{memory_id}", response_model=MemoryResponse, tags=["memories"])
async def api_get_memory(memory_id: str):
    """Get a memory by ID"""
    try:
        result = await service.get_memory(memory_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memories", response_model=MemoriesResponse, tags=["memories"])
async def api_list_memories():
    """List all memories"""
    try:
        result = await service.list_memories()
        return result
    except Exception as e:
        logger.error(f"Error in list_memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/memories/{memory_id}", tags=["memories"])
async def api_delete_memory(memory_id: str):
    """Delete a memory by ID"""
    try:
        result = await service.delete_memory(memory_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router in app
app.include_router(router)

# Generate FastAPI app from FastMCP
# Note: FastMCP.from_fastapi expects a FastAPI app, not a FastMCP instance
# Let's skip this step since we already have a FastAPI app

# We're not merging apps since we're not generating a FastAPI app from FastMCP

# Start both servers
def start_mcp_server():
    """Start the MCP server."""
    asyncio.run(mcp.run_async(transport="sse", port=8001))

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the server.

    Args:
        host: Host to bind to
        port: Port to bind to for the REST API
    """
    # Start MCP server in a separate thread
    mcp_thread = threading.Thread(target=start_mcp_server)
    mcp_thread.daemon = True
    mcp_thread.start()

    # Start FastAPI server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
