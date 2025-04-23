"""Redis client for the context engine."""

import os
import json
import numpy as np
from typing import Dict, Any, List, Optional
import redis.asyncio as redis

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redispassword")

class RedisClient:
    """Redis client for vector storage and retrieval."""
    
    def __init__(self):
        """Initialize the Redis client."""
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        self.binary_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=False
        )
    
    async def create_index(self) -> bool:
        """Create the vector index if it doesn't exist."""
        try:
            # Check if index exists
            try:
                await self.client.ft("vector_index").info()
                return True
            except:
                # Create vector index
                await self.client.execute_command(
                    "FT.CREATE", "vector_index", "ON", "HASH", "PREFIX", "1", "vector:",
                    "SCHEMA", 
                    "vector", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", 
                    "DIM", "384", "DISTANCE_METRIC", "COSINE",
                    "metadata", "TEXT"
                )
                return True
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    async def store_vector(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store a vector in Redis.
        
        Args:
            vector_id: Unique identifier for the vector
            embedding: Vector embedding
            metadata: Metadata for the vector
            ttl: Time to live in seconds (None for no expiration)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert embedding to bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            
            # Store the vector
            pipeline = self.binary_client.pipeline()
            pipeline.hset(f"vector:{vector_id}", mapping={
                "vector": embedding_bytes,
                "metadata": json.dumps(metadata)
            })
            
            if ttl:
                pipeline.expire(f"vector:{vector_id}", ttl)
                
            await pipeline.execute()
            
            # Update access stats
            await self.client.hincrby("vector:access_stats", vector_id, 1)
            
            return True
        
        except Exception as e:
            print(f"Error storing vector in Redis: {e}")
            return False
    
    async def search_vectors(self, query_vector: List[float], k: int = 10, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in Redis.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_dict: Filter to apply to the results
            
        Returns:
            List of results with id, score, and metadata
        """
        try:
            # Convert query vector to bytes
            query_vector_bytes = np.array(query_vector, dtype=np.float32).tobytes()
            
            # Perform the search
            result = await self.binary_client.execute_command(
                "FT.SEARCH", "vector_index",
                f"(*)=>[KNN {k} @vector $query_vector AS vector_score]",
                "PARAMS", 2, "query_vector", query_vector_bytes,
                "SORTBY", "vector_score",
                "DIALECT", 2
            )
            
            # Process the results
            search_results = []
            for i in range(1, len(result), 2):
                doc_id = result[i].decode('utf-8')
                doc_data = {k.decode('utf-8'): v if isinstance(v, bytes) else v.decode('utf-8') 
                           for k, v in result[i+1].items()}
                
                # Extract metadata
                metadata = json.loads(doc_data.get("metadata", "{}"))
                
                # Apply filter if provided
                if filter_dict:
                    skip = False
                    for key, value in filter_dict.items():
                        if key not in metadata or metadata[key] != value:
                            skip = True
                            break
                    if skip:
                        continue
                
                # Calculate score (convert from distance to similarity)
                score = 1 - float(doc_data.get("vector_score", 0))
                
                search_results.append({
                    "id": doc_id.replace("vector:", ""),
                    "score": score,
                    "metadata": metadata
                })
                
                # Update access stats
                await self.client.hincrby("vector:access_stats", doc_id.replace("vector:", ""), 1)
            
            return search_results
        
        except Exception as e:
            print(f"Error searching vectors in Redis: {e}")
            return []
    
    async def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector from Redis.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            Vector data with embedding and metadata
        """
        try:
            # Get the vector
            vector_data = await self.binary_client.hgetall(f"vector:{vector_id}")
            
            if not vector_data:
                return None
            
            # Convert bytes to vector
            vector_bytes = vector_data.get(b"vector", b"")
            if not vector_bytes:
                return None
            
            vector = np.frombuffer(vector_bytes, dtype=np.float32).tolist()
            
            # Extract metadata
            metadata_bytes = vector_data.get(b"metadata", b"{}")
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            # Update access stats
            await self.client.hincrby("vector:access_stats", vector_id, 1)
            
            return {
                "id": vector_id,
                "embedding": vector,
                "metadata": metadata
            }
        
        except Exception as e:
            print(f"Error getting vector from Redis: {e}")
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from Redis.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete the vector
            await self.client.delete(f"vector:{vector_id}")
            
            # Remove from access stats
            await self.client.hdel("vector:access_stats", vector_id)
            
            return True
        
        except Exception as e:
            print(f"Error deleting vector from Redis: {e}")
            return False
    
    async def close(self):
        """Close the Redis client."""
        await self.client.close()
        await self.binary_client.close()


# Singleton instance
redis_client = RedisClient()
