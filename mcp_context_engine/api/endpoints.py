"""API endpoints for the MCP-enabled context engine."""

import time
import uuid
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException

from mcp_context_engine.api.models import (
    VectorSearchRequest, VectorSearchResponse, VectorSearchResult,
    VectorStoreRequest, VectorStoreResponse,
    CodeIndexRequest, CodeIndexResponse,
    RelationshipRequest, RelationshipResponse,
    RelatedVectorsRequest, RelatedVectorsResponse, RelatedVector
)
from mcp_context_engine.db.redis_client import redis_client
from mcp_context_engine.db.neo4j_client import neo4j_client
from mcp_context_engine.db.embedding import embedding_model

# Create router
router = APIRouter()

# Vector Search Endpoint
@router.post("/vector/search", response_model=VectorSearchResponse, tags=["Vector"])
async def search_vectors(request: VectorSearchRequest):
    """Search for vectors similar to the query."""
    # Start timer
    start_time = time.time()
    
    # Generate embedding for the query
    query_embedding = embedding_model.encode(request.query)
    
    # Perform the search
    if request.use_graph:
        # Use Neo4j for graph search
        results = await neo4j_client.search_vectors(
            query_vector=query_embedding,
            k=request.k,
            filter_dict=request.filter
        )
    else:
        # Use Redis for vector search
        results = await redis_client.search_vectors(
            query_vector=query_embedding,
            k=request.k,
            filter_dict=request.filter
        )
    
    # Calculate query time
    query_time_ms = (time.time() - start_time) * 1000
    
    # Format the results
    search_results = [
        VectorSearchResult(
            id=result["id"],
            score=result["score"],
            metadata=result["metadata"] if request.include_metadata else None
        )
        for result in results
    ]
    
    # Return the response
    return VectorSearchResponse(
        results=search_results,
        total=len(search_results),
        query_time_ms=query_time_ms
    )

# Vector Store Endpoint
@router.post("/vector/store", response_model=VectorStoreResponse, tags=["Vector"])
async def store_vector(request: VectorStoreRequest):
    """Store a vector in the database."""
    # Generate a vector ID if not provided
    vector_id = request.vector_id or str(uuid.uuid4())
    
    # Generate embedding for the text
    embedding = embedding_model.encode(request.text)
    
    # Add timestamp to metadata
    metadata = request.metadata.copy()
    metadata["created_at"] = int(time.time())
    
    # Store in the appropriate tier
    if request.tier == "hot":
        # Store in Redis with no expiration
        success = await redis_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata,
            ttl=None
        )
    elif request.tier == "warm":
        # Store in Redis with 24-hour expiration
        success = await redis_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata,
            ttl=86400  # 24 hours
        )
    elif request.tier == "cold":
        # Store in Neo4j
        success = await neo4j_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata
        )
    else:
        return VectorStoreResponse(
            vector_id=vector_id,
            status="error",
            message=f"Invalid tier: {request.tier}"
        )
    
    # Return the response
    if success:
        return VectorStoreResponse(
            vector_id=vector_id,
            status="success",
            message=f"Vector stored in {request.tier} tier"
        )
    else:
        return VectorStoreResponse(
            vector_id=vector_id,
            status="error",
            message=f"Failed to store vector in {request.tier} tier"
        )

# Code Index Endpoint
@router.post("/code/index", response_model=CodeIndexResponse, tags=["Code"])
async def index_code(request: CodeIndexRequest):
    """Index code in the database."""
    # Determine language from file extension if not provided
    language = request.language
    if not language:
        ext = os.path.splitext(request.file_path)[1].lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sql": "sql",
            ".graphql": "graphql",
            ".proto": "protobuf"
        }
        language = language_map.get(ext, "text")
    
    # Generate a vector ID based on the file path
    vector_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"file://{request.file_path}"))
    
    # Generate embedding for the code
    embedding = embedding_model.encode(request.code)
    
    # Create metadata
    metadata = {
        "file_path": request.file_path,
        "language": language,
        "created_at": int(time.time()),
        "size": len(request.code)
    }
    
    # Add additional metadata if provided
    if request.additional_metadata:
        metadata.update(request.additional_metadata)
    
    # Store in the appropriate tier
    if request.tier == "hot":
        # Store in Redis with no expiration
        success = await redis_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata,
            ttl=None
        )
    elif request.tier == "warm":
        # Store in Redis with 24-hour expiration
        success = await redis_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata,
            ttl=86400  # 24 hours
        )
    elif request.tier == "cold":
        # Store in Neo4j
        success = await neo4j_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata
        )
    else:
        return CodeIndexResponse(
            vector_id=vector_id,
            status="error",
            message=f"Invalid tier: {request.tier}"
        )
    
    # Return the response
    if success:
        return CodeIndexResponse(
            vector_id=vector_id,
            status="success",
            message=f"Code indexed in {request.tier} tier"
        )
    else:
        return CodeIndexResponse(
            vector_id=vector_id,
            status="error",
            message=f"Failed to index code in {request.tier} tier"
        )

# Create Relationship Endpoint
@router.post("/graph/relationship", response_model=RelationshipResponse, tags=["Graph"])
async def create_relationship(request: RelationshipRequest):
    """Create a relationship between two vectors."""
    # Create the relationship
    success = await neo4j_client.create_relationship(
        from_id=request.from_id,
        to_id=request.to_id,
        relationship_type=request.relationship_type,
        properties=request.properties
    )
    
    # Return the response
    if success:
        return RelationshipResponse(
            status="success",
            message=f"Relationship created: ({request.from_id})-[:{request.relationship_type}]->({request.to_id})"
        )
    else:
        return RelationshipResponse(
            status="error",
            message="Failed to create relationship"
        )

# Get Related Vectors Endpoint
@router.post("/graph/related", response_model=RelatedVectorsResponse, tags=["Graph"])
async def get_related_vectors(request: RelatedVectorsRequest):
    """Get vectors related to a vector."""
    # Get related vectors
    related_vectors = await neo4j_client.get_related_vectors(
        vector_id=request.vector_id,
        relationship_type=request.relationship_type,
        max_depth=request.max_depth
    )
    
    # Format the results
    vectors = [
        RelatedVector(
            id=vector["id"],
            metadata=vector["metadata"]
        )
        for vector in related_vectors
    ]
    
    # Return the response
    return RelatedVectorsResponse(
        vectors=vectors,
        total=len(vectors)
    )

# Health Check Endpoint
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
