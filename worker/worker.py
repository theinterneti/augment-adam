import os
import json
import time
import asyncio
import numpy as np
from typing import Dict, Any, List
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
from sentence_transformers import SentenceTransformer

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redispassword")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neopassword")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))

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

# Task queue name
TASK_QUEUE = "context_engine:tasks"
TASK_GROUP = "context_engine:worker"

class Worker:
    def __init__(self):
        self.running = True
        self.tasks = []
    
    async def setup(self):
        """Set up the worker."""
        # Create consumer group if it doesn't exist
        try:
            await redis_client.xgroup_create(TASK_QUEUE, TASK_GROUP, mkstream=True)
        except redis.ResponseError:
            # Group already exists
            pass
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]):
        """Process a single task."""
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
            await redis_client.hset(f"task:{task_id}", mapping={
                "status": "completed",
                "completed_at": time.time()
            })
            
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            
            # Update task status
            await redis_client.hset(f"task:{task_id}", mapping={
                "status": "failed",
                "error": str(e),
                "completed_at": time.time()
            })
    
    async def index_code(self, parameters: Dict[str, Any]):
        """Index code in the vector database."""
        code_text = parameters.get("code", "")
        file_path = parameters.get("file_path", "")
        metadata = parameters.get("metadata", {})
        
        if not code_text:
            raise ValueError("Code text is required")
        
        # Generate embedding
        embedding = model.encode(code_text).tolist()
        
        # Store in Redis (hot tier)
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        
        # Add file path to metadata
        metadata["file_path"] = file_path
        
        # Store the vector
        await redis_client.hset(f"vector:{file_path}", mapping={
            "vector": embedding_bytes,
            "metadata": json.dumps(metadata)
        })
        
        # Store in Neo4j (cold tier) for graph relationships
        async with neo4j_driver.session() as session:
            await session.run(
                """
                MERGE (f:File {path: $file_path})
                CREATE (c:Code {
                    id: $id,
                    embedding: $embedding,
                    content: $code,
                    metadata: $metadata
                })
                CREATE (f)-[:CONTAINS]->(c)
                """,
                id=file_path,
                file_path=file_path,
                embedding=embedding,
                code=code_text,
                metadata=json.dumps(metadata)
            )
    
    async def update_knowledge_graph(self, parameters: Dict[str, Any]):
        """Update the knowledge graph with new relationships."""
        entity_type = parameters.get("entity_type", "")
        entity_id = parameters.get("entity_id", "")
        relationships = parameters.get("relationships", [])
        
        if not entity_id or not entity_type:
            raise ValueError("Entity ID and type are required")
        
        async with neo4j_driver.session() as session:
            # Create or update the entity
            await session.run(
                """
                MERGE (e:{entity_type} {{id: $entity_id}})
                SET e += $properties
                """.format(entity_type=entity_type),
                entity_id=entity_id,
                properties=parameters.get("properties", {})
            )
            
            # Create relationships
            for rel in relationships:
                target_type = rel.get("target_type", "")
                target_id = rel.get("target_id", "")
                rel_type = rel.get("rel_type", "")
                rel_properties = rel.get("properties", {})
                
                if not target_id or not target_type or not rel_type:
                    continue
                
                await session.run(
                    """
                    MATCH (e:{entity_type} {{id: $entity_id}})
                    MERGE (t:{target_type} {{id: $target_id}})
                    MERGE (e)-[r:{rel_type}]->(t)
                    SET r += $properties
                    """.format(
                        entity_type=entity_type,
                        target_type=target_type,
                        rel_type=rel_type
                    ),
                    entity_id=entity_id,
                    target_id=target_id,
                    properties=rel_properties
                )
    
    async def sync_vectors(self, parameters: Dict[str, Any]):
        """Synchronize vectors between Redis and Neo4j."""
        direction = parameters.get("direction", "redis_to_neo4j")
        batch_size = parameters.get("batch_size", 100)
        
        if direction == "redis_to_neo4j":
            # Get all vectors from Redis
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(cursor, match="vector:*", count=batch_size)
                
                for key in keys:
                    vector_data = await redis_client.hgetall(key)
                    if not vector_data:
                        continue
                    
                    vector_id = key.replace("vector:", "")
                    metadata = json.loads(vector_data.get("metadata", "{}"))
                    
                    # Convert bytes to vector
                    vector_bytes = vector_data.get("vector", b"")
                    if not vector_bytes:
                        continue
                    
                    vector = np.frombuffer(vector_bytes, dtype=np.float32).tolist()
                    
                    # Store in Neo4j
                    async with neo4j_driver.session() as session:
                        await session.run(
                            """
                            MERGE (n:Vector {id: $id})
                            SET n.embedding = $embedding,
                                n.metadata = $metadata
                            """,
                            id=vector_id,
                            embedding=vector,
                            metadata=json.dumps(metadata)
                        )
                
                if cursor == 0:
                    break
        
        elif direction == "neo4j_to_redis":
            # Get all vectors from Neo4j
            async with neo4j_driver.session() as session:
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
                    
                    # Convert embedding to bytes
                    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
                    
                    # Parse metadata
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    # Store in Redis
                    await redis_client.hset(f"vector:{vector_id}", mapping={
                        "vector": embedding_bytes,
                        "metadata": json.dumps(metadata)
                    })
    
    async def prune_vectors(self, parameters: Dict[str, Any]):
        """Prune old or unused vectors."""
        max_age = parameters.get("max_age", 30 * 24 * 60 * 60)  # 30 days in seconds
        min_access_count = parameters.get("min_access_count", 5)
        batch_size = parameters.get("batch_size", 100)
        
        # Get access statistics
        access_stats = await redis_client.hgetall("vector:access_stats")
        
        # Get all vectors from Redis
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor, match="vector:*", count=batch_size)
            
            for key in keys:
                if key == "vector:access_stats":
                    continue
                
                vector_id = key.replace("vector:", "")
                
                # Check access count
                access_count = int(access_stats.get(vector_id, 0))
                
                if access_count < min_access_count:
                    # Get creation time from metadata
                    vector_data = await redis_client.hgetall(key)
                    metadata = json.loads(vector_data.get("metadata", "{}"))
                    created_at = metadata.get("created_at", 0)
                    
                    # Check age
                    age = time.time() - created_at
                    
                    if age > max_age:
                        # Move to Neo4j before deleting from Redis
                        await self.sync_vectors({"direction": "redis_to_neo4j", "batch_size": 1})
                        
                        # Delete from Redis
                        await redis_client.delete(key)
                        
                        # Remove from access stats
                        await redis_client.hdel("vector:access_stats", vector_id)
            
            if cursor == 0:
                break
    
    async def run(self):
        """Run the worker."""
        await self.setup()
        
        print(f"Worker started with concurrency {WORKER_CONCURRENCY}")
        
        while self.running:
            try:
                # Read from the task queue
                tasks = await redis_client.xreadgroup(
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
                        await redis_client.xack(TASK_QUEUE, TASK_GROUP, entry_id)
            
            except Exception as e:
                print(f"Error in worker loop: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the worker."""
        self.running = False
        
        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks)

async def main():
    """Main entry point."""
    worker = Worker()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        print("Worker stopping...")
    finally:
        await worker.stop()
        await redis_client.close()
        await neo4j_driver.close()

if __name__ == "__main__":
    asyncio.run(main())
