"""MCP server for the context engine."""

import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Depends
from fastapi_mcp import MCPRouter, MCPTool, MCPToolCall

from context_engine.tools.vector_search import vector_search, VectorSearchRequest, VectorSearchResponse
from context_engine.tools.vector_store import vector_store, VectorStoreRequest, VectorStoreResponse
from context_engine.tools.code_index import code_index, CodeIndexRequest, CodeIndexResponse
from context_engine.tools.knowledge_graph import (
    create_relationship, RelationshipRequest, RelationshipResponse,
    get_related_vectors, RelatedVectorsRequest, RelatedVectorsResponse
)
from context_engine.db.redis_client import redis_client
from context_engine.db.neo4j_client import neo4j_client

# Create FastAPI app
app = FastAPI(
    title="Context Engine MCP Server",
    description="MCP server for the context engine",
    version="0.1.0"
)

# Create MCP router
mcp_router = MCPRouter()
app.include_router(mcp_router.router)

# Register MCP tools
@mcp_router.tool("vector_search")
async def vector_search_tool(call: MCPToolCall[VectorSearchRequest]) -> VectorSearchResponse:
    """Search for vectors similar to the query.
    
    This tool allows you to search for vectors similar to a query text.
    You can specify the number of results, whether to include metadata,
    and filters to apply to the results.
    
    Args:
        query: The query text to search for
        k: Number of results to return (default: 10)
        include_metadata: Whether to include metadata in the results (default: True)
        filter: Filter to apply to the results (default: None)
        use_graph: Whether to use graph search (Neo4j) instead of vector search (Redis) (default: False)
        
    Returns:
        Search results with similarity scores and metadata
    """
    return await vector_search(call.parameters)

@mcp_router.tool("vector_store")
async def vector_store_tool(call: MCPToolCall[VectorStoreRequest]) -> VectorStoreResponse:
    """Store a vector in the database.
    
    This tool allows you to store a vector in the database.
    You can specify the text to encode, metadata, and the storage tier.
    
    Args:
        text: The text to encode and store
        metadata: Metadata for the vector
        tier: Storage tier (hot, warm, or cold) (default: hot)
        vector_id: Custom vector ID (generated if not provided)
        
    Returns:
        Status of the operation
    """
    return await vector_store(call.parameters)

@mcp_router.tool("code_index")
async def code_index_tool(call: MCPToolCall[CodeIndexRequest]) -> CodeIndexResponse:
    """Index code in the database.
    
    This tool allows you to index code in the database.
    You can specify the code, file path, language, and storage tier.
    
    Args:
        code: The code to index
        file_path: Path to the file
        language: Programming language (detected from file extension if not provided)
        tier: Storage tier (hot, warm, or cold) (default: hot)
        additional_metadata: Additional metadata
        
    Returns:
        Status of the operation
    """
    return await code_index(call.parameters)

@mcp_router.tool("create_relationship")
async def create_relationship_tool(call: MCPToolCall[RelationshipRequest]) -> RelationshipResponse:
    """Create a relationship between two vectors.
    
    This tool allows you to create a relationship between two vectors.
    You can specify the source and target vector IDs, relationship type, and properties.
    
    Args:
        from_id: Source vector ID
        to_id: Target vector ID
        relationship_type: Type of relationship
        properties: Relationship properties
        
    Returns:
        Status of the operation
    """
    return await create_relationship(call.parameters)

@mcp_router.tool("get_related_vectors")
async def get_related_vectors_tool(call: MCPToolCall[RelatedVectorsRequest]) -> RelatedVectorsResponse:
    """Get vectors related to a vector.
    
    This tool allows you to get vectors related to a vector.
    You can specify the vector ID, relationship type, and maximum depth.
    
    Args:
        vector_id: Vector ID
        relationship_type: Type of relationship (None for any)
        max_depth: Maximum depth of relationships (default: 1)
        
    Returns:
        Related vectors with metadata
    """
    return await get_related_vectors(call.parameters)

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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
