# Augment Adam Examples

This directory contains example scripts demonstrating how to use Augment Adam.

## Directory Structure

- **basic/**: Simple examples to get started with Augment Adam
  - `quickstart.py`: Basic usage of Augment Adam with a simple assistant and memory system
  - `minimal_example.py`: A minimal working example that doesn't require any external dependencies
  - `simple_agent_example.py`: Demonstrates how to create a basic agent with a system prompt and output instructions

- **memory/**: Examples demonstrating memory capabilities
  - `memory_integration.py`: Demonstrates how to use and integrate different memory types
  - `memory_integration_example.py`: Shows how to use different memory systems together

- **agent/**: Examples demonstrating agent capabilities
  - `agent_coordination.py`: Shows how to coordinate multiple specialized agents
  - `agent_coordination_example.py`: Illustrates how to coordinate multiple specialized agents to work together on complex tasks
  - `worker_agent_example.py`: Shows how to create an asynchronous worker agent that processes tasks in the background
  - `agent_core_example.py`: Demonstrates core agent functionality
  - `basic_agent_example.py`: Shows how to create a basic agent

- **web/**: Examples demonstrating web interface capabilities
  - `mcp_server_example.py`: Demonstrates how to deploy agents as MCP servers using FastAPI
  - `simple_mcp_server.py`: A simple MCP server implementation
  - `agent_mcp_example.py`: Shows how to use agents with MCP

- **advanced/**: Advanced examples demonstrating more complex features
  - `async_processing.py`: Demonstrates asynchronous processing capabilities
  - `hardware_optimization.py`: Shows how to optimize for different hardware
  - `model_management_demo.py`: Demonstrates model management features
  - `progress_tracking.py`: Shows how to track progress of long-running tasks

## Running the Examples

To run these examples, make sure you have Augment Adam installed:

```bash
pip install augment-adam
```

Then run any example script:

```bash
python examples/basic/quickstart.py
```

## Creating Your Own Examples

Feel free to modify these examples or create your own. The examples are designed to be simple and easy to understand, while still demonstrating the key features of Augment Adam.

## Contributing

If you create an interesting example that demonstrates a feature or use case not covered by the existing examples, please consider contributing it back to the project. See the [Contributing Guide](../CONTRIBUTING.md) for more information.
