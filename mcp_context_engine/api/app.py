"""FastAPI application for the MCP-enabled context engine."""

import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi_mcp import FastApiMCP

from mcp_context_engine.api.endpoints import router
from mcp_context_engine.db.redis_client import redis_client
from mcp_context_engine.db.neo4j_client import neo4j_client

# API key security
API_KEY = os.getenv("API_KEY", "test-api-key")
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key."""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Create FastAPI app
app = FastAPI(
    title="MCP Context Engine",
    description="A high-performance context engine with MCP integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Include router with API key security
app.include_router(
    router,
    prefix="/api",
    dependencies=[Depends(get_api_key)]
)

# Create MCP server
mcp = FastApiMCP(app)

# Mount the MCP server
mcp.mount()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    # Create indexes
    await redis_client.create_index()
    await neo4j_client.create_index()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    await redis_client.close()
    await neo4j_client.close()

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "MCP Context Engine",
        "version": "0.1.0",
        "description": "A high-performance context engine with MCP integration",
        "endpoints": {
            "api": "/api",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "mcp": "/mcp"
        }
    }
