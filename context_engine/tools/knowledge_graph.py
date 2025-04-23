"""Knowledge graph tool for the context engine."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from context_engine.db.neo4j_client import neo4j_client

class RelationshipRequest(BaseModel):
    """Relationship request model."""
    
    from_id: str = Field(..., description="Source vector ID")
    to_id: str = Field(..., description="Target vector ID")
    relationship_type: str = Field(..., description="Type of relationship")
    properties: Optional[Dict[str, Any]] = Field(None, description="Relationship properties")

class RelationshipResponse(BaseModel):
    """Relationship response model."""
    
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Message about the operation")

class RelatedVectorsRequest(BaseModel):
    """Related vectors request model."""
    
    vector_id: str = Field(..., description="Vector ID")
    relationship_type: Optional[str] = Field(None, description="Type of relationship (None for any)")
    max_depth: int = Field(1, description="Maximum depth of relationships")

class RelatedVector(BaseModel):
    """Related vector model."""
    
    id: str = Field(..., description="ID of the vector")
    metadata: Dict[str, Any] = Field(..., description="Metadata of the vector")

class RelatedVectorsResponse(BaseModel):
    """Related vectors response model."""
    
    vectors: List[RelatedVector] = Field(..., description="Related vectors")
    total: int = Field(..., description="Total number of related vectors")

async def create_relationship(request: RelationshipRequest) -> RelationshipResponse:
    """Create a relationship between two vectors.
    
    Args:
        request: Relationship request
        
    Returns:
        Relationship response
    """
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

async def get_related_vectors(request: RelatedVectorsRequest) -> RelatedVectorsResponse:
    """Get vectors related to a vector.
    
    Args:
        request: Related vectors request
        
    Returns:
        Related vectors response
    """
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
