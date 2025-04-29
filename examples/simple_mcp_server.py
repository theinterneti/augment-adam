#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

# Create a FastAPI app
app = FastAPI(title="Simple MCP Server", description="A simple MCP server")

# Create a router
router = APIRouter()

# Define a simple model
class EchoRequest(BaseModel):
    message: str = Field(..., description="Message to echo")

class EchoResponse(BaseModel):
    message: str = Field(..., description="Echoed message")

# Create a simple endpoint
@router.post("/echo", response_model=EchoResponse, tags=["Echo"])
async def echo(request: EchoRequest):
    """Echo the message back."""
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

# Mount the MCP server
mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
