# Augment Adam

An intelligent assistant with advanced memory capabilities and agent coordination.

## Overview

Augment Adam is an AI assistant framework that uses advanced memory systems and agent coordination to provide more contextual and personalized responses. It's designed to be modular, extensible, and optimized for current hardware.

### Key Features

- **Advanced Memory Systems**: FAISS-based vector memory, Neo4j graph memory, and more
- **Agent Coordination**: Coordinate multiple specialized agents to solve complex tasks
- **Monte Carlo Techniques**: Optimize smaller models with advanced context/memory techniques
- **Context Engine**: Efficiently manage memory access and context windows
- **FastAPI-MCP Integration**: Package everything via FastAPI-MCP for client use

## Installation

```bash
# Install from PyPI
pip install augment-adam

# Install with Neo4j support
pip install augment-adam[neo4j]

# Install development dependencies
pip install augment-adam[dev]
```

## Quick Start

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

## Documentation

For more detailed information, check out our documentation:

- [User Guide](https://augment-adam.readthedocs.io/en/latest/user_guide/)
- [API Reference](https://augment-adam.readthedocs.io/en/latest/api/)
- [Examples](https://augment-adam.readthedocs.io/en/latest/examples/)
- [Research](https://augment-adam.readthedocs.io/en/latest/research/)

## Development

### Setup Development Environment

The recommended way to set up the development environment is to use the VS Code devcontainer, which provides a consistent environment with all dependencies pre-installed.

#### Using VS Code Devcontainer (Recommended)

1. Prerequisites:

   - [Visual Studio Code](https://code.visualstudio.com/)
   - [Docker](https://www.docker.com/products/docker-desktop)
   - [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. Clone and open in VS Code:

   ```bash
   git clone https://github.com/theinterneti/augment-adam.git
   cd augment-adam
   code .
   ```

3. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container".

For more details, see [Devcontainer Documentation](docs/DEVCONTAINER.md).

#### Manual Setup (Alternative)

```bash
# Clone the repository
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam

# Install Poetry (dependency management)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --with dev

# Activate virtual environment
poetry shell

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/unit/test_memory.py

# Run with coverage
pytest --cov=augment_adam
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
