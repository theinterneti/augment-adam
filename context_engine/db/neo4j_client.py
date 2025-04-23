"""Neo4j client for the context engine."""

import os
import json
from typing import Dict, Any, List, Optional
from neo4j import AsyncGraphDatabase

# Environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neopassword")

class Neo4jClient:
    """Neo4j client for graph storage and retrieval."""
    
    def __init__(self):
        """Initialize the Neo4j client."""
        self.driver = AsyncGraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    
    async def create_index(self) -> bool:
        """Create the vector index if it doesn't exist."""
        try:
            async with self.driver.session() as session:
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
                return True
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    async def store_vector(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any]) -> bool:
        """Store a vector in Neo4j.
        
        Args:
            vector_id: Unique identifier for the vector
            embedding: Vector embedding
            metadata: Metadata for the vector
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    MERGE (n:Vector {id: $id})
                    SET n.embedding = $embedding,
                        n.metadata = $metadata
                    """,
                    id=vector_id,
                    embedding=embedding,
                    metadata=json.dumps(metadata)
                )
                return True
        
        except Exception as e:
            print(f"Error storing vector in Neo4j: {e}")
            return False
    
    async def search_vectors(self, query_vector: List[float], k: int = 10, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in Neo4j.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_dict: Filter to apply to the results
            
        Returns:
            List of results with id, score, and metadata
        """
        try:
            # Build the filter query
            filter_query = ""
            if filter_dict:
                filter_conditions = []
                for key, value in filter_dict.items():
                    filter_conditions.append(f"json.metadata CONTAINS '{{\"{key}\": \"{value}\"}}' ")
                
                if filter_conditions:
                    filter_query = "WHERE " + " AND ".join(filter_conditions)
            
            async with self.driver.session() as session:
                result = await session.run(
                    f"""
                    CALL db.index.vector.queryNodes('vector_index', $k, $embedding)
                    YIELD node, score
                    WITH node, score, apoc.convert.fromJsonMap(node.metadata) AS json
                    {filter_query}
                    RETURN node.id AS id, score, node.metadata AS metadata
                    ORDER BY score DESC
                    LIMIT $k
                    """,
                    embedding=query_vector,
                    k=k
                )
                
                records = await result.values()
                
                # Process the results
                search_results = []
                for record in records:
                    id, score, metadata_json = record
                    metadata = json.loads(metadata_json)
                    
                    search_results.append({
                        "id": id,
                        "score": score,
                        "metadata": metadata
                    })
                
                return search_results
        
        except Exception as e:
            print(f"Error searching vectors in Neo4j: {e}")
            return []
    
    async def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector from Neo4j.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            Vector data with embedding and metadata
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (n:Vector {id: $id})
                    RETURN n.embedding AS embedding, n.metadata AS metadata
                    """,
                    id=vector_id
                )
                
                record = await result.single()
                
                if not record:
                    return None
                
                embedding, metadata_json = record
                metadata = json.loads(metadata_json)
                
                return {
                    "id": vector_id,
                    "embedding": embedding,
                    "metadata": metadata
                }
        
        except Exception as e:
            print(f"Error getting vector from Neo4j: {e}")
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from Neo4j.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    MATCH (n:Vector {id: $id})
                    DELETE n
                    """,
                    id=vector_id
                )
                return True
        
        except Exception as e:
            print(f"Error deleting vector from Neo4j: {e}")
            return False
    
    async def create_relationship(self, from_id: str, to_id: str, relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Create a relationship between two vectors.
        
        Args:
            from_id: Source vector ID
            to_id: Target vector ID
            relationship_type: Type of relationship
            properties: Relationship properties
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    f"""
                    MATCH (from:Vector {{id: $from_id}})
                    MATCH (to:Vector {{id: $to_id}})
                    MERGE (from)-[r:{relationship_type}]->(to)
                    SET r += $properties
                    """,
                    from_id=from_id,
                    to_id=to_id,
                    properties=properties or {}
                )
                return True
        
        except Exception as e:
            print(f"Error creating relationship in Neo4j: {e}")
            return False
    
    async def get_related_vectors(self, vector_id: str, relationship_type: Optional[str] = None, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get vectors related to a vector.
        
        Args:
            vector_id: Vector ID
            relationship_type: Type of relationship (None for any)
            max_depth: Maximum depth of relationships
            
        Returns:
            List of related vectors
        """
        try:
            # Build the relationship query
            rel_query = ""
            if relationship_type:
                rel_query = f":{relationship_type}"
            
            async with self.driver.session() as session:
                result = await session.run(
                    f"""
                    MATCH (n:Vector {{id: $id}})-[r{rel_query}*1..{max_depth}]->(related:Vector)
                    RETURN related.id AS id, related.metadata AS metadata
                    """,
                    id=vector_id
                )
                
                records = await result.values()
                
                # Process the results
                related_vectors = []
                for record in records:
                    id, metadata_json = record
                    metadata = json.loads(metadata_json)
                    
                    related_vectors.append({
                        "id": id,
                        "metadata": metadata
                    })
                
                return related_vectors
        
        except Exception as e:
            print(f"Error getting related vectors from Neo4j: {e}")
            return []
    
    async def close(self):
        """Close the Neo4j client."""
        await self.driver.close()


# Singleton instance
neo4j_client = Neo4jClient()
