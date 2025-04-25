"""
Base classes for graph-based memory systems.

This module provides the base classes for graph-based memory systems,
including the GraphMemory base class, GraphMemoryItem class, Node class,
Edge class, and Relationship enum.
"""

import uuid
import json
import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType


class Relationship(Enum):
    """
    Types of relationships in a graph memory.

    This enum defines the types of relationships between nodes in a graph memory.
    """

    IS_A = auto()
    HAS_A = auto()
    PART_OF = auto()
    RELATED_TO = auto()
    DEPENDS_ON = auto()
    CAUSES = auto()
    PRECEDES = auto()
    FOLLOWS = auto()
    SIMILAR_TO = auto()
    OPPOSITE_OF = auto()
    INSTANCE_OF = auto()
    ATTRIBUTE_OF = auto()
    LOCATED_IN = auto()
    OCCURS_AT = auto()
    CREATED_BY = auto()
    USED_BY = auto()
    MEMBER_OF = auto()
    CONTAINS = auto()
    REFERS_TO = auto()
    CUSTOM = auto()


@dataclass
class Node:
    """
    Node in a graph memory.

    This class represents a node in a graph memory, including its ID,
    labels, properties, and other attributes.

    Attributes:
        id: Unique identifier for the node.
        labels: List of labels for the node.
        properties: Dictionary of properties for the node.
        embedding: Vector embedding for the node (if applicable).
        created_at: When the node was created.
        updated_at: When the node was last updated.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    labels: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    def __post_init__(self) -> None:
        """Initialize the node with timestamps."""
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def update(self, labels: Optional[List[str]] = None, properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the node.

        Args:
            labels: New labels for the node.
            properties: New properties for the node.
        """
        if labels is not None:
            self.labels = labels

        if properties is not None:
            self.properties.update(properties)

        self.updated_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary.

        Returns:
            Dictionary representation of the node.
        """
        return {
            "id": self.id,
            "labels": self.labels,
            "properties": self.properties,
            "embedding": self.embedding,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """
        Create a node from a dictionary.

        Args:
            data: Dictionary representation of the node.

        Returns:
            Node.
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            labels=data.get("labels", []),
            properties=data.get("properties", {}),
            embedding=data.get("embedding"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class Edge:
    """
    Edge in a graph memory.

    This class represents an edge in a graph memory, including its ID,
    source node, target node, relationship type, properties, and other attributes.

    Attributes:
        id: Unique identifier for the edge.
        source_id: ID of the source node.
        target_id: ID of the target node.
        relationship: Type of relationship between the nodes.
        properties: Dictionary of properties for the edge.
        created_at: When the edge was created.
        updated_at: When the edge was last updated.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relationship: Union[Relationship, str] = Relationship.RELATED_TO
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    def __post_init__(self) -> None:
        """Initialize the edge with timestamps."""
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

        # Convert string relationship to enum if needed
        if isinstance(self.relationship, str):
            try:
                self.relationship = Relationship[self.relationship]
            except KeyError:
                self.relationship = Relationship.CUSTOM
                self.properties["custom_relationship"] = self.relationship

    def update(self, relationship: Optional[Union[Relationship, str]] = None, properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the edge.

        Args:
            relationship: New relationship type for the edge.
            properties: New properties for the edge.
        """
        if relationship is not None:
            self.relationship = relationship

            # Convert string relationship to enum if needed
            if isinstance(self.relationship, str):
                try:
                    self.relationship = Relationship[self.relationship]
                except KeyError:
                    self.relationship = Relationship.CUSTOM
                    self.properties["custom_relationship"] = relationship

        if properties is not None:
            self.properties.update(properties)

        self.updated_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the edge to a dictionary.

        Returns:
            Dictionary representation of the edge.
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship": self.relationship.name if isinstance(self.relationship, Relationship) else self.relationship,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Edge':
        """
        Create an edge from a dictionary.

        Args:
            data: Dictionary representation of the edge.

        Returns:
            Edge.
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            relationship=data.get("relationship", Relationship.RELATED_TO),
            properties=data.get("properties", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class GraphMemoryItem(MemoryItem):
    """
    Item stored in graph memory.

    This class represents an item stored in graph memory, including its content,
    metadata, nodes, and edges.

    Attributes:
        id: Unique identifier for the memory item.
        content: The content of the memory item.
        metadata: Additional metadata for the memory item.
        created_at: When the memory item was created.
        updated_at: When the memory item was last updated.
        expires_at: When the memory item expires (if applicable).
        importance: Importance score for the memory item (0-1).
        embedding: Vector embedding for the memory item (if applicable).
        nodes: Dictionary of nodes in the graph, keyed by ID.
        edges: Dictionary of edges in the graph, keyed by ID.

    TODO(Issue #6): Add support for memory item versioning
    TODO(Issue #6): Implement memory item validation
    """

    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: Dict[str, Edge] = field(default_factory=dict)

    def add_node(self, node: Node) -> str:
        """
        Add a node to the graph.

        Args:
            node: The node to add.

        Returns:
            The ID of the added node.
        """
        self.nodes[node.id] = node
        return node.id

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node from the graph by ID.

        Args:
            node_id: The ID of the node to get.

        Returns:
            The node, or None if it doesn't exist.
        """
        return self.nodes.get(node_id)

    def update_node(self, node_id: str, labels: Optional[List[str]] = None, properties: Optional[Dict[str, Any]] = None) -> Optional[Node]:
        """
        Update a node in the graph.

        Args:
            node_id: The ID of the node to update.
            labels: New labels for the node.
            properties: New properties for the node.

        Returns:
            The updated node, or None if it doesn't exist.
        """
        node = self.get_node(node_id)
        if node is None:
            return None

        node.update(labels, properties)
        return node

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the graph.

        Args:
            node_id: The ID of the node to remove.

        Returns:
            True if the node was removed, False otherwise.
        """
        if node_id in self.nodes:
            # Remove all edges connected to this node
            edges_to_remove = []
            for edge_id, edge in self.edges.items():
                if edge.source_id == node_id or edge.target_id == node_id:
                    edges_to_remove.append(edge_id)

            for edge_id in edges_to_remove:
                del self.edges[edge_id]

            # Remove the node
            del self.nodes[node_id]
            return True

        return False

    def add_edge(self, edge: Edge) -> str:
        """
        Add an edge to the graph.

        Args:
            edge: The edge to add.

        Returns:
            The ID of the added edge.
        """
        self.edges[edge.id] = edge
        return edge.id

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """
        Get an edge from the graph by ID.

        Args:
            edge_id: The ID of the edge to get.

        Returns:
            The edge, or None if it doesn't exist.
        """
        return self.edges.get(edge_id)

    def update_edge(self, edge_id: str, relationship: Optional[Union[Relationship, str]] = None, properties: Optional[Dict[str, Any]] = None) -> Optional[Edge]:
        """
        Update an edge in the graph.

        Args:
            edge_id: The ID of the edge to update.
            relationship: New relationship type for the edge.
            properties: New properties for the edge.

        Returns:
            The updated edge, or None if it doesn't exist.
        """
        edge = self.get_edge(edge_id)
        if edge is None:
            return None

        edge.update(relationship, properties)
        return edge

    def remove_edge(self, edge_id: str) -> bool:
        """
        Remove an edge from the graph.

        Args:
            edge_id: The ID of the edge to remove.

        Returns:
            True if the edge was removed, False otherwise.
        """
        if edge_id in self.edges:
            del self.edges[edge_id]
            return True

        return False

    def get_neighbors(self, node_id: str) -> List[Node]:
        """
        Get the neighbors of a node.

        Args:
            node_id: The ID of the node.

        Returns:
            List of neighboring nodes.
        """
        neighbors = []

        for edge in self.edges.values():
            if edge.source_id == node_id:
                neighbor = self.get_node(edge.target_id)
                if neighbor is not None:
                    neighbors.append(neighbor)
            elif edge.target_id == node_id:
                neighbor = self.get_node(edge.source_id)
                if neighbor is not None:
                    neighbors.append(neighbor)

        return neighbors

    def get_edges_between(self, node1_id: str, node2_id: str) -> List[Edge]:
        """
        Get the edges between two nodes.

        Args:
            node1_id: The ID of the first node.
            node2_id: The ID of the second node.

        Returns:
            List of edges between the nodes.
        """
        edges = []

        for edge in self.edges.values():
            if (edge.source_id == node1_id and edge.target_id == node2_id) or (edge.source_id == node2_id and edge.target_id == node1_id):
                edges.append(edge)

        return edges

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the graph memory item to a dictionary.

        Returns:
            Dictionary representation of the graph memory item.
        """
        data = super().to_dict()
        data["nodes"] = {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        data["edges"] = {edge_id: edge.to_dict() for edge_id, edge in self.edges.items()}
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphMemoryItem':
        """
        Create a graph memory item from a dictionary.

        Args:
            data: Dictionary representation of the graph memory item.

        Returns:
            Graph memory item.
        """
        item = super().from_dict(data)

        # Add nodes
        for node_data in data.get("nodes", {}).values():
            node = Node.from_dict(node_data)
            item.nodes[node.id] = node

        # Add edges
        for edge_data in data.get("edges", {}).values():
            edge = Edge.from_dict(edge_data)
            item.edges[edge.id] = edge

        return item


T = TypeVar('T', bound=GraphMemoryItem)


@tag("memory.graph")
class GraphMemory(Memory[T]):
    """
    Base class for graph-based memory systems.

    This class defines the interface for graph-based memory systems, including
    methods for adding, retrieving, updating, and removing items from memory,
    as well as methods for graph operations.

    Attributes:
        name: The name of the memory system.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.

    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the graph memory system.

        Args:
            name: The name of the memory system.
        """
        super().__init__(name, MemoryType.GRAPH)

    def add_node(self, item_id: str, node: Node) -> Optional[str]:
        """
        Add a node to a graph memory item.

        Args:
            item_id: The ID of the memory item.
            node: The node to add.

        Returns:
            The ID of the added node, or None if the memory item doesn't exist.
        """
        item = self.get(item_id)
        if item is None:
            return None

        return item.add_node(node)

    def get_node(self, item_id: str, node_id: str) -> Optional[Node]:
        """
        Get a node from a graph memory item.

        Args:
            item_id: The ID of the memory item.
            node_id: The ID of the node.

        Returns:
            The node, or None if the memory item or node doesn't exist.
        """
        item = self.get(item_id)
        if item is None:
            return None

        return item.get_node(node_id)

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
        item = self.get(item_id)
        if item is None:
            return None

        return item.update_node(node_id, labels, properties)

    def remove_node(self, item_id: str, node_id: str) -> bool:
        """
        Remove a node from a graph memory item.

        Args:
            item_id: The ID of the memory item.
            node_id: The ID of the node.

        Returns:
            True if the node was removed, False otherwise.
        """
        item = self.get(item_id)
        if item is None:
            return False

        return item.remove_node(node_id)

    def add_edge(self, item_id: str, edge: Edge) -> Optional[str]:
        """
        Add an edge to a graph memory item.

        Args:
            item_id: The ID of the memory item.
            edge: The edge to add.

        Returns:
            The ID of the added edge, or None if the memory item doesn't exist.
        """
        item = self.get(item_id)
        if item is None:
            return None

        return item.add_edge(edge)

    def get_edge(self, item_id: str, edge_id: str) -> Optional[Edge]:
        """
        Get an edge from a graph memory item.

        Args:
            item_id: The ID of the memory item.
            edge_id: The ID of the edge.

        Returns:
            The edge, or None if the memory item or edge doesn't exist.
        """
        item = self.get(item_id)
        if item is None:
            return None

        return item.get_edge(edge_id)

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
        item = self.get(item_id)
        if item is None:
            return None

        return item.update_edge(edge_id, relationship, properties)

    def remove_edge(self, item_id: str, edge_id: str) -> bool:
        """
        Remove an edge from a graph memory item.

        Args:
            item_id: The ID of the memory item.
            edge_id: The ID of the edge.

        Returns:
            True if the edge was removed, False otherwise.
        """
        item = self.get(item_id)
        if item is None:
            return False

        return item.remove_edge(edge_id)

    def get_neighbors(self, item_id: str, node_id: str) -> List[Node]:
        """
        Get the neighbors of a node in a graph memory item.

        Args:
            item_id: The ID of the memory item.
            node_id: The ID of the node.

        Returns:
            List of neighboring nodes, or an empty list if the memory item or node doesn't exist.
        """
        item = self.get(item_id)
        if item is None:
            return []

        return item.get_neighbors(node_id)

    def get_edges_between(self, item_id: str, node1_id: str, node2_id: str) -> List[Edge]:
        """
        Get the edges between two nodes in a graph memory item.

        Args:
            item_id: The ID of the memory item.
            node1_id: The ID of the first node.
            node2_id: The ID of the second node.

        Returns:
            List of edges between the nodes, or an empty list if the memory item or nodes don't exist.
        """
        item = self.get(item_id)
        if item is None:
            return []

        return item.get_edges_between(node1_id, node2_id)

    def search(self, query: Any, limit: int = 10) -> List[T]:
        """
        Search for items in memory.

        Args:
            query: The query to search for.
            limit: The maximum number of results to return.

        Returns:
            List of items that match the query.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use a more sophisticated search algorithm

        # If the query is a string, search for nodes with matching properties
        if isinstance(query, str):
            results = []

            for item in self.items.values():
                for node in item.nodes.values():
                    # Check if any property value contains the query
                    for value in node.properties.values():
                        if isinstance(value, str) and query.lower() in value.lower():
                            results.append(item)
                            break

                    # If we've already added this item, move on
                    if item in results:
                        break

            return results[:limit]

        # If the query is a dictionary, search for nodes with matching properties
        elif isinstance(query, dict):
            results = []

            for item in self.items.values():
                for node in item.nodes.values():
                    # Check if all query properties match
                    match = True
                    for key, value in query.items():
                        if key not in node.properties or node.properties[key] != value:
                            match = False
                            break

                    if match:
                        results.append(item)
                        break

            return results[:limit]

        # Otherwise, return an empty list
        return []
