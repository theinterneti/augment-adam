# Quickstart Guide for Augment Adam

This guide will help you quickly get started with Augment Adam, an intelligent assistant with advanced memory capabilities.

## Installation

You can install Augment Adam using pip:

```bash
pip install augment-adam
```

For development, you can install from source:

```bash
git clone https://github.com/augment-adam/augment-adam.git
cd augment-adam
pip install -e ".[dev]"
```

## Basic Usage

Here's a simple example of using Augment Adam:

```python
from augment_adam.core import Agent
from augment_adam.memory import FAISSMemory

# Create a memory system
memory = FAISSMemory()

# Create an agent with the memory system
agent = Agent(memory=memory)

# Run the agent
response = agent.run("What can you tell me about quantum computing?")
print(response)
```

## Using the CLI

Augment Adam comes with a command-line interface for easy interaction:

```bash
# Start a chat session
augment-adam chat

# Specify a model
augment-adam chat --model gpt-3.5-turbo

# Specify a memory system
augment-adam chat --memory-type neo4j
```

## Next Steps

- Learn about [Memory Systems](memory_systems.md)
- Explore [Agent Coordination](agent_coordination.md)
- Check out the [API Reference](../api/index.md)
- Try the [Examples](../../examples/README.md)
