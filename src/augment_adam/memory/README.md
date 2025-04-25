# Advanced Memory System

## Overview

This module provides advanced memory systems for AI agents, including vector-based, graph-based, episodic, semantic, and working memory.

## Components

### Core

The core components of the memory system include:

- **Memory**: Base class for all memory systems
- **MemoryItem**: Base class for items stored in memory
- **MemoryType**: Enum defining the types of memory
- **MemoryManager**: Manager for multiple memory systems

### Vector Memory

Vector memory systems store and retrieve items based on vector embeddings:

- **VectorMemory**: Base class for vector memory systems
- **FAISSMemory**: Vector memory system based on FAISS
- **ChromaMemory**: Vector memory system based on Chroma

### Graph Memory

Graph memory systems store and retrieve items as nodes and edges in a graph:

- **GraphMemory**: Base class for graph memory systems
- **Neo4jMemory**: Graph memory system based on Neo4j
- **NetworkXMemory**: Graph memory system based on NetworkX

### Episodic Memory

Episodic memory systems store and retrieve temporal sequences of events:

- **EpisodicMemory**: Episodic memory system
- **Episode**: Episode in an episodic memory
- **Event**: Event in an episodic memory

### Semantic Memory

Semantic memory systems store and retrieve conceptual knowledge:

- **SemanticMemory**: Semantic memory system
- **Concept**: Concept in a semantic memory
- **Relation**: Relation between concepts in a semantic memory

### Working Memory

Working memory systems provide temporary storage for ongoing tasks:

- **WorkingMemory**: Working memory system
- **WorkingMemoryItem**: Item in a working memory

## Usage

### Creating a Memory System

```python
from augment_adam.memory import FAISSMemory, VectorMemoryItem

# Create a FAISS memory system
memory = FAISSMemory(name="my_memory", dimension=1536)

# Create a memory item
item = VectorMemoryItem(
    content="This is a test item",
    metadata={"source": "user", "type": "text"},
    importance=0.8
)

# Add the item to memory
item_id = memory.add(item)
```

### Retrieving Items from Memory

```python
# Get an item by ID
item = memory.get(item_id)

# Search for items
results = memory.search("test", limit=10)
```

### Using the Memory Manager

```python
from augment_adam.memory import get_memory_manager, FAISSMemory, Neo4jMemory

# Get the memory manager
manager = get_memory_manager()

# Register memory systems
vector_memory = FAISSMemory(name="vector_memory", dimension=1536)
graph_memory = Neo4jMemory(name="graph_memory", uri="bolt://localhost:7687", username="neo4j", password="password")

manager.register_memory(vector_memory)
manager.register_memory(graph_memory)

# Add an item to a memory system
item_id = manager.add_item("vector_memory", item)

# Search for items
results = manager.search("vector_memory", "test", limit=10)
```

### Using Vector Memory

```python
from augment_adam.memory import FAISSMemory, VectorMemoryItem

# Create a FAISS memory system
memory = FAISSMemory(name="vector_memory", dimension=1536)

# Add items
item1 = VectorMemoryItem(content="This is a test item", text="This is a test item")
item2 = VectorMemoryItem(content="Another test item", text="Another test item")

memory.add(item1)
memory.add(item2)

# Search for items
results = memory.search("test", limit=10)
```

### Using Graph Memory

```python
from augment_adam.memory import Neo4jMemory, GraphMemoryItem, Node, Edge, Relationship

# Create a Neo4j memory system
memory = Neo4jMemory(name="graph_memory", uri="bolt://localhost:7687", username="neo4j", password="password")

# Create a graph memory item
item = GraphMemoryItem(content="Graph test")

# Add nodes
node1 = Node(labels=["Person"], properties={"name": "Alice", "age": 30})
node2 = Node(labels=["Person"], properties={"name": "Bob", "age": 25})

node1_id = item.add_node(node1)
node2_id = item.add_node(node2)

# Add an edge
edge = Edge(source_id=node1_id, target_id=node2_id, relationship=Relationship.KNOWS)
item.add_edge(edge)

# Add the item to memory
memory.add(item)

# Get neighbors of a node
neighbors = memory.get_neighbors(item.id, node1_id)
```

### Using Episodic Memory

```python
from augment_adam.memory import EpisodicMemory, Episode, Event

# Create an episodic memory system
memory = EpisodicMemory(name="episodic_memory")

# Create an episode
episode = Episode(content="User conversation")

# Add events
event1 = Event(content="User: Hello", metadata={"speaker": "user"})
event2 = Event(content="AI: Hi there! How can I help you?", metadata={"speaker": "ai"})

episode.add_event(event1)
episode.add_event(event2)

# Add the episode to memory
memory.add(episode)

# Get events in a time range
events = memory.get_events_in_range(episode.id, start_time="2023-01-01T00:00:00", end_time="2023-12-31T23:59:59")
```

### Using Semantic Memory

```python
from augment_adam.memory import SemanticMemory, Concept, RelationType

# Create a semantic memory system
memory = SemanticMemory(name="semantic_memory")

# Create concepts
concept1 = Concept(name="Dog", description="A domesticated carnivorous mammal", examples=["Labrador", "Poodle"])
concept2 = Concept(name="Animal", description="A living organism that feeds on organic matter", examples=["Dog", "Cat"])

# Add concepts to memory
concept1_id = memory.add(concept1)
concept2_id = memory.add(concept2)

# Add a relation between concepts
memory.add_relation(concept1_id, concept2_id, RelationType.IS_A)

# Search for concepts
results = memory.search("dog", limit=10)
```

### Using Working Memory

```python
from augment_adam.memory import WorkingMemory, WorkingMemoryItem

# Create a working memory system with a capacity of 100 items
memory = WorkingMemory(name="working_memory", capacity=100, cleanup_interval=60)

# Add items
item1 = WorkingMemoryItem(content="Current task", task_id="task1", priority=8, ttl=3600)
item2 = WorkingMemoryItem(content="Subtask", task_id="task1", priority=5, ttl=1800)

memory.add(item1)
memory.add(item2)

# Get items by task
task_items = memory.get_by_task("task1")

# Update item status
memory.update_status(item1.id, "completed")
```

## TODOs

- Add memory persistence support (Issue #6)
- Implement memory validation against a schema (Issue #6)
- Add memory analytics to track usage and performance (Issue #6)
- Add support for memory item versioning (Issue #6)
- Implement memory item validation (Issue #6)
