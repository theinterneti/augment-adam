"""Task processor for the context engine."""

import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
import redis.asyncio as redis

from context_engine.db.redis_client import redis_client as vector_redis_client
from context_engine.db.neo4j_client import neo4j_client
from context_engine.db.embedding import embedding_model

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redispassword")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))

# Task queue name
TASK_QUEUE = "context_engine:tasks"
TASK_GROUP = "context_engine:worker"

class TaskProcessor:
    """Task processor for background tasks."""
    
    def __init__(self):
        """Initialize the task processor."""
        self.running = True
        self.tasks = []
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
    
    async def setup(self):
        """Set up the task processor."""
        # Create consumer group if it doesn't exist
        try:
            await self.redis_client.xgroup_create(TASK_QUEUE, TASK_GROUP, mkstream=True)
        except redis.ResponseError:
            # Group already exists
            pass
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]):
        """Process a single task.
        
        Args:
            task_id: Task ID
            task_data: Task data
        """
        try:
            task_type = task_data.get("type")
            parameters = task_data.get("parameters", {})
            
            print(f"Processing task {task_id} of type {task_type}")
            
            if task_type == "index_code":
                await self.index_code(parameters)
            elif task_type == "update_knowledge_graph":
                await self.update_knowledge_graph(parameters)
            elif task_type == "sync_vectors":
                await self.sync_vectors(parameters)
            elif task_type == "prune_vectors":
                await self.prune_vectors(parameters)
            else:
                print(f"Unknown task type: {task_type}")
            
            # Update task status
            await self.redis_client.hset(f"task:{task_id}", mapping={
                "status": "completed",
                "completed_at": time.time()
            })
            
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            
            # Update task status
            await self.redis_client.hset(f"task:{task_id}", mapping={
                "status": "failed",
                "error": str(e),
                "completed_at": time.time()
            })
    
    async def index_code(self, parameters: Dict[str, Any]):
        """Index code in the vector database.
        
        Args:
            parameters: Task parameters
        """
        code_text = parameters.get("code", "")
        file_path = parameters.get("file_path", "")
        language = parameters.get("language", "")
        metadata = parameters.get("metadata", {})
        
        if not code_text:
            raise ValueError("Code text is required")
        
        # Generate embedding
        embedding = embedding_model.encode(code_text)
        
        # Add file path and language to metadata
        metadata["file_path"] = file_path
        if language:
            metadata["language"] = language
        
        # Store in Redis (hot tier)
        await vector_redis_client.store_vector(
            vector_id=file_path,
            embedding=embedding,
            metadata=metadata
        )
        
        # Store in Neo4j (cold tier) for graph relationships
        await neo4j_client.store_vector(
            vector_id=file_path,
            embedding=embedding,
            metadata=metadata
        )
    
    async def update_knowledge_graph(self, parameters: Dict[str, Any]):
        """Update the knowledge graph with new relationships.
        
        Args:
            parameters: Task parameters
        """
        from_id = parameters.get("from_id", "")
        to_id = parameters.get("to_id", "")
        relationship_type = parameters.get("relationship_type", "")
        properties = parameters.get("properties", {})
        
        if not from_id or not to_id or not relationship_type:
            raise ValueError("from_id, to_id, and relationship_type are required")
        
        # Create the relationship
        await neo4j_client.create_relationship(
            from_id=from_id,
            to_id=to_id,
            relationship_type=relationship_type,
            properties=properties
        )
    
    async def sync_vectors(self, parameters: Dict[str, Any]):
        """Synchronize vectors between Redis and Neo4j.
        
        Args:
            parameters: Task parameters
        """
        direction = parameters.get("direction", "redis_to_neo4j")
        batch_size = parameters.get("batch_size", 100)
        
        if direction == "redis_to_neo4j":
            # Get all vectors from Redis
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match="vector:*", count=batch_size)
                
                for key in keys:
                    if key == "vector:access_stats":
                        continue
                    
                    vector_data = await self.redis_client.hgetall(key)
                    if not vector_data:
                        continue
                    
                    vector_id = key.replace("vector:", "")
                    metadata = json.loads(vector_data.get("metadata", "{}"))
                    
                    # Get the vector from Redis
                    vector = await vector_redis_client.get_vector(vector_id)
                    if not vector:
                        continue
                    
                    # Store in Neo4j
                    await neo4j_client.store_vector(
                        vector_id=vector_id,
                        embedding=vector["embedding"],
                        metadata=metadata
                    )
                
                if cursor == 0:
                    break
        
        elif direction == "neo4j_to_redis":
            # Get all vectors from Neo4j
            async with neo4j_client.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (n:Vector)
                    RETURN n.id AS id, n.embedding AS embedding, n.metadata AS metadata
                    LIMIT $batch_size
                    """,
                    batch_size=batch_size
                )
                
                records = await result.values()
                
                for record in records:
                    vector_id, embedding, metadata_json = record
                    
                    if not vector_id or not embedding:
                        continue
                    
                    # Parse metadata
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    # Store in Redis
                    await vector_redis_client.store_vector(
                        vector_id=vector_id,
                        embedding=embedding,
                        metadata=metadata
                    )
    
    async def prune_vectors(self, parameters: Dict[str, Any]):
        """Prune old or unused vectors.
        
        Args:
            parameters: Task parameters
        """
        max_age = parameters.get("max_age", 30 * 24 * 60 * 60)  # 30 days in seconds
        min_access_count = parameters.get("min_access_count", 5)
        batch_size = parameters.get("batch_size", 100)
        
        # Get access statistics
        access_stats = await self.redis_client.hgetall("vector:access_stats")
        
        # Get all vectors from Redis
        cursor = 0
        while True:
            cursor, keys = await self.redis_client.scan(cursor, match="vector:*", count=batch_size)
            
            for key in keys:
                if key == "vector:access_stats":
                    continue
                
                vector_id = key.replace("vector:", "")
                
                # Check access count
                access_count = int(access_stats.get(vector_id, 0))
                
                if access_count < min_access_count:
                    # Get creation time from metadata
                    vector_data = await self.redis_client.hgetall(key)
                    metadata = json.loads(vector_data.get("metadata", "{}"))
                    created_at = metadata.get("created_at", 0)
                    
                    # Check age
                    age = time.time() - created_at
                    
                    if age > max_age:
                        # Move to Neo4j before deleting from Redis
                        await self.sync_vectors({"direction": "redis_to_neo4j", "batch_size": 1})
                        
                        # Delete from Redis
                        await self.redis_client.delete(key)
                        
                        # Remove from access stats
                        await self.redis_client.hdel("vector:access_stats", vector_id)
            
            if cursor == 0:
                break
    
    async def run(self):
        """Run the task processor."""
        await self.setup()
        
        print(f"Task processor started with concurrency {WORKER_CONCURRENCY}")
        
        while self.running:
            try:
                # Read from the task queue
                tasks = await self.redis_client.xreadgroup(
                    TASK_GROUP, f"worker-{os.getpid()}",
                    {TASK_QUEUE: ">"},
                    count=WORKER_CONCURRENCY,
                    block=1000
                )
                
                if not tasks:
                    await asyncio.sleep(0.1)
                    continue
                
                # Process tasks
                for stream, entries in tasks:
                    for entry_id, task_data in entries:
                        # Convert task data
                        task = {}
                        for key, value in task_data.items():
                            task[key] = value
                        
                        # Process the task
                        task_id = task.get("id", entry_id)
                        asyncio.create_task(self.process_task(task_id, task))
                        
                        # Acknowledge the task
                        await self.redis_client.xack(TASK_QUEUE, TASK_GROUP, entry_id)
            
            except Exception as e:
                print(f"Error in task processor loop: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the task processor."""
        self.running = False
        
        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks)
        
        # Close Redis client
        await self.redis_client.close()


async def main():
    """Main entry point."""
    processor = TaskProcessor()
    
    try:
        await processor.run()
    except KeyboardInterrupt:
        print("Task processor stopping...")
    finally:
        await processor.stop()
        await vector_redis_client.close()
        await neo4j_client.close()

if __name__ == "__main__":
    asyncio.run(main())
