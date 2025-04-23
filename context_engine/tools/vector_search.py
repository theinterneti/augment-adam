"""Vector search tool for the context engine."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from context_engine.db.redis_client import redis_client
from context_engine.db.neo4j_client import neo4j_client
from context_engine.db.embedding import embedding_model

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

async def vector_search(request: VectorSearchRequest) -> VectorSearchResponse:
    """Search for vectors similar to the query.
    
    Args:
        request: Vector search request
        
    Returns:
        Vector search response
    """
    import time
    
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
