# Memory System

The Augment Adam memory system provides a sophisticated architecture for managing agent memory, optimized for different model context windows and agent roles.

## Overview

The memory system is designed with the following principles:

1. **Context Window Efficiency**: Maximize the utility of limited context windows
2. **Role-Specific Optimization**: Tailor memory allocation to the agent's specific role
3. **Model Compatibility**: Work with different models and their varying context window sizes
4. **Memory Persistence**: Maintain knowledge across interactions
5. **Intelligent Retrieval**: Retrieve the most relevant information for each query

## Architecture

The memory system consists of multiple layers, each serving a specific purpose:

### Working Memory (Short-Term)

Working memory holds the immediate conversation context and recent interactions. It has the highest priority in context window allocation.

```python
from augment_adam.ai_agent.memory_integration import ContextMemory

# Create working memory
working_memory = ContextMemory(
    name="agent_working_memory",
    max_size=20  # Store up to 20 items
)

# Add items
working_memory.add("User asked about quantum computing")
working_memory.add("Agent explained quantum bits")

# Retrieve items
recent_items = working_memory.get(3)  # Get last 3 items
```

### Episodic Memory (Medium-Term)

Episodic memory stores complete interaction episodes that can be retrieved by similarity search. It provides historical context for recurring topics.

```python
from augment_adam.ai_agent.memory_integration import EpisodicMemory

# Create episodic memory
episodic_memory = EpisodicMemory(
    name="agent_episodic_memory",
    max_size=100  # Store up to 100 episodes
)

# Add an episode
episode = episodic_memory.add_episode(
    content="User: What is quantum computing?\nAgent: Quantum computing uses qubits...",
    title="Quantum Computing Discussion",
    metadata={"topic": "quantum computing", "sentiment": "curious"}
)

# Search for relevant episodes
results = episodic_memory.search_episodes(
    query="quantum entanglement",
    n_results=3
)
```

### Semantic Memory (Long-Term)

Semantic memory stores concepts, facts, and knowledge organized by topic and relevance. It provides background knowledge for reasoning.

```python
from augment_adam.ai_agent.memory_integration import SemanticMemory

# Create semantic memory
semantic_memory = SemanticMemory(
    name="agent_semantic_memory",
    max_size=500  # Store up to 500 concepts
)

# Add a concept
concept = semantic_memory.add_concept(
    name="Quantum Computing",
    description="A type of computing that uses quantum bits or qubits",
    content="Quantum computing is a type of computing that uses quantum-mechanical phenomena...",
    metadata={"field": "computer science", "subfield": "quantum information"}
)

# Search for relevant concepts
results = semantic_memory.search_concepts(
    query="quantum entanglement",
    n_results=3
)
```

## Memory Configuration

The memory system includes a configuration system that optimizes memory allocation based on the agent's role and the model's context window size.

```python
from augment_adam.ai_agent.memory_integration import get_memory_configuration

# Get memory configuration
memory_config = get_memory_configuration()

# Configure memory for an agent
memory_components = memory_config.configure_memory_for_agent(
    agent_name="research_agent",
    role="researcher",
    model_name="claude-3-sonnet-20240229"
)

# Extract components
memory_manager = memory_components["memory_manager"]
context_window = memory_components["context_window"]
working_memory = memory_components["working_memory"]
episodic_memory = memory_components["episodic_memory"]
semantic_memory = memory_components["semantic_memory"]
token_budgets = memory_components["token_budgets"]
```

## Role-Specific Configurations

The memory system includes predefined configurations for different agent roles:

### Researcher

- Larger semantic memory allocation
- Strong episodic memory for tracking research progress
- Context window optimized for information density

### Coder

- Enhanced procedural memory for code patterns
- Specialized context window for code snippets
- Working memory optimized for debugging flows

### Writer

- Balanced memory allocation
- Strong episodic memory for narrative consistency
- Context window optimized for stylistic elements

### Coordinator

- Enhanced working memory for tracking multiple agents
- Specialized context for agent capabilities and states
- Procedural memory for coordination workflows

## Context Window Management

The memory system intelligently manages the model's context window:

```python
from augment_adam.context_engine import get_context_manager

# Get context manager
context_manager = get_context_manager()

# Create context window
context_window = context_manager.create_context_window(
    name="agent_window",
    max_tokens=8192
)

# Add items to context window
context_window.add_item(context_manager.create_context_item(
    content="User asked about quantum entanglement",
    source="working_memory",
    relevance=0.9
))

# Get content for model prompt
context_content = context_window.get_content()
```

## Integration with Models

The memory system is designed to work with different models and their varying context window sizes:

```python
from augment_adam.models import create_model

# Create a model
model = create_model(
    model_type="anthropic",
    model_name="claude-3-sonnet-20240229"
)

# Get model's context window size
model_info = model.get_model_info()
context_window_size = model_info.get("max_tokens", 8192)

# Configure memory based on model's context window
memory_config = get_memory_configuration()
memory_components = memory_config.configure_memory_for_agent(
    agent_name="agent",
    role="default",
    model_name=model_info["name"]
)
```

## Complete Example

See the [memory integration example](../examples/memory_integration_example.py) for a complete demonstration of how to use the memory system in an agent.

## Best Practices

1. **Configure Memory Based on Role**: Use the appropriate role configuration for your agent's purpose
2. **Consider Model Context Window**: Choose models with appropriate context window sizes for your use case
3. **Balance Memory Types**: Allocate tokens appropriately across different memory types
4. **Update Memory After Interactions**: Keep memory up-to-date with new information
5. **Retrieve Relevant Information**: Use search functions to find the most relevant information for each query
