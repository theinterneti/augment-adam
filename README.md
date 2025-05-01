# Augment Adam

An intelligent assistant with advanced memory capabilities.

## Overview

Augment Adam is an AI assistant framework that uses advanced memory systems to provide more contextual and personalized responses. It features a modular architecture that allows for easy extension and customization.

## Features

- **Advanced Memory Systems**: FAISS-based vector memory for efficient similarity search and Neo4j-based graph memory for complex relationships
- **Modular Architecture**: Easily extend and customize the assistant with plugins
- **Context Engine**: Intelligent context management for better responses
- **Agent Coordination**: Coordinate multiple agents to work together on complex tasks
- **Monte Carlo Techniques**: Apply Monte Carlo techniques to models to enable using smaller models with advanced context/memory techniques
- **Parallel Processing**: Execute tasks in parallel for improved performance
- **Sophisticated Tagging System**: Categorize and organize code with a hierarchical tagging system
- **Enhanced Template Engine**: Generate code, tests, and documentation with a powerful template engine
- **Google-Style Docstrings**: All code includes comprehensive Google-style docstrings
- **Type Hints**: Extensive use of type hints for better code quality and IDE support

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
from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory

# Create a memory system
memory = FAISSMemory()

# Create an assistant
assistant = Assistant(memory=memory)

# Chat with the assistant
response = assistant.chat("Hello, how can you help me?")
print(response)
```

## Running with Docker

Augment Adam uses Docker for both development and deployment. The project includes a comprehensive Docker setup with multiple services for different components of the system.

### Development Environment

The project uses VS Code's Dev Containers extension to provide a consistent development environment. This environment includes:

- Python 3.10 with all required dependencies
- Ollama for local LLM inference
- ChromaDB for vector storage
- Neo4j for graph relationships
- Redis for caching
- Redis Vector for embeddings search
- GPU support for NVIDIA GPUs (optional)

To start the development environment:

1. Install Docker and VS Code with the Dev Containers extension
2. Open the project in VS Code
3. When prompted, click "Reopen in Container"

### Testing Services

The repository includes a test script to verify connectivity to all services:

```bash
python test_services.py
```

This script checks connectivity to all services and reports their status.

### Detailed Documentation

For detailed information about the Docker configuration, including:

- Service descriptions
- Persistent volumes
- GPU support
- Environment variables
- Troubleshooting

See the [Docker Configuration](docs/docker_configuration.md) documentation.

For more details on advanced configuration, see the [Memory System](docs/memory_system.md) and [Architecture Overview](docs/ARCHITECTURE.md).

## Documentation

For more detailed information, check out the documentation in the `docs/` directory:

- [Getting Started](docs/user_guide/getting_started.md)
- [Architecture Overview](docs/architecture/ARCHITECTURE.md)
- [Memory System](docs/architecture/memory_system.md)
- [Plugin System](docs/architecture/plugin_system.md)
- [Tagging System](docs/architecture/TAGGING_SYSTEM.md)
- [Docker Configuration](docs/docker_configuration.md)
- [Agent Coordination](docs/guides/agent_coordination.md)
- [Monte Carlo Techniques](docs/guides/parallel_monte_carlo.md)
- [Template Engine](docs/architecture/TEMPLATE_ENGINE.md)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
python scripts/setup_pre_commit.py

# Run tests
pytest
```

### Pre-Commit Hooks

This project uses pre-commit hooks to ensure code quality and run tests before each commit. The hooks will:

1. Check for common issues (trailing whitespace, merge conflicts, etc.)
2. Run linters (flake8, isort, black)
3. Run tests on modified files

To set up the pre-commit hooks, run:

```bash
python scripts/setup_pre_commit.py
```

You can also run the pre-commit checks manually:

```bash
pre-commit run --all-files
```

Or run tests on modified files:

```bash
python scripts/run_pre_commit_tests.py
```

### Project Structure

The project follows a standard Python package structure. For more details, see [Directory Structure](docs/DIRECTORY_STRUCTURE.md).

## Contributing

Contributions are welcome! Please see [Contributing Guidelines](docs/CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
