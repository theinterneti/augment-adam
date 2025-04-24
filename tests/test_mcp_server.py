#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI, APIRouter, Depends
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP
from typing import Dict, Any, List, Optional

app = FastAPI(title="Test MCP Server", description="Test MCP server")

# Create API router
router = APIRouter()

# Define a simple model
class EchoRequest(BaseModel):
    message: str = Field(..., description="Message to echo")

class EchoResponse(BaseModel):
    message: str = Field(..., description="Echoed message")

# Create a simple endpoint
@router.post("/echo", response_model=EchoResponse, tags=["Echo"])
async def echo(request: EchoRequest):
    """Echo the message back.

    Args:
        message: Message to echo

    Returns:
        Echoed message
    """
    return EchoResponse(message=request.message)

# Health check endpoint
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include the router
app.include_router(router)

# Create MCP server
mcp = FastApiMCP(app)

# Mount the MCP server to the FastAPI app
mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
