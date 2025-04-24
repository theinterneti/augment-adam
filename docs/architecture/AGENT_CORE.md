# Agent Core

The Agent Core is a flexible AI agent architecture with model management, memory integration, and reasoning capabilities. It leverages the Context Engine for efficient context management and uses Sequential Monte Carlo (SMC) for controlled generation.

## Overview

The Agent Core provides a modular and extensible framework for building AI agents with different capabilities. It includes:

- **Base Agent**: A foundation for all agent types with core functionality
- **Specialized Agents**: Conversational, Task, Research, Creative, and Coding agents
- **Memory Integration**: Agent-specific memory with global memory access
- **Reasoning Components**: Chain of thought, reflection, planning, and more
- **Sequential Monte Carlo**: Controlled generation with syntactic and semantic constraints

## Sequential Monte Carlo (SMC)

The Agent Core uses Sequential Monte Carlo for controlled generation from language models. This approach allows for:

- **Controlled Generation**: Generate text under syntactic/semantic constraints
- **Potential Functions**: Non-negative scores for token sequences
- **Product of Experts**: Combine LLM base distribution with constraint potentials
- **Constraint Types**: Efficient (checked incrementally) and Expensive (checked less frequently)
- **Particle-Based Sampling**: Incrementally extend, reweight, and resample particles

## Components

### Agent Interface

The `AgentInterface` defines the core methods that all agents must implement:

- `process`: Process input and generate a response
- `generate`: Generate text based on a prompt
- `remember`: Store information in memory
- `retrieve`: Retrieve information from memory
- `reason`: Perform reasoning on a query

### Base Agent

The `BaseAgent` provides a base implementation of the Agent interface with:

- Context management using the Context Engine
- Memory management for agent-specific memory
- Reasoning capabilities with chain of thought
- Sequential Monte Carlo for controlled generation

### Agent Types

The Agent Core includes several specialized agent types:

- `ConversationalAgent`: For general conversation
- `TaskAgent`: For task-focused interactions
- `ResearchAgent`: For research-focused interactions
- `CreativeAgent`: For creative tasks
- `CodingAgent`: For code generation

### Memory Integration

The Agent Core integrates with memory systems through:

- `MemoryManager`: Manages agent-specific memory
- `ContextMemory`: Short-term context memory
- `EpisodicMemory`: Long-term episodic memory
- `SemanticMemory`: Long-term semantic memory

### Reasoning Components

The Agent Core includes several reasoning components:

- `ChainOfThought`: For structured reasoning
- `Reflection`: For self-reflection
- `Planning`: For task planning
- `DecisionMaking`: For decision making
- `KnowledgeGraph`: For knowledge graph reasoning

### Sequential Monte Carlo Components

The Agent Core includes several SMC components:

- `Particle`: Represents a partial sequence in SMC
- `Potential`: Base class for potential functions
- `GrammarPotential`: For grammar constraints
- `SemanticPotential`: For semantic constraints
- `RegexPotential`: For regex constraints
- `SequentialMonteCarlo`: The SMC sampler

## Usage

```python
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential

# Create a potential for proper sentence endings
sentence_ending_potential = RegexPotential(
    pattern=r".*[.!?]$",
    name="sentence_ending_potential"
)

# Create a conversational agent
agent = create_agent(
    agent_type="conversational",
    name="My Agent",
    description="A conversational agent",
    potentials=[sentence_ending_potential],
    num_particles=100
)

# Process input
result = agent.process("Hello, how are you?")
print(result["response"])
```

## Integration with Context Engine

The Agent Core integrates with the Context Engine for efficient context management:

```python
from augment_adam.context_engine import get_context_manager
from augment_adam.context_engine.retrieval import MemoryRetriever, WebRetriever
from augment_adam.ai_agent import create_agent

# Get the context manager
context_manager = get_context_manager()

# Register retrievers
context_manager.register_retriever("memory", MemoryRetriever())
context_manager.register_retriever("web", WebRetriever())

# Create an agent
agent = create_agent(agent_type="research")

# Process input (will use the context manager)
result = agent.process("Tell me about quantum computing")
```

## Examples

See the `examples/agent_core_example.py` file for a complete example of using the Agent Core with the Context Engine.
