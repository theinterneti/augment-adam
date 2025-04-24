# Memory Graph Visualization

This module provides utilities for visualizing the Neo4j memory graph.

## Overview

The memory graph visualization module allows you to:

1. Generate HTML visualizations of the Neo4j memory graph
2. Save visualizations to files
3. Explore the memory graph interactively

## Usage

### Basic Usage

```python
from augment_adam.memory.neo4j_memory import get_neo4j_memory
from augment_adam.memory.visualization import save_memory_graph_visualization

# Initialize the memory system
memory = get_neo4j_memory()

# Save a visualization of the memory graph
output_path = save_memory_graph_visualization(
    output_path="memory_graph.html",
    collection_name=memory.default_collection
)

print(f"Saved visualization to: {output_path}")
```

### Advanced Usage

For more control over the visualization, you can use the `MemoryGraphVisualizer` class:

```python
import asyncio
from augment_adam.memory.neo4j_memory import get_neo4j_memory
from augment_adam.memory.visualization import MemoryGraphVisualizer

async def visualize_graph():
    # Initialize the memory system
    memory = get_neo4j_memory()
    
    # Create a visualizer
    visualizer = MemoryGraphVisualizer(client=memory.client)
    
    # Generate the visualization
    html = await visualizer.generate_visualization(
        center_node_id="mem_123",  # Optional: Center on a specific node
        collection_name=memory.default_collection,
        depth=3,  # Depth of the graph to retrieve
        limit=100  # Maximum number of nodes to retrieve
    )
    
    # Save to a file
    with open("memory_graph.html", "w") as f:
        f.write(html)
    
    print("Saved visualization to: memory_graph.html")

# Run the async function
asyncio.run(visualize_graph())
```

## Example

See the `examples/advanced/memory_graph_visualization.py` script for a complete example.

## Customization

The visualization is generated using Jinja2 templates. You can customize the visualization by modifying the templates in the `templates/memory` directory.
