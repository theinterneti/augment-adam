import os
import json
import time
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
from sentence_transformers import SentenceTransformer

# Initialize FastAPI app
app = FastAPI(title="Context Engine API", description="API for the high-performance context engine")

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redispassword")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neopassword")

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Initialize Neo4j driver
neo4j_driver = AsyncGraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Pydantic models
class VectorSearchRequest(BaseModel):
    query: str
    k: int = 10
    include_metadata: bool = True
    filter: Optional[Dict[str, Any]] = None

class VectorStoreRequest(BaseModel):
    text: str
    metadata: Dict[str, Any]
    tier: str = "hot"  # "hot", "warm", or "cold"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class SearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query_time_ms: float

# Helper functions
async def create_indexes():
    """Create necessary indexes in Redis and Neo4j."""
    try:
        # Check if Redis index exists
        try:
            await redis_client.ft("vector_index").info()
        except:
            # Create Redis vector index
            await redis_client.execute_command(
                "FT.CREATE", "vector_index", "ON", "HASH", "PREFIX", "1", "vector:",
                "SCHEMA", 
                "vector", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", 
                "DIM", "384", "DISTANCE_METRIC", "COSINE",
                "metadata", "TEXT"
            )
        
        # Create Neo4j vector index
        async with neo4j_driver.session() as session:
            await session.run("""
                CREATE VECTOR INDEX vector_index IF NOT EXISTS
                FOR (n:Vector) ON (n.embedding)
                OPTIONS {
                  indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                  }
                }
            """)
    except Exception as e:
        print(f"Error creating indexes: {e}")

# API endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    await create_indexes()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/search", response_model=SearchResponse)
async def search(request: VectorSearchRequest):
    """Search for similar vectors."""
    start_time = time.time()
    
    # Generate embedding for the query
    query_embedding = model.encode(request.query).tolist()
    
    # Convert query embedding to bytes for Redis
    query_embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
    
    try:
        # Perform the search in Redis
        result = await redis_client.execute_command(
            "FT.SEARCH", "vector_index",
            f"(*)=>[KNN {request.k} @vector $query_vector AS vector_score]",
            "PARAMS", 2, "query_vector", query_embedding_bytes,
            "SORTBY", "vector_score",
            "DIALECT", 2
        )
        
        # Process the results
        search_results = []
        for i in range(1, len(result), 2):
            doc_id = result[i]
            doc_data = result[i+1]
            
            # Extract metadata
            metadata = json.loads(doc_data.get("metadata", "{}"))
            
            # Apply filter if provided
            if request.filter:
                skip = False
                for key, value in request.filter.items():
                    if key not in metadata or metadata[key] != value:
                        skip = True
                        break
                if skip:
                    continue
            
            # Calculate score (convert from distance to similarity)
            score = 1 - float(doc_data.get("vector_score", 0))
            
            search_results.append(SearchResult(
                id=doc_id.replace("vector:", ""),
                score=score,
                metadata=metadata
            ))
        
        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query_time_ms=query_time_ms
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/store", response_model=TaskResponse)
async def store_vector(request: VectorStoreRequest, background_tasks: BackgroundTasks):
    """Store a vector in the database."""
    try:
        # Generate a unique ID
        vector_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = model.encode(request.text).tolist()
        
        # Store in the appropriate tier
        if request.tier in ["hot", "warm"]:
            # Store in Redis
            background_tasks.add_task(store_in_redis, vector_id, embedding, request.metadata, request.tier)
        else:
            # Store in Neo4j
            background_tasks.add_task(store_in_neo4j, vector_id, embedding, request.metadata)
        
        return TaskResponse(
            task_id=vector_id,
            status="processing",
            message=f"Vector storage initiated in {request.tier} tier"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

async def store_in_redis(vector_id: str, embedding: List[float], metadata: Dict[str, Any], tier: str):
    """Store a vector in Redis."""
    try:
        # Convert embedding to bytes
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        
        # Set TTL based on tier
        ttl = None
        if tier == "warm":
            ttl = 86400  # 24 hours
        
        # Store the vector
        pipeline = redis_client.pipeline()
        pipeline.hset(f"vector:{vector_id}", mapping={
            "vector": embedding_bytes,
            "metadata": json.dumps(metadata)
        })
        
        if ttl:
            pipeline.expire(f"vector:{vector_id}", ttl)
            
        await pipeline.execute()
    
    except Exception as e:
        print(f"Error storing vector in Redis: {e}")

async def store_in_neo4j(vector_id: str, embedding: List[float], metadata: Dict[str, Any]):
    """Store a vector in Neo4j."""
    try:
        async with neo4j_driver.session() as session:
            await session.run(
                """
                CREATE (n:Vector {
                    id: $id,
                    embedding: $embedding,
                    metadata: $metadata
                })
                """,
                id=vector_id,
                embedding=embedding,
                metadata=json.dumps(metadata)
            )
    
    except Exception as e:
        print(f"Error storing vector in Neo4j: {e}")

@app.post("/graph-search")
async def graph_search(request: VectorSearchRequest):
    """Search for similar vectors with graph context."""
    try:
        # Generate embedding for the query
        query_embedding = model.encode(request.query).tolist()
        
        # Perform the search in Neo4j
        async with neo4j_driver.session() as session:
            result = await session.run(
                """
                CALL db.index.vector.queryNodes('vector_index', $k, $embedding)
                YIELD node, score
                RETURN node.id AS id, score, node.metadata AS metadata
                ORDER BY score DESC
                LIMIT $k
                """,
                embedding=query_embedding,
                k=request.k
            )
            
            records = await result.values()
            
            # Process the results
            search_results = []
            for record in records:
                id, score, metadata_json = record
                metadata = json.loads(metadata_json)
                
                # Apply filter if provided
                if request.filter:
                    skip = False
                    for key, value in request.filter.items():
                        if key not in metadata or metadata[key] != value:
                            skip = True
                            break
                    if skip:
                        continue
                
                search_results.append(SearchResult(
                    id=id,
                    score=score,
                    metadata=metadata
                ))
            
            return SearchResponse(
                results=search_results,
                total=len(search_results),
                query_time_ms=0  # Neo4j doesn't provide query time
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
