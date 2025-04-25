# Memory Integration Module

This module provides memory integration components for AI agents, enabling them to maintain context, learn from interactions, and provide more coherent responses.

## Components

### MemoryManager

The `MemoryManager` class manages interactions with memory systems:

```python
from augment_adam.ai_agent.memory_integration import MemoryManager

# Create memory manager
memory_manager = MemoryManager(agent_id="agent_123")

# Add memory
memory_id = memory_manager.add(
    text="Important information to remember",
    metadata={"topic": "important_topic"}
)

# Retrieve memories
memories = memory_manager.retrieve(
    query="important information",
    n_results=5
)
```

### ContextMemory

The `ContextMemory` class manages short-term working memory:

```python
from augment_adam.ai_agent.memory_integration import ContextMemory

# Create context memory
context_memory = ContextMemory(
    name="agent_context_memory",
    max_size=20
)

# Add items
context_memory.add("User asked about quantum computing")
context_memory.add("Agent explained quantum bits")

# Get items
items = context_memory.get(5)  # Get last 5 items
```

### EpisodicMemory

The `EpisodicMemory` class manages medium-term episodic memory:

```python
from augment_adam.ai_agent.memory_integration import EpisodicMemory

# Create episodic memory
episodic_memory = EpisodicMemory(
    name="agent_episodic_memory",
    max_size=100
)

# Add episode
episode = episodic_memory.add_episode(
    content="User: What is quantum computing?\nAgent: Quantum computing uses qubits...",
    title="Quantum Computing Discussion",
    metadata={"topic": "quantum computing"}
)

# Search episodes
results = episodic_memory.search_episodes(
    query="quantum entanglement",
    n_results=3
)
```

### SemanticMemory

The `SemanticMemory` class manages long-term semantic memory:

```python
from augment_adam.ai_agent.memory_integration import SemanticMemory

# Create semantic memory
semantic_memory = SemanticMemory(
    name="agent_semantic_memory",
    max_size=500
)

# Add concept
concept = semantic_memory.add_concept(
    name="Quantum Computing",
    description="A type of computing that uses quantum bits or qubits",
    content="Quantum computing is a type of computing that uses quantum-mechanical phenomena...",
    metadata={"field": "computer science"}
)

# Search concepts
results = semantic_memory.search_concepts(
    query="quantum entanglement",
    n_results=3
)
```

### MemoryConfiguration

The `MemoryConfiguration` class manages memory configurations for different agent roles and models:

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

## Integration with Context Engine

The memory integration module works with the context engine to manage context windows:

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
```

## Role-Specific Configurations

The memory system includes predefined configurations for different agent roles:

- **Researcher**: Optimized for information gathering and analysis
- **Coder**: Optimized for code generation and debugging
- **Writer**: Optimized for content creation and narrative consistency
- **Coordinator**: Optimized for managing multiple agents and tasks

## Model Compatibility

The memory system is compatible with various models and their context window sizes:

- Anthropic Claude models (up to 200K tokens)
- OpenAI GPT models (up to 128K tokens)
- Hugging Face models (various sizes)
- Ollama models (various sizes)

## Example Usage

See the [memory integration example](../../../examples/memory_integration_example.py) for a complete demonstration of how to use the memory system in an agent.
