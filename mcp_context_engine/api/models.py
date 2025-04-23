"""API models for the MCP-enabled context engine."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Vector Search Models
class VectorSearchRequest(BaseModel):
    """Vector search request model."""
    
    query: str = Field(..., description="The query text to search for")
    k: int = Field(10, description="Number of results to return")
    include_metadata: bool = Field(True, description="Whether to include metadata in the results")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filter to apply to the results")
    use_graph: bool = Field(False, description="Whether to use graph search (Neo4j) instead of vector search (Redis)")

class VectorSearchResult(BaseModel):
    """Vector search result model."""
    
    id: str = Field(..., description="ID of the result")
    score: float = Field(..., description="Similarity score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata of the result")

class VectorSearchResponse(BaseModel):
    """Vector search response model."""
    
    results: List[VectorSearchResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    query_time_ms: float = Field(..., description="Query time in milliseconds")

# Vector Store Models
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

# Code Index Models
class CodeIndexRequest(BaseModel):
    """Code index request model."""
    
    code: str = Field(..., description="The code to index")
    file_path: str = Field(..., description="Path to the file")
    language: Optional[str] = Field(None, description="Programming language")
    tier: str = Field("hot", description="Storage tier (hot, warm, or cold)")
    additional_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class CodeIndexResponse(BaseModel):
    """Code index response model."""
    
    vector_id: str = Field(..., description="ID of the stored vector")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Message about the operation")

# Relationship Models
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

# Related Vectors Models
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
