# Augment Adam Examples

This directory contains examples demonstrating how to use Augment Adam.

## Getting Started

### Quick Start

The quickstart example demonstrates basic usage of Augment Adam:

```bash
python -m examples.quickstart
```

This example shows how to create a simple assistant with memory capabilities.

### Minimal Example

The minimal example demonstrates a simple agent without external dependencies:

```bash
python -m examples.minimal_example
```

This example provides a simple interactive chat with a mock agent that can respond to basic queries about the agent framework.

### Agent Examples

These examples demonstrate the full agent framework capabilities:

```bash
# Basic agent with system prompt
python -m examples.simple_agent_example

# Asynchronous worker agent
python -m examples.worker_agent_example

# Agent coordination
python -m examples.agent_coordination_example

# MCP server
python -m examples.mcp_server_example
```

Note: These examples require additional dependencies:

```bash
pip install anthropic openai transformers torch
```

## Dependency Management

Augment Adam is designed to work with a variety of model providers. The core functionality works without external dependencies, but for full functionality, you may need to install additional packages:

- **Anthropic Models**: `pip install anthropic`
- **OpenAI Models**: `pip install openai`
- **Hugging Face Models**: `pip install transformers torch`
- **Ollama Models**: No additional dependencies (uses HTTP API)

The framework will automatically detect available dependencies and adjust functionality accordingly.

## Example Descriptions

### quickstart.py

A simple example showing how to create an assistant with memory capabilities.

### memory_integration.py

Demonstrates how to use and integrate different memory types (FAISS, Episodic, Semantic, Working).

### agent_coordination.py

Shows how to coordinate multiple specialized agents (Researcher, Coder, Creator) to work together on complex tasks.

### simple_agent_example.py

Demonstrates how to create a basic agent with a system prompt and output instructions.

### worker_agent_example.py

Shows how to create an asynchronous worker agent that processes tasks in the background.

### agent_coordination_example.py

Illustrates how to coordinate multiple specialized agents to work together on complex tasks.

### mcp_server_example.py

Demonstrates how to deploy agents as MCP servers using FastAPI.

### minimal_example.py

A minimal working example that doesn't require any external dependencies.

## Hardware Optimization

To see how Augment Adam optimizes for your hardware:

```bash
python -m examples.hardware_optimization
```

This will analyze your system and recommend optimal settings for different model types.

## Next Steps

After exploring these examples, check out the [documentation](../docs/) for more detailed information on:

- [Building Agents](../docs/guides/building_agents.md)
- [Agent Coordination](../docs/guides/agent_coordination.md)
- [Hardware Optimization](../docs/guides/hardware_optimization.md)
