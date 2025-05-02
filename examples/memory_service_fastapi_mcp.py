#!/usr/bin/env python3
"""
Memory Service Example using FastAPI and FastAPI-MCP

This example demonstrates how to create a memory service that exposes
functionality as both REST API endpoints and MCP tools using FastAPI and FastAPI-MCP.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from fastapi_mcp import FastApiMCP

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

# Create MCP server from FastAPI app
mcp = FastApiMCP(app)

# Mount MCP server to FastAPI app
mcp.mount()

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
