"""Vector store tool for the context engine."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from context_engine.db.redis_client import redis_client
from context_engine.db.neo4j_client import neo4j_client
from context_engine.db.embedding import embedding_model

class VectorStoreRequest(BaseModel):
    """Vector store request model."""
    
    text: str = Field(..., description="The text to encode and store")
    metadata: Dict[str, Any] = Field(..., description="Metadata for the vector")
    tier: str = Field("hot", description="Storage tier (hot, warm, or cold)")
    vector_id: Optional[str] = Field(None, description="Custom vector ID (generated if not provided)")

class VectorStoreResponse(BaseModel):
    """Vector store response model."""
    
    vector_id: str = Field(..., description="ID of the stored vector")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Message about the operation")

async def vector_store(request: VectorStoreRequest) -> VectorStoreResponse:
    """Store a vector in the database.
    
    Args:
        request: Vector store request
        
    Returns:
        Vector store response
    """
    import uuid
    
    # Generate a vector ID if not provided
    vector_id = request.vector_id or str(uuid.uuid4())
    
    # Generate embedding for the text
    embedding = embedding_model.encode(request.text)
    
    # Add timestamp to metadata
    import time
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
