"""
Graph visualization utilities for the Neo4j memory system.

This module provides utilities for visualizing the Neo4j memory graph.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

from augment_adam.memory.neo4j_client import Neo4jClient, get_neo4j_client
from augment_adam.utils.jinja_utils import render_graph_visualization

logger = logging.getLogger(__name__)


class MemoryGraphVisualizer:
    """
    Visualizer for the Neo4j memory graph.
    
    This class provides methods for visualizing the Neo4j memory graph.
    
    Attributes:
        client: Neo4j client for database operations
    """
    
    def __init__(
        self,
        client: Optional[Neo4jClient] = None
    ):
        """
        Initialize the memory graph visualizer.
        
        Parameters
        ----------
        client : Neo4jClient, optional
            Neo4j client for database operations. If None, uses the default client.
        """
        self.client = client or get_neo4j_client()
    
    async def get_graph_data(
        self,
        center_node_id: Optional[str] = None,
        collection_name: str = "default",
        depth: int = 2,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Get graph data for visualization.
        
        Parameters
        ----------
        center_node_id : str, optional
            ID of the node to center the graph on. If None, returns the entire graph.
        collection_name : str, optional
            Name of the collection to visualize.
        depth : int, optional
            Depth of the graph to retrieve.
        limit : int, optional
            Maximum number of nodes to retrieve.
        
        Returns
        -------
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]
            Tuple of (nodes, edges) for visualization.
        """
        try:
            async with self.client.driver.session() as session:
                if center_node_id:
                    # Get a subgraph centered on the specified node
                    query = f"""
                    MATCH path = (n:Vector:{collection_name} {{id: $id}})-[*1..{depth}]-(related)
                    RETURN path
                    LIMIT {limit}
                    """
                    result = await session.run(query, id=center_node_id)
                else:
                    # Get the entire graph
                    query = f"""
                    MATCH path = (n:Vector:{collection_name})-[r]-(m:Vector:{collection_name})
                    RETURN path
                    LIMIT {limit}
                    """
                    result = await session.run(query)
                
                # Process the results
                nodes = {}
                edges = []
                
                records = await result.values()
                
                for record in records:
                    path = record[0]
                    
                    # Process nodes
                    for node in path.nodes:
                        if node.id not in nodes:
                            # Extract node properties
                            props = dict(node)
                            metadata = json.loads(props.get("metadata", "{}"))
                            
                            # Create node data
                            node_data = {
                                "id": props.get("id", str(node.id)),
                                "label": metadata.get("text", "")[:50] + "..." if len(metadata.get("text", "")) > 50 else metadata.get("text", ""),
                                "metadata": metadata,
                                "group": list(node.labels)[0] if node.labels else "Unknown"
                            }
                            
                            nodes[node.id] = node_data
                    
                    # Process relationships
                    for rel in path.relationships:
                        # Extract relationship properties
                        props = dict(rel)
                        
                        # Create edge data
                        edge_data = {
                            "id": str(rel.id),
                            "from": nodes[rel.start_node.id]["id"],
                            "to": nodes[rel.end_node.id]["id"],
                            "label": rel.type,
                            "arrows": "to",
                            "properties": props
                        }
                        
                        edges.append(edge_data)
                
                return list(nodes.values()), edges
        
        except Exception as e:
            logger.error(f"Failed to get graph data: {str(e)}")
            return [], []
    
    async def generate_visualization(
        self,
        center_node_id: Optional[str] = None,
        collection_name: str = "default",
        depth: int = 2,
        limit: int = 100
    ) -> str:
        """
        Generate HTML visualization of the memory graph.
        
        Parameters
        ----------
        center_node_id : str, optional
            ID of the node to center the graph on. If None, returns the entire graph.
        collection_name : str, optional
            Name of the collection to visualize.
        depth : int, optional
            Depth of the graph to retrieve.
        limit : int, optional
            Maximum number of nodes to retrieve.
        
        Returns
        -------
        str
            HTML visualization of the memory graph.
        """
        # Get graph data
        nodes, edges = await self.get_graph_data(
            center_node_id=center_node_id,
            collection_name=collection_name,
            depth=depth,
            limit=limit
        )
        
        # Define node types for the legend
        node_types = [
            {"label": "Vector", "color": "#97C2FC"},
            {"label": "Memory", "color": "#FB7E81"},
            {"label": "Concept", "color": "#7BE141"},
            {"label": "Entity", "color": "#FFA807"},
            {"label": "Relationship", "color": "#6E6EFD"}
        ]
        
        # Render the visualization
        html = render_graph_visualization(nodes, edges, node_types)
        
        return html
    
    async def save_visualization(
        self,
        output_path: str,
        center_node_id: Optional[str] = None,
        collection_name: str = "default",
        depth: int = 2,
        limit: int = 100
    ) -> str:
        """
        Save HTML visualization of the memory graph to a file.
        
        Parameters
        ----------
        output_path : str
            Path to save the visualization to.
        center_node_id : str, optional
            ID of the node to center the graph on. If None, returns the entire graph.
        collection_name : str, optional
            Name of the collection to visualize.
        depth : int, optional
            Depth of the graph to retrieve.
        limit : int, optional
            Maximum number of nodes to retrieve.
        
        Returns
        -------
        str
            Path to the saved visualization.
        """
        # Generate the visualization
        html = await self.generate_visualization(
            center_node_id=center_node_id,
            collection_name=collection_name,
            depth=depth,
            limit=limit
        )
        
        # Save to file
        with open(output_path, "w") as f:
            f.write(html)
        
        logger.info(f"Saved memory graph visualization to {output_path}")
        
        return output_path


def visualize_memory_graph(
    center_node_id: Optional[str] = None,
    collection_name: str = "default",
    depth: int = 2,
    limit: int = 100,
    client: Optional[Neo4jClient] = None
) -> str:
    """
    Generate HTML visualization of the memory graph.
    
    Parameters
    ----------
    center_node_id : str, optional
        ID of the node to center the graph on. If None, returns the entire graph.
    collection_name : str, optional
        Name of the collection to visualize.
    depth : int, optional
        Depth of the graph to retrieve.
    limit : int, optional
        Maximum number of nodes to retrieve.
    client : Neo4jClient, optional
        Neo4j client for database operations. If None, uses the default client.
    
    Returns
    -------
    str
        HTML visualization of the memory graph.
    """
    visualizer = MemoryGraphVisualizer(client=client)
    return asyncio.run(visualizer.generate_visualization(
        center_node_id=center_node_id,
        collection_name=collection_name,
        depth=depth,
        limit=limit
    ))


def save_memory_graph_visualization(
    output_path: str,
    center_node_id: Optional[str] = None,
    collection_name: str = "default",
    depth: int = 2,
    limit: int = 100,
    client: Optional[Neo4jClient] = None
) -> str:
    """
    Save HTML visualization of the memory graph to a file.
    
    Parameters
    ----------
    output_path : str
        Path to save the visualization to.
    center_node_id : str, optional
        ID of the node to center the graph on. If None, returns the entire graph.
    collection_name : str, optional
        Name of the collection to visualize.
    depth : int, optional
        Depth of the graph to retrieve.
    limit : int, optional
        Maximum number of nodes to retrieve.
    client : Neo4jClient, optional
        Neo4j client for database operations. If None, uses the default client.
    
    Returns
    -------
    str
        Path to the saved visualization.
    """
    visualizer = MemoryGraphVisualizer(client=client)
    return asyncio.run(visualizer.save_visualization(
        output_path=output_path,
        center_node_id=center_node_id,
        collection_name=collection_name,
        depth=depth,
        limit=limit
    ))
