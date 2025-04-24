# Augment Adam

An intelligent assistant with advanced memory capabilities.

## Features

- **Multiple Memory Systems**: FAISS, Neo4j, and working memory integration
- **Memory Interface**: Common interface for all memory systems
- **Memory Factory**: Easy creation of different memory systems
- **AI Agent**: Flexible AI agent architecture with model management
- **Context Engine**: Advanced context management with vector search and knowledge graphs
- **Plugin System**: Extensible plugin architecture
- **Web Interface**: Interactive web interface for visualization and management

## Installation

```bash
# Basic installation
pip install augment-adam

# With Neo4j support
pip install augment-adam[neo4j]

# With development tools
pip install augment-adam[dev]
```

## Quick Start

### Memory System

```python
from augment_adam.memory import create_memory

# Create a memory instance
memory = create_memory(memory_type="faiss")

# Add a memory
memory_id = memory.add(
    text="Python is a programming language with simple syntax and powerful libraries.",
    metadata={"type": "note", "topic": "programming", "language": "python"}
)

# Retrieve memories
results = memory.retrieve(
    query="programming language",
    n_results=5,
    filter_metadata={"topic": "programming"}
)

# Process results
for memory, similarity in results:
    print(f"Memory: {memory['text']}")
    print(f"Similarity: {similarity}")
    print(f"Metadata: {memory}")
    print()
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

## Memory Systems

Augment Adam provides multiple memory systems with a common interface:

- **FAISS Memory**: Vector-based memory using Facebook AI Similarity Search

  - Fast similarity search for large collections of vectors
  - Persistent storage of vectors and metadata
  - Filtering based on metadata

- **Neo4j Memory**: Graph-based memory using Neo4j
  - Graph-based relationships between memories
  - Advanced graph queries
  - Filtering based on metadata

## Memory Factory

The memory factory provides a simple way to create different types of memory systems:

```python
from augment_adam.memory import create_memory, get_default_memory

# Create a FAISS memory instance
faiss_memory = create_memory(
    memory_type="faiss",
    persist_dir="/path/to/memory",
    collection_name="my_collection"
)

# Create a Neo4j memory instance
neo4j_memory = create_memory(
    memory_type="neo4j",
    collection_name="my_collection"
)

# Get the default memory instance (based on settings)
default_memory = get_default_memory()
```

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

For more detailed documentation, see the [docs](docs/) directory.

## License

MIT
