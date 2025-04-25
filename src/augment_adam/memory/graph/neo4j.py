"""
Neo4j-based graph memory system.

This module provides a graph memory system based on Neo4j,
which is a graph database management system.
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, cast
from neo4j import GraphDatabase

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.graph.base import GraphMemory, GraphMemoryItem, Node, Edge, Relationship


@tag("memory.graph.neo4j")
class Neo4jMemory(GraphMemory[GraphMemoryItem]):
    """
    Neo4j-based graph memory system.
    
    This class implements a graph memory system using Neo4j for efficient
    storage and retrieval of graph data.
    
    Attributes:
        name: The name of the memory system.
        uri: The URI of the Neo4j database.
        username: The username for the Neo4j database.
        password: The password for the Neo4j database.
        driver: The Neo4j driver.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str, uri: str, username: str, password: str) -> None:
        """
        Initialize the Neo4j memory system.
        
        Args:
            name: The name of the memory system.
            uri: The URI of the Neo4j database.
            username: The username for the Neo4j database.
            password: The password for the Neo4j database.
        """
        super().__init__(name)
        
        self.uri = uri
        self.username = username
        self.password = password
        
        # Create Neo4j driver
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Initialize the database
        self._init_database()
        
        self.metadata["uri"] = uri
        self.metadata["username"] = username
    
    def _init_database(self) -> None:
        """Initialize the Neo4j database."""
        with self.driver.session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:EDGE]-() REQUIRE r.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE")
    
    def add(self, item: GraphMemoryItem) -> str:
        """
        Add an item to memory.
        
        Args:
            item: The item to add to memory.
            
        Returns:
            The ID of the added item.
        """
        # Add the item to the dictionary
        super().add(item)
        
        # Add the item to the Neo4j database
        with self.driver.session() as session:
            # Create the item node
            session.run(
                "CREATE (i:Item {id: $id, content: $content, created_at: $created_at, updated_at: $updated_at, expires_at: $expires_at, importance: $importance})",
                id=item.id,
                content=str(item.content) if item.content is not None else None,
                created_at=item.created_at,
                updated_at=item.updated_at,
                expires_at=item.expires_at,
                importance=item.importance
            )
            
            # Add metadata
            for key, value in item.metadata.items():
                session.run(
                    "MATCH (i:Item {id: $id}) SET i[$key] = $value",
                    id=item.id,
                    key=key,
                    value=str(value)
                )
            
            # Add nodes
            for node in item.nodes.values():
                self._add_node_to_neo4j(item.id, node)
            
            # Add edges
            for edge in item.edges.values():
                self._add_edge_to_neo4j(item.id, edge)
        
        return item.id
    
    def _add_node_to_neo4j(self, item_id: str, node: Node) -> None:
        """
        Add a node to the Neo4j database.
        
        Args:
            item_id: The ID of the memory item.
            node: The node to add.
        """
        with self.driver.session() as session:
            # Create the node
            query = "MATCH (i:Item {id: $item_id}) CREATE (n:Node {id: $id, created_at: $created_at, updated_at: $updated_at})"
            
            # Add labels
            for label in node.labels:
                query += f" SET n:`{label}`"
            
            # Add properties
            for key, value in node.properties.items():
                query += f" SET n.`{key}` = ${key}"
            
            # Create relationship to item
            query += " CREATE (i)-[:CONTAINS]->(n)"
            
            # Execute the query
            params = {
                "item_id": item_id,
                "id": node.id,
                "created_at": node.created_at,
                "updated_at": node.updated_at,
                **{key: str(value) for key, value in node.properties.items()}
            }
            
            session.run(query, **params)
    
    def _add_edge_to_neo4j(self, item_id: str, edge: Edge) -> None:
        """
        Add an edge to the Neo4j database.
        
        Args:
            item_id: The ID of the memory item.
            edge: The edge to add.
        """
        with self.driver.session() as session:
            # Create the edge
            relationship_type = edge.relationship.name if isinstance(edge.relationship, Relationship) else edge.relationship
            
            query = """
            MATCH (i:Item {id: $item_id})
            MATCH (s:Node {id: $source_id})
            MATCH (t:Node {id: $target_id})
            CREATE (s)-[r:EDGE {id: $id, type: $type, created_at: $created_at, updated_at: $updated_at}]->(t)
            """
            
            # Add properties
            for key, value in edge.properties.items():
                query += f" SET r.`{key}` = ${key}"
            
            # Execute the query
            params = {
                "item_id": item_id,
                "id": edge.id,
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "type": relationship_type,
                "created_at": edge.created_at,
                "updated_at": edge.updated_at,
                **{key: str(value) for key, value in edge.properties.items()}
            }
            
            session.run(query, **params)
    
    def get(self, item_id: str) -> Optional[GraphMemoryItem]:
        """
        Get an item from memory by ID.
        
        Args:
            item_id: The ID of the item to get.
            
        Returns:
            The item, or None if it doesn't exist.
        """
        # Get the item from the dictionary
        item = super().get(item_id)
        
        # If the item doesn't exist in the dictionary but exists in the database, load it
        if item is None:
            with self.driver.session() as session:
                # Check if the item exists
                result = session.run(
                    "MATCH (i:Item {id: $id}) RETURN i",
                    id=item_id
                )
                
                if result.peek() is None:
                    return None
                
                # Create the item
                item = self._load_item_from_neo4j(item_id)
                
                # Add the item to the dictionary
                if item is not None:
                    self.items[item_id] = item
        
        return item
    
    def _load_item_from_neo4j(self, item_id: str) -> Optional[GraphMemoryItem]:
        """
        Load an item from the Neo4j database.
        
        Args:
            item_id: The ID of the item to load.
            
        Returns:
            The loaded item, or None if it doesn't exist.
        """
        with self.driver.session() as session:
            # Get the item
            result = session.run(
                "MATCH (i:Item {id: $id}) RETURN i",
                id=item_id
            )
            
            if result.peek() is None:
                return None
            
            record = result.single()
            item_data = record["i"]
            
            # Create the item
            item = GraphMemoryItem(
                id=item_id,
                content=item_data.get("content"),
                created_at=item_data.get("created_at"),
                updated_at=item_data.get("updated_at"),
                expires_at=item_data.get("expires_at"),
                importance=item_data.get("importance", 0.5)
            )
            
            # Add metadata
            for key, value in item_data.items():
                if key not in ["id", "content", "created_at", "updated_at", "expires_at", "importance"]:
                    item.metadata[key] = value
            
            # Load nodes
            result = session.run(
                "MATCH (i:Item {id: $id})-[:CONTAINS]->(n:Node) RETURN n",
                id=item_id
            )
            
            for record in result:
                node_data = record["n"]
                
                # Create the node
                node = Node(
                    id=node_data.get("id"),
                    created_at=node_data.get("created_at"),
                    updated_at=node_data.get("updated_at")
                )
                
                # Add labels
                for label in node_data.labels:
                    if label != "Node":
                        node.labels.append(label)
                
                # Add properties
                for key, value in node_data.items():
                    if key not in ["id", "created_at", "updated_at"]:
                        node.properties[key] = value
                
                # Add the node to the item
                item.nodes[node.id] = node
            
            # Load edges
            result = session.run(
                """
                MATCH (i:Item {id: $id})-[:CONTAINS]->(s:Node)-[r:EDGE]->(t:Node)
                RETURN r, s.id AS source_id, t.id AS target_id
                """,
                id=item_id
            )
            
            for record in result:
                edge_data = record["r"]
                source_id = record["source_id"]
                target_id = record["target_id"]
                
                # Create the edge
                edge = Edge(
                    id=edge_data.get("id"),
                    source_id=source_id,
                    target_id=target_id,
                    relationship=edge_data.get("type", Relationship.RELATED_TO),
                    created_at=edge_data.get("created_at"),
                    updated_at=edge_data.get("updated_at")
                )
                
                # Add properties
                for key, value in edge_data.items():
                    if key not in ["id", "type", "created_at", "updated_at"]:
                        edge.properties[key] = value
                
                # Add the edge to the item
                item.edges[edge.id] = edge
            
            return item
    
    def update(self, item_id: str, content: Any = None, metadata: Dict[str, Any] = None) -> Optional[GraphMemoryItem]:
        """
        Update an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            content: New content for the item.
            metadata: New metadata for the item.
            
        Returns:
            The updated item, or None if it doesn't exist.
        """
        # Update the item in the dictionary
        item = super().update(item_id, content, metadata)
        
        # If the item was updated, update it in the Neo4j database
        if item is not None:
            with self.driver.session() as session:
                # Update the item
                query = "MATCH (i:Item {id: $id}) SET i.updated_at = $updated_at"
                
                if content is not None:
                    query += ", i.content = $content"
                
                params = {
                    "id": item_id,
                    "updated_at": item.updated_at,
                    "content": str(content) if content is not None else None
                }
                
                session.run(query, **params)
                
                # Update metadata
                if metadata is not None:
                    for key, value in metadata.items():
                        session.run(
                            "MATCH (i:Item {id: $id}) SET i[$key] = $value",
                            id=item_id,
                            key=key,
                            value=str(value)
                        )
        
        return item
    
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.
        
        Args:
            item_id: The ID of the item to remove.
            
        Returns:
            True if the item was removed, False otherwise.
        """
        # Remove the item from the dictionary
        if not super().remove(item_id):
            return False
        
        # Remove the item from the Neo4j database
        with self.driver.session() as session:
            # Remove all nodes and edges
            session.run(
                """
                MATCH (i:Item {id: $id})-[:CONTAINS]->(n:Node)
                DETACH DELETE n
                """,
                id=item_id
            )
            
            # Remove the item
            session.run(
                "MATCH (i:Item {id: $id}) DELETE i",
                id=item_id
            )
        
        return True
    
    def clear(self) -> None:
        """Remove all items from memory."""
        super().clear()
        
        # Clear the Neo4j database
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def add_node(self, item_id: str, node: Node) -> Optional[str]:
        """
        Add a node to a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            node: The node to add.
            
        Returns:
            The ID of the added node, or None if the memory item doesn't exist.
        """
        # Add the node to the item
        node_id = super().add_node(item_id, node)
        
        # If the node was added, add it to the Neo4j database
        if node_id is not None:
            self._add_node_to_neo4j(item_id, node)
        
        return node_id
    
    def update_node(self, item_id: str, node_id: str, labels: Optional[List[str]] = None, properties: Optional[Dict[str, Any]] = None) -> Optional[Node]:
        """
        Update a node in a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            node_id: The ID of the node.
            labels: New labels for the node.
            properties: New properties for the node.
            
        Returns:
            The updated node, or None if the memory item or node doesn't exist.
        """
        # Update the node in the item
        node = super().update_node(item_id, node_id, labels, properties)
        
        # If the node was updated, update it in the Neo4j database
        if node is not None:
            with self.driver.session() as session:
                # Update the node
                query = "MATCH (n:Node {id: $id}) SET n.updated_at = $updated_at"
                
                # Update labels
                if labels is not None:
                    # Remove all labels except "Node"
                    session.run(
                        """
                        MATCH (n:Node {id: $id})
                        CALL apoc.refactor.removeLabels(n, [l IN labels(n) WHERE l <> 'Node' | l]) YIELD node
                        RETURN node
                        """,
                        id=node_id
                    )
                    
                    # Add new labels
                    for label in labels:
                        query += f" SET n:`{label}`"
                
                # Update properties
                if properties is not None:
                    for key, value in properties.items():
                        query += f" SET n.`{key}` = ${key}"
                
                # Execute the query
                params = {
                    "id": node_id,
                    "updated_at": node.updated_at,
                    **{key: str(value) for key, value in (properties or {}).items()}
                }
                
                session.run(query, **params)
        
        return node
    
    def remove_node(self, item_id: str, node_id: str) -> bool:
        """
        Remove a node from a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            node_id: The ID of the node.
            
        Returns:
            True if the node was removed, False otherwise.
        """
        # Remove the node from the item
        if not super().remove_node(item_id, node_id):
            return False
        
        # Remove the node from the Neo4j database
        with self.driver.session() as session:
            session.run(
                "MATCH (n:Node {id: $id}) DETACH DELETE n",
                id=node_id
            )
        
        return True
    
    def add_edge(self, item_id: str, edge: Edge) -> Optional[str]:
        """
        Add an edge to a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            edge: The edge to add.
            
        Returns:
            The ID of the added edge, or None if the memory item doesn't exist.
        """
        # Add the edge to the item
        edge_id = super().add_edge(item_id, edge)
        
        # If the edge was added, add it to the Neo4j database
        if edge_id is not None:
            self._add_edge_to_neo4j(item_id, edge)
        
        return edge_id
    
    def update_edge(self, item_id: str, edge_id: str, relationship: Optional[Union[Relationship, str]] = None, properties: Optional[Dict[str, Any]] = None) -> Optional[Edge]:
        """
        Update an edge in a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            edge_id: The ID of the edge.
            relationship: New relationship type for the edge.
            properties: New properties for the edge.
            
        Returns:
            The updated edge, or None if the memory item or edge doesn't exist.
        """
        # Update the edge in the item
        edge = super().update_edge(item_id, edge_id, relationship, properties)
        
        # If the edge was updated, update it in the Neo4j database
        if edge is not None:
            with self.driver.session() as session:
                # Update the edge
                query = "MATCH ()-[r:EDGE {id: $id}]->() SET r.updated_at = $updated_at"
                
                # Update relationship type
                if relationship is not None:
                    relationship_type = relationship.name if isinstance(relationship, Relationship) else relationship
                    query += ", r.type = $type"
                
                # Update properties
                if properties is not None:
                    for key, value in properties.items():
                        query += f" SET r.`{key}` = ${key}"
                
                # Execute the query
                params = {
                    "id": edge_id,
                    "updated_at": edge.updated_at,
                    "type": relationship_type if relationship is not None else None,
                    **{key: str(value) for key, value in (properties or {}).items()}
                }
                
                session.run(query, **params)
        
        return edge
    
    def remove_edge(self, item_id: str, edge_id: str) -> bool:
        """
        Remove an edge from a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            edge_id: The ID of the edge.
            
        Returns:
            True if the edge was removed, False otherwise.
        """
        # Remove the edge from the item
        if not super().remove_edge(item_id, edge_id):
            return False
        
        # Remove the edge from the Neo4j database
        with self.driver.session() as session:
            session.run(
                "MATCH ()-[r:EDGE {id: $id}]->() DELETE r",
                id=edge_id
            )
        
        return True
    
    def search(self, query: Any, limit: int = 10) -> List[GraphMemoryItem]:
        """
        Search for items in memory.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query.
        """
        # If the query is a string, use Neo4j's full-text search
        if isinstance(query, str):
            with self.driver.session() as session:
                # Search for nodes with matching properties
                result = session.run(
                    """
                    MATCH (i:Item)-[:CONTAINS]->(n:Node)
                    WHERE any(key IN keys(n) WHERE n[key] CONTAINS $query)
                    RETURN DISTINCT i.id AS item_id
                    LIMIT $limit
                    """,
                    query=query,
                    limit=limit
                )
                
                # Load the matching items
                items = []
                for record in result:
                    item_id = record["item_id"]
                    item = self.get(item_id)
                    if item is not None:
                        items.append(item)
                
                return items
        
        # If the query is a dictionary, use Neo4j's property matching
        elif isinstance(query, dict):
            with self.driver.session() as session:
                # Build the query
                cypher_query = "MATCH (i:Item)-[:CONTAINS]->(n:Node) WHERE "
                conditions = []
                params = {}
                
                for i, (key, value) in enumerate(query.items()):
                    conditions.append(f"n.`{key}` = $value{i}")
                    params[f"value{i}"] = str(value)
                
                cypher_query += " AND ".join(conditions)
                cypher_query += " RETURN DISTINCT i.id AS item_id LIMIT $limit"
                params["limit"] = limit
                
                # Execute the query
                result = session.run(cypher_query, **params)
                
                # Load the matching items
                items = []
                for record in result:
                    item_id = record["item_id"]
                    item = self.get(item_id)
                    if item is not None:
                        items.append(item)
                
                return items
        
        # Otherwise, use the default search
        return super().search(query, limit)
    
    def close(self) -> None:
        """Close the Neo4j driver."""
        self.driver.close()
    
    def __del__(self) -> None:
        """Close the Neo4j driver when the object is deleted."""
        try:
            self.close()
        except:
            pass
