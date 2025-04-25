"""
NetworkX-based graph memory system.

This module provides a graph memory system based on NetworkX,
which is a Python package for the creation, manipulation, and study of complex networks.
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, cast
import networkx as nx

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.graph.base import GraphMemory, GraphMemoryItem, Node, Edge, Relationship


@tag("memory.graph.networkx")
class NetworkXMemory(GraphMemory[GraphMemoryItem]):
    """
    NetworkX-based graph memory system.
    
    This class implements a graph memory system using NetworkX for efficient
    in-memory storage and manipulation of graph data.
    
    Attributes:
        name: The name of the memory system.
        graphs: Dictionary of NetworkX graphs, keyed by item ID.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the NetworkX memory system.
        
        Args:
            name: The name of the memory system.
        """
        super().__init__(name)
        
        self.graphs: Dict[str, nx.MultiDiGraph] = {}
    
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
        
        # Create a NetworkX graph for the item
        graph = nx.MultiDiGraph()
        
        # Add nodes
        for node in item.nodes.values():
            graph.add_node(
                node.id,
                labels=node.labels,
                properties=node.properties,
                embedding=node.embedding,
                created_at=node.created_at,
                updated_at=node.updated_at
            )
        
        # Add edges
        for edge in item.edges.values():
            graph.add_edge(
                edge.source_id,
                edge.target_id,
                key=edge.id,
                id=edge.id,
                relationship=edge.relationship,
                properties=edge.properties,
                created_at=edge.created_at,
                updated_at=edge.updated_at
            )
        
        # Store the graph
        self.graphs[item.id] = graph
        
        return item.id
    
    def get(self, item_id: str) -> Optional[GraphMemoryItem]:
        """
        Get an item from memory by ID.
        
        Args:
            item_id: The ID of the item to get.
            
        Returns:
            The item, or None if it doesn't exist.
        """
        return super().get(item_id)
    
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
        return super().update(item_id, content, metadata)
    
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
        
        # Remove the graph
        if item_id in self.graphs:
            del self.graphs[item_id]
        
        return True
    
    def clear(self) -> None:
        """Remove all items from memory."""
        super().clear()
        
        # Clear the graphs
        self.graphs = {}
    
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
        
        # If the node was added, add it to the graph
        if node_id is not None and item_id in self.graphs:
            self.graphs[item_id].add_node(
                node.id,
                labels=node.labels,
                properties=node.properties,
                embedding=node.embedding,
                created_at=node.created_at,
                updated_at=node.updated_at
            )
        
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
        
        # If the node was updated, update it in the graph
        if node is not None and item_id in self.graphs and node_id in self.graphs[item_id]:
            if labels is not None:
                self.graphs[item_id].nodes[node_id]["labels"] = labels
            
            if properties is not None:
                self.graphs[item_id].nodes[node_id]["properties"].update(properties)
            
            self.graphs[item_id].nodes[node_id]["updated_at"] = node.updated_at
        
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
        
        # Remove the node from the graph
        if item_id in self.graphs and node_id in self.graphs[item_id]:
            self.graphs[item_id].remove_node(node_id)
        
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
        
        # If the edge was added, add it to the graph
        if edge_id is not None and item_id in self.graphs:
            self.graphs[item_id].add_edge(
                edge.source_id,
                edge.target_id,
                key=edge.id,
                id=edge.id,
                relationship=edge.relationship,
                properties=edge.properties,
                created_at=edge.created_at,
                updated_at=edge.updated_at
            )
        
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
        
        # If the edge was updated, update it in the graph
        if edge is not None and item_id in self.graphs:
            # Find the edge in the graph
            for u, v, k, data in self.graphs[item_id].edges(keys=True, data=True):
                if data.get("id") == edge_id:
                    if relationship is not None:
                        self.graphs[item_id][u][v][k]["relationship"] = relationship
                    
                    if properties is not None:
                        self.graphs[item_id][u][v][k]["properties"].update(properties)
                    
                    self.graphs[item_id][u][v][k]["updated_at"] = edge.updated_at
                    break
        
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
        
        # Remove the edge from the graph
        if item_id in self.graphs:
            # Find the edge in the graph
            for u, v, k, data in self.graphs[item_id].edges(keys=True, data=True):
                if data.get("id") == edge_id:
                    self.graphs[item_id].remove_edge(u, v, k)
                    break
        
        return True
    
    def get_neighbors(self, item_id: str, node_id: str) -> List[Node]:
        """
        Get the neighbors of a node in a graph memory item.
        
        Args:
            item_id: The ID of the memory item.
            node_id: The ID of the node.
            
        Returns:
            List of neighboring nodes, or an empty list if the memory item or node doesn't exist.
        """
        # If the graph exists, use NetworkX to get the neighbors
        if item_id in self.graphs and node_id in self.graphs[item_id]:
            item = self.get(item_id)
            if item is None:
                return []
            
            neighbors = []
            
            # Get successors (outgoing edges)
            for neighbor_id in self.graphs[item_id].successors(node_id):
                neighbor = item.get_node(neighbor_id)
                if neighbor is not None:
                    neighbors.append(neighbor)
            
            # Get predecessors (incoming edges)
            for neighbor_id in self.graphs[item_id].predecessors(node_id):
                neighbor = item.get_node(neighbor_id)
                if neighbor is not None and neighbor not in neighbors:
                    neighbors.append(neighbor)
            
            return neighbors
        
        # Otherwise, use the default implementation
        return super().get_neighbors(item_id, node_id)
    
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
        # If the graph exists, use NetworkX to get the edges
        if item_id in self.graphs and node1_id in self.graphs[item_id] and node2_id in self.graphs[item_id]:
            item = self.get(item_id)
            if item is None:
                return []
            
            edges = []
            
            # Get edges from node1 to node2
            if self.graphs[item_id].has_edge(node1_id, node2_id):
                for k, data in self.graphs[item_id][node1_id][node2_id].items():
                    edge_id = data.get("id")
                    edge = item.get_edge(edge_id)
                    if edge is not None:
                        edges.append(edge)
            
            # Get edges from node2 to node1
            if self.graphs[item_id].has_edge(node2_id, node1_id):
                for k, data in self.graphs[item_id][node2_id][node1_id].items():
                    edge_id = data.get("id")
                    edge = item.get_edge(edge_id)
                    if edge is not None:
                        edges.append(edge)
            
            return edges
        
        # Otherwise, use the default implementation
        return super().get_edges_between(item_id, node1_id, node2_id)
    
    def search(self, query: Any, limit: int = 10) -> List[GraphMemoryItem]:
        """
        Search for items in memory.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query.
        """
        # If the query is a string, search for nodes with matching properties
        if isinstance(query, str):
            results = []
            
            for item_id, graph in self.graphs.items():
                for node_id, data in graph.nodes(data=True):
                    # Check if any property value contains the query
                    properties = data.get("properties", {})
                    for value in properties.values():
                        if isinstance(value, str) and query.lower() in value.lower():
                            item = self.get(item_id)
                            if item is not None and item not in results:
                                results.append(item)
                                break
                    
                    # If we've already added this item, move on
                    if len(results) > 0 and results[-1].id == item_id:
                        break
            
            return results[:limit]
        
        # If the query is a dictionary, search for nodes with matching properties
        elif isinstance(query, dict):
            results = []
            
            for item_id, graph in self.graphs.items():
                for node_id, data in graph.nodes(data=True):
                    # Check if all query properties match
                    properties = data.get("properties", {})
                    match = True
                    for key, value in query.items():
                        if key not in properties or properties[key] != value:
                            match = False
                            break
                    
                    if match:
                        item = self.get(item_id)
                        if item is not None and item not in results:
                            results.append(item)
                            break
            
            return results[:limit]
        
        # Otherwise, use the default implementation
        return super().search(query, limit)
    
    def save(self, directory: str) -> None:
        """
        Save the memory system to disk.
        
        Args:
            directory: The directory to save the memory system to.
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save the items
        items_data = {item_id: item.to_dict() for item_id, item in self.items.items()}
        with open(os.path.join(directory, "items.json"), "w") as f:
            json.dump(items_data, f)
        
        # Save the graphs
        for item_id, graph in self.graphs.items():
            # Convert the graph to a dictionary
            graph_data = nx.node_link_data(graph)
            
            # Save the graph
            with open(os.path.join(directory, f"{item_id}.json"), "w") as f:
                json.dump(graph_data, f)
        
        # Save the metadata
        with open(os.path.join(directory, "metadata.json"), "w") as f:
            json.dump({
                "name": self.name,
                "memory_type": self.memory_type.name,
                "metadata": self.metadata,
            }, f)
    
    @classmethod
    def load(cls, directory: str) -> 'NetworkXMemory':
        """
        Load a memory system from disk.
        
        Args:
            directory: The directory to load the memory system from.
            
        Returns:
            The loaded memory system.
        """
        # Load the metadata
        with open(os.path.join(directory, "metadata.json"), "r") as f:
            metadata_data = json.load(f)
        
        # Create the memory system
        memory = cls(name=metadata_data.get("name", ""))
        memory.metadata = metadata_data.get("metadata", {})
        
        # Load the items
        with open(os.path.join(directory, "items.json"), "r") as f:
            items_data = json.load(f)
        
        for item_data in items_data.values():
            item = GraphMemoryItem.from_dict(item_data)
            memory.items[item.id] = item
        
        # Load the graphs
        for item_id in memory.items:
            graph_path = os.path.join(directory, f"{item_id}.json")
            if os.path.exists(graph_path):
                with open(graph_path, "r") as f:
                    graph_data = json.load(f)
                
                # Convert the dictionary to a graph
                graph = nx.node_link_graph(graph_data, directed=True, multigraph=True)
                
                memory.graphs[item_id] = graph
        
        return memory
