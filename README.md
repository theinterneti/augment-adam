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

### Memory System

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

### Agent Core

```python
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential

# Create a potential for controlled generation
sentence_ending_potential = RegexPotential(
    pattern=r".*[.!?]$",
    name="sentence_ending_potential"
)

# Create a conversational agent
agent = create_agent(
    agent_type="conversational",
    name="My Assistant",
    description="A helpful AI assistant",
    potentials=[sentence_ending_potential]
)

# Process user input
result = agent.process("Hello, how are you?")
print(f"Agent: {result['response']}")

# Create a task-focused agent
task_agent = create_agent(
    agent_type="task",
    name="Task Assistant",
    description="A task-focused AI assistant"
)

# Process a task request
result = task_agent.process("Can you help me plan a birthday party?")
print(f"Agent: {result['response']}")
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

## Agent Core

Augment Adam provides a flexible AI agent architecture with model management, memory integration, and reasoning capabilities:

- **Base Agent**: Foundation for all agent types with core functionality
- **Specialized Agents**: Conversational, Task, Research, Creative, and Coding agents
- **Memory Integration**: Agent-specific memory with global memory access
- **Reasoning Components**: Chain of thought, reflection, planning, and more
- **Sequential Monte Carlo**: Controlled generation with syntactic and semantic constraints, enabling smaller models to produce higher-quality outputs

### Agent Factory

The agent factory provides a simple way to create different types of agents:

```python
from augment_adam.ai_agent import create_agent, get_default_agent

# Create a conversational agent
conversational_agent = create_agent(
    agent_type="conversational",
    name="Conversational Assistant",
    description="A conversational AI assistant"
)

# Create a task agent
task_agent = create_agent(
    agent_type="task",
    name="Task Assistant",
    description="A task-focused AI assistant"
)

# Create a research agent
research_agent = create_agent(
    agent_type="research",
    name="Research Assistant",
    description="A research-focused AI assistant"
)

# Create a creative agent
creative_agent = create_agent(
    agent_type="creative",
    name="Creative Assistant",
    description="A creative-focused AI assistant"
)

# Create a coding agent
coding_agent = create_agent(
    agent_type="coding",
    name="Coding Assistant",
    description="A code-focused AI assistant"
)

# Get the default agent (based on settings)
default_agent = get_default_agent()
```

## Context Engine

Augment Adam provides a sophisticated context engine for managing context windows, retrieving relevant information, and optimizing prompts for language models:

- **Context Manager**: Central orchestrator for context management
- **Retrievers**: Components for retrieving information from various sources
- **Composers**: Components for composing context into coherent windows
- **Chunkers**: Components for intelligently chunking content
- **Optimizers**: Components for maximizing information density
- **Prompt Composers**: Components for creating prompts with context

```python
from augment_adam.context_engine import get_context_manager
from augment_adam.context_engine.retrieval import MemoryRetriever, WebRetriever
from augment_adam.context_engine.composition import ContextComposer, ContextOptimizer
from augment_adam.context_engine.chunking import IntelligentChunker, Summarizer
from augment_adam.context_engine.prompt import PromptComposer, PromptTemplates

# Get the context manager
context_manager = get_context_manager()

# Register retrievers
context_manager.register_retriever("memory", MemoryRetriever())
context_manager.register_retriever("web", WebRetriever())

# Register composers
context_manager.register_composer("default", ContextComposer())
context_manager.register_composer("optimizer", ContextOptimizer(Summarizer()))

# Register chunkers
context_manager.register_chunker("intelligent", IntelligentChunker())

# Register prompt composers
prompt_templates = PromptTemplates()
context_manager.register_prompt_composer(
    "default",
    PromptComposer(prompt_templates.get_all_templates())
)

# Process a query
prompt = context_manager.process_query(
    query="What is the capital of France?",
    sources=["memory", "web"],
    max_items=10,
    composer_name="default",
    optimizer_name="optimizer",
    prompt_type="qa"
)
```

## Small Models with Large Context Windows

Augment Adam supports small models with large context windows, leveraging our Monte Carlo approach for better performance:

```python
from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential
from augment_adam.ai_agent.smc.advanced_potentials import StylePotential, CONVERSATIONAL_STYLE

# Create a small model with large context window
model = create_model(
    model_type="huggingface",
    model_size="small_context",  # Uses Qwen/Qwen1.5-0.5B-Chat with 32K context
    use_cache=True,
    use_monte_carlo=True,
    monte_carlo_particles=100
)

# Create potentials for guided generation
potentials = [
    RegexPotential(
        pattern=r".*[.!?]$",
        name="sentence_ending_potential"
    ),
    StylePotential(
        style_patterns=CONVERSATIONAL_STYLE,
        name="conversational_style_potential"
    )
]

# Create an agent using the model
agent = create_agent(
    agent_type="conversational",
    name="Conversational Agent",
    description="A conversational AI assistant",
    model=model,
    potentials=potentials
)

# Generate a response
response = agent.process("Tell me about the benefits of small models with large context windows.")
print(f"Agent: {response['response']}")
```

Key benefits:

- **Efficiency**: Small models require less computational resources
- **Large Context**: Support for context windows up to 32K tokens
- **Guided Generation**: Monte Carlo approach enhances output quality
- **Parallel Processing**: Multi-core and GPU acceleration for faster generation
- **Persistent Caching**: Docker named volumes for efficient caching

For more details, see the [Small Models with Large Context Windows](docs/guides/small_models_large_context.md) guide.

## Hardware Optimization and Model Analysis

Augment Adam includes tools for automatically detecting your hardware capabilities and optimizing model settings accordingly:

```python
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings
from augment_adam.models import create_model

# Get optimal settings for your hardware
settings = get_optimal_model_settings("huggingface", "small_context")

# Create model with optimal settings
model = create_model(
    model_type="huggingface",
    model_size="small_context",
    **settings
)

# Generate text with optimized model
response = model.generate(
    prompt="What are the benefits of hardware optimization?",
    max_tokens=100
)
print(response)
```

Key features:

- **Automatic Hardware Detection**: CPU, memory, GPU, and disk specifications
- **Optimal Settings**: Quantization, parallel processing, and Monte Carlo parameters
- **Scientific Analysis**: Compare model performance across different tasks
- **Task-Specific Recommendations**: Find the best model for each specific task

For more details, see the [Hardware Optimization and Model Analysis](docs/guides/hardware_optimization.md) guide.

## Specialized Agents

Augment Adam provides a powerful agent framework for building specialized AI assistants:

```python
from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent

# Create a model
model = create_model(
    model_type="huggingface",
    model_size="small_context"
)

# Create an agent with system prompt and output instructions
agent = create_agent(
    agent_type="conversational",
    name="My Agent",
    description="A helpful AI assistant",
    model=model,
    system_prompt="You are a helpful AI assistant...",
    output_format="json",
    strict_output=True
)

# Process a request
result = agent.process("Hello, how are you?")
print(result["response"])
```

Key features:

- **System Prompts**: Define agent behavior with detailed instructions
- **Output Formats**: Support for text or structured JSON output
- **Specialized Tools**: Add custom tools for specific tasks
- **Worker Agents**: Process tasks asynchronously
- **MCP Integration**: Deploy agents as MCP servers

For more details, see the [Building Agents](docs/guides/building_agents.md) guide.

## Agent Coordination

Augment Adam provides powerful tools for coordinating multiple agents:

```python
from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow

# Create coordinator
coordinator = AgentCoordinator("My Coordinator")

# Register agents
coordinator.register_agent("research_agent", research_agent)
coordinator.register_agent("coding_agent", coding_agent)

# Send message from one agent to another
message = coordinator.send_message(
    from_agent_id="research_agent",
    to_agent_id="coding_agent",
    message="Here's information about algorithms..."
)

# Process the message
response = coordinator.process_message(message)
print(response["message"])

# Create a team with roles
team = AgentTeam(
    name="Development Team",
    description="A team for software development tasks"
)

# Add roles
team.add_role("researcher", research_agent)
team.add_role("developer", coding_agent)

# Create and execute a workflow
workflow = Workflow("Development Workflow")
workflow.add_process_step(role="researcher", input="Research algorithms")
workflow.add_message_step(from_role="researcher", to_role="developer", message="{researcher_result}")

# Execute workflow
result = team.execute_workflow("Create an algorithm", workflow.to_list())
```

Key features:

- **Agent Coordinator**: Manages communication between agents
- **Agent Team**: Organizes agents into teams with specific roles
- **Workflow**: Defines sequences of steps for agents to follow
- **Coordination Patterns**: Sequential, parallel, and collaborative coordination
- **Asynchronous Processing**: Support for async coordination

For more details, see the [Agent Coordination](docs/guides/agent_coordination.md) guide.

## FastAPI Server

Augment Adam includes a FastAPI server for easy integration with web applications:

```bash
# Start the server
python -m augment_adam.server

# The server will be available at http://localhost:8000
```

Key endpoints:

- `/models`: Create and manage models
- `/agents`: Create and manage agents
- `/models/{model_id}/generate`: Generate text with a model
- `/agents/{agent_id}/chat`: Chat with an agent
- `/hardware`: Get hardware information

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

### Research

The project includes research on various AI technologies and frameworks:

- [Open Source AI Projects](docs/research/open-source-ai-projects/index.md) - Critical assessments of leading open-source AI projects
- [Agentic Memory](docs/research/agentic-memory.md) - Research on memory systems for AI agents
- [AI Agent Development](docs/research/ai-agent-dev.md) - Research on AI agent development frameworks
- [DSPy](docs/research/dspy.md) - Research on the DSPy framework for programming with foundation models

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
