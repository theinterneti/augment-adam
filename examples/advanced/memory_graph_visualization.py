#!/usr/bin/env python3
"""
Example script for visualizing the Neo4j memory graph.

This script demonstrates how to use the Neo4j memory graph visualization utilities.
"""

import os
import asyncio
import argparse
import webbrowser
from pathlib import Path

from augment_adam.memory.neo4j_memory import Neo4jMemory, get_neo4j_memory
from augment_adam.memory.visualization import (
    MemoryGraphVisualizer,
    save_memory_graph_visualization
)


async def populate_memory_graph(memory: Neo4jMemory, num_memories: int = 10):
    """
    Populate the memory graph with sample data.
    
    Parameters
    ----------
    memory : Neo4jMemory
        Neo4j memory instance
    num_memories : int, optional
        Number of memories to create
    """
    print(f"Populating memory graph with {num_memories} memories...")
    
    # Add some memories
    memory_ids = []
    for i in range(num_memories):
        memory_id = memory.add(
            text=f"This is memory {i}",
            metadata={"type": "memory", "index": i},
            id_prefix="mem"
        )
        memory_ids.append(memory_id)
        print(f"Added memory: {memory_id}")
    
    # Create some relationships
    for i in range(len(memory_ids) - 1):
        await memory.client.create_relationship(
            from_id=memory_ids[i],
            to_id=memory_ids[i + 1],
            relationship_type="NEXT",
            properties={"index": i}
        )
        print(f"Created relationship: {memory_ids[i]} -> {memory_ids[i + 1]}")
    
    # Create a circular relationship
    await memory.client.create_relationship(
        from_id=memory_ids[-1],
        to_id=memory_ids[0],
        relationship_type="NEXT",
        properties={"index": len(memory_ids) - 1}
    )
    print(f"Created relationship: {memory_ids[-1]} -> {memory_ids[0]}")
    
    # Create some random relationships
    import random
    for _ in range(5):
        from_idx = random.randint(0, len(memory_ids) - 1)
        to_idx = random.randint(0, len(memory_ids) - 1)
        if from_idx != to_idx:
            await memory.client.create_relationship(
                from_id=memory_ids[from_idx],
                to_id=memory_ids[to_idx],
                relationship_type="RELATED",
                properties={"strength": random.random()}
            )
            print(f"Created relationship: {memory_ids[from_idx]} -> {memory_ids[to_idx]}")
    
    return memory_ids


async def visualize_graph(memory: Neo4jMemory, center_node_id: str = None, output_path: str = None):
    """
    Visualize the memory graph.
    
    Parameters
    ----------
    memory : Neo4jMemory
        Neo4j memory instance
    center_node_id : str, optional
        ID of the node to center the graph on
    output_path : str, optional
        Path to save the visualization to
    """
    # Create a visualizer
    visualizer = MemoryGraphVisualizer(client=memory.client)
    
    # Generate the visualization
    if output_path:
        output_path = await visualizer.save_visualization(
            output_path=output_path,
            center_node_id=center_node_id,
            collection_name=memory.default_collection,
            depth=3,
            limit=100
        )
        print(f"Saved visualization to: {output_path}")
        
        # Open the visualization in a web browser
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
    else:
        html = await visualizer.generate_visualization(
            center_node_id=center_node_id,
            collection_name=memory.default_collection,
            depth=3,
            limit=100
        )
        print(f"Generated visualization ({len(html)} bytes)")
        
        # Save to a temporary file and open in a web browser
        temp_path = os.path.join(os.path.dirname(__file__), "memory_graph.html")
        with open(temp_path, "w") as f:
            f.write(html)
        
        print(f"Saved visualization to: {temp_path}")
        webbrowser.open(f"file://{os.path.abspath(temp_path)}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Visualize the Neo4j memory graph")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="password", help="Neo4j password")
    parser.add_argument("--collection", default="example_memory", help="Memory collection name")
    parser.add_argument("--num-memories", type=int, default=10, help="Number of memories to create")
    parser.add_argument("--center-node", help="ID of the node to center the graph on")
    parser.add_argument("--output", help="Path to save the visualization to")
    parser.add_argument("--clear", action="store_true", help="Clear the memory collection before populating")
    
    args = parser.parse_args()
    
    # Initialize the memory system
    memory = get_neo4j_memory(
        neo4j_uri=args.uri,
        neo4j_user=args.user,
        neo4j_password=args.password,
        collection_name=args.collection
    )
    
    # Create the vector index
    await memory.client.create_index(collection_name=args.collection)
    
    # Clear the memory collection if requested
    if args.clear:
        await memory.client.clear(collection_name=args.collection)
        print(f"Cleared memory collection: {args.collection}")
    
    # Populate the memory graph
    memory_ids = await populate_memory_graph(memory, args.num_memories)
    
    # Visualize the graph
    center_node_id = args.center_node or memory_ids[0] if memory_ids else None
    await visualize_graph(memory, center_node_id, args.output)


if __name__ == "__main__":
    asyncio.run(main())
