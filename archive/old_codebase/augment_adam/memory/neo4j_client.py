"""Neo4j client for the Augment Adam memory system.

This module provides a Neo4j client for graph-based vector storage and retrieval.

Version: 0.1.0
Created: 2025-04-25
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from neo4j import AsyncGraphDatabase

from augment_adam.core.errors import (
    DatabaseError, wrap_error, log_error, ErrorCategory
)

logger = logging.getLogger(__name__)

# Environment variables with defaults
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class Neo4jClient:
    """Neo4j client for graph-based vector storage and retrieval.
    
    This class provides methods for storing, retrieving, and searching
    vector embeddings in a Neo4j graph database.
    
    Attributes:
        driver: Neo4j async driver instance
        vector_dimensions: Dimensions of the vector embeddings
        similarity_function: Similarity function to use for vector search
    """
    
    def __init__(
        self,
        uri: str = NEO4J_URI,
        user: str = NEO4J_USER,
        password: str = NEO4J_PASSWORD,
        vector_dimensions: int = 384,
        similarity_function: str = "cosine"
    ):
        """Initialize the Neo4j client.
        
        Args:
            uri: Neo4j server URI
            user: Neo4j username
            password: Neo4j password
            vector_dimensions: Dimensions of the vector embeddings
            similarity_function: Similarity function to use for vector search
        """
        self.driver = AsyncGraphDatabase.driver(
            uri,
            auth=(user, password)
        )
        self.vector_dimensions = vector_dimensions
        self.similarity_function = similarity_function
        
        logger.info(f"Initialized Neo4j client with URI: {uri}")
    
    async def create_index(self, collection_name: str = "default") -> bool:
        """Create the vector index if it doesn't exist.
        
        Args:
            collection_name: Name of the collection/index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            index_name = f"vector_index_{collection_name}"
            
            async with self.driver.session() as session:
                await session.run(f"""
                    CREATE VECTOR INDEX {index_name} IF NOT EXISTS
                    FOR (n:Vector:{collection_name}) ON (n.embedding)
                    OPTIONS {{
                      indexConfig: {{
                        `vector.dimensions`: {self.vector_dimensions},
                        `vector.similarity_function`: '{self.similarity_function}'
                      }}
                    }}
                """)
                
                logger.info(f"Created vector index: {index_name}")
                return True
                
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to create Neo4j vector index for collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
    
    async def store_vector(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        collection_name: str = "default"
    ) -> bool:
        """Store a vector in Neo4j.
        
        Args:
            vector_id: Unique identifier for the vector
            embedding: Vector embedding
            metadata: Metadata for the vector
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    f"""
                    MERGE (n:Vector:{collection_name} {{id: $id}})
                    SET n.embedding = $embedding,
                        n.metadata = $metadata,
                        n.timestamp = timestamp()
                    """,
                    id=vector_id,
                    embedding=embedding,
                    metadata=json.dumps(metadata)
                )
                
                logger.info(f"Stored vector {vector_id} in collection {collection_name}")
                return True
        
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to store vector in Neo4j collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "vector_id": vector_id,
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
    
    async def search_vectors(
        self,
        query_vector: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = "default"
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors in Neo4j.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_metadata: Filter to apply to the results
            collection_name: Name of the collection
            
        Returns:
            List of tuples containing the memory and its similarity score
        """
        try:
            index_name = f"vector_index_{collection_name}"
            
            # Build the filter query
            filter_query = ""
            if filter_metadata:
                filter_conditions = []
                for key, value in filter_metadata.items():
                    filter_conditions.append(f"json.{key} = '{value}' ")
                
                if filter_conditions:
                    filter_query = "WHERE " + " AND ".join(filter_conditions)
            
            async with self.driver.session() as session:
                result = await session.run(
                    f"""
                    CALL db.index.vector.queryNodes('{index_name}', $k, $embedding)
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
                    metadata["id"] = id
                    
                    # Convert score to similarity (Neo4j returns cosine similarity directly)
                    similarity = score
                    
                    search_results.append((metadata, similarity))
                
                logger.info(f"Found {len(search_results)} results in collection {collection_name}")
                return search_results
        
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to search vectors in Neo4j collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                    "filter_metadata": filter_metadata,
                },
            )
            log_error(error, logger=logger)
            return []
    
    async def get_by_id(
        self,
        vector_id: str,
        collection_name: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """Get a vector from Neo4j by ID.
        
        Args:
            vector_id: Vector ID
            collection_name: Name of the collection
            
        Returns:
            Vector metadata or None if not found
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    f"""
                    MATCH (n:Vector:{collection_name} {{id: $id}})
                    RETURN n.metadata AS metadata
                    """,
                    id=vector_id
                )
                
                record = await result.single()
                
                if not record:
                    logger.warning(f"Vector {vector_id} not found in collection {collection_name}")
                    return None
                
                metadata_json = record["metadata"]
                metadata = json.loads(metadata_json)
                metadata["id"] = vector_id
                
                return metadata
        
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to get vector by ID from Neo4j collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "vector_id": vector_id,
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return None
    
    async def delete(
        self,
        vector_id: str,
        collection_name: str = "default"
    ) -> bool:
        """Delete a vector from Neo4j.
        
        Args:
            vector_id: Vector ID
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    f"""
                    MATCH (n:Vector:{collection_name} {{id: $id}})
                    DELETE n
                    RETURN count(n) as deleted_count
                    """,
                    id=vector_id
                )
                
                record = await result.single()
                deleted_count = record["deleted_count"]
                
                if deleted_count == 0:
                    logger.warning(f"Vector {vector_id} not found in collection {collection_name}")
                    return False
                
                logger.info(f"Deleted vector {vector_id} from collection {collection_name}")
                return True
        
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to delete vector from Neo4j collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "vector_id": vector_id,
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
    
    async def clear(
        self,
        collection_name: str = "default"
    ) -> bool:
        """Clear all vectors from a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    f"""
                    MATCH (n:Vector:{collection_name})
                    DELETE n
                    RETURN count(n) as deleted_count
                    """
                )
                
                record = await result.single()
                deleted_count = record["deleted_count"]
                
                logger.info(f"Cleared {deleted_count} vectors from collection {collection_name}")
                return True
        
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to clear Neo4j collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
    
    async def create_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        collection_name: str = "default"
    ) -> bool:
        """Create a relationship between two vectors.
        
        Args:
            from_id: Source vector ID
            to_id: Target vector ID
            relationship_type: Type of relationship
            properties: Relationship properties
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    f"""
                    MATCH (from:Vector:{collection_name} {{id: $from_id}})
                    MATCH (to:Vector:{collection_name} {{id: $to_id}})
                    MERGE (from)-[r:{relationship_type}]->(to)
                    SET r += $properties
                    """,
                    from_id=from_id,
                    to_id=to_id,
                    properties=properties or {}
                )
                
                logger.info(f"Created relationship from {from_id} to {to_id} in collection {collection_name}")
                return True
        
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to create relationship in Neo4j collection: {collection_name}",
                category=ErrorCategory.DATABASE,
                details={
                    "from_id": from_id,
                    "to_id": to_id,
                    "relationship_type": relationship_type,
                    "collection_name": collection_name,
                },
            )
            log_error(error, logger=logger)
            return False
    
    async def close(self):
        """Close the Neo4j client."""
        try:
            await self.driver.close()
            logger.info("Closed Neo4j client")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to close Neo4j client",
                category=ErrorCategory.DATABASE
            )
            log_error(error, logger=logger)


# Global instance for singleton pattern
_default_client: Optional[Neo4jClient] = None


def get_neo4j_client(
    uri: str = NEO4J_URI,
    user: str = NEO4J_USER,
    password: str = NEO4J_PASSWORD,
    vector_dimensions: int = 384,
    similarity_function: str = "cosine"
) -> Neo4jClient:
    """Get the default Neo4j client instance.
    
    Args:
        uri: Neo4j server URI
        user: Neo4j username
        password: Neo4j password
        vector_dimensions: Dimensions of the vector embeddings
        similarity_function: Similarity function to use for vector search
        
    Returns:
        The default Neo4j client instance
    """
    global _default_client
    
    if _default_client is None:
        _default_client = Neo4jClient(
            uri=uri,
            user=user,
            password=password,
            vector_dimensions=vector_dimensions,
            similarity_function=similarity_function
        )
    
    return _default_client
