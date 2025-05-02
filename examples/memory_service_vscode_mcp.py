#!/usr/bin/env python3
"""
Memory Service VS Code MCP Demo

This script demonstrates how to use the Memory Service with VS Code MCP.
It starts the Memory Service with FastAPI-MCP and provides instructions for connecting VS Code to it.
"""

import os
import sys
import logging
import argparse
import subprocess
import webbrowser
import time
import threading
import asyncio
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

def print_instructions(host: str, port: int):
    """Print instructions for connecting VS Code to the MCP server."""
    print("\n" + "=" * 80)
    print("Memory Service VS Code MCP Demo")
    print("=" * 80)
    print(f"\nMemory Service running at http://{host}:{port}")
    print(f"MCP server running at http://{host}:{port}/mcp")
    print(f"API documentation available at http://{host}:{port}/docs")
    print("\nTo connect VS Code to the MCP server:")
    print("1. Open VS Code")
    print("2. Open the Command Palette (Ctrl+Shift+P)")
    print("3. Type 'MCP: Connect to Server'")
    print(f"4. Enter the URL: http://{host}:{port}/mcp")
    print("\nIf you're running VS Code in a different environment (e.g., Docker, WSL),")
    print("you may need to use socat to create a bridge:")
    print(f"\n    docker run -i --rm alpine/socat STDIO TCP:host.docker.internal:{port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80 + "\n")

def open_vscode_docs():
    """Open the VS Code MCP documentation in a browser."""
    url = "https://code.visualstudio.com/docs/copilot/chat/mcp-servers"
    print(f"Opening VS Code MCP documentation: {url}")
    webbrowser.open(url)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Memory Service VS Code MCP Demo")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8811, help="Port to bind to")
    parser.add_argument("--docs", action="store_true", help="Open VS Code MCP documentation")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Open VS Code MCP documentation if requested
    if args.docs:
        open_vscode_docs()
    
    # Print instructions
    print_instructions(args.host, args.port)
    
    # Start the server
    try:
        uvicorn.run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    main()
