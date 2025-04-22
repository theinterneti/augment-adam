# Dukat: Open Source AI Assistant v0.1.0

An open-source AI assistant focused on personal automation, built entirely with open-source models and packages.

_Last updated: 2025-04-22_

## Project Status

Dukat is currently in active development. We have completed the foundation phase and are working on implementing core capabilities. See [TASKS.md](TASKS.md) for current progress and [PLANNING.md](PLANNING.md) for the overall development plan.

## Overview

Dukat is an open-source AI assistant built with DSPy that focuses on personal automation. It leverages the power of locally-run open-source language models to provide a self-improving assistant that prioritizes:

- **High-Quality Code**: Automated testing, documentation, and code quality checks
- **Local-First**: Runs entirely on your machine with open source models
- **Self-Improvement**: Learns from interactions to get better over time
- **Asynchronous Processing**: Responsive performance through async operations
- **Extensibility**: Plugin architecture for adding new capabilities

## Features

- **Conversation**: Natural language interaction with memory of past conversations
- **Tool Integration**: Use tools for file operations, web search, and system information
- **Memory Management**: Working, episodic, and semantic memory for comprehensive context awareness
- **Self-Optimization**: Automatic improvement of prompts and responses through DSPy
- **Async Processing**: Background task handling for responsive performance
- **CLI and Web Interface**: Multiple ways to interact with the assistant

## Technology Stack

Dukat is built using the following technologies:

- **DSPy**: Core framework for LLM programming and optimization
- **Ollama**: Local model hosting and inference
- **ChromaDB/FAISS**: Vector storage for knowledge and memory
- **Poetry**: Dependency management
- **Pytest**: Testing framework
- **Sphinx**: Documentation generation
- **Rich**: Terminal UI for CLI

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.ai/) for running models locally

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/dukat.git
   cd dukat
   ```

2. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

3. Set up Ollama and download a model:

   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull a model
   ollama pull llama3:8b
   ```

4. Run Dukat:

   ```bash
   poetry run dukat
   ```

### Configuration

Dukat can be configured through a `config.yaml` file in your home directory:

```yaml
# ~/.dukat/config.yaml
model: llama3:8b # Model to use for inference
ollama_host: http://localhost:11434 # Ollama API endpoint
memory:
  vector_db: chroma # Vector database for memory (chroma or faiss)
  persist_dir: ~/.dukat/memory # Directory to store memory
```

### Using Dukat

Once installed, you can use Dukat in several ways:

1. **Command Line**: Run `dukat` to start the interactive CLI
2. **Web Interface**: Run `dukat web` to start the web interface
3. **Python API**: Import and use Dukat in your Python scripts

```python
from dukat.core import Assistant

assistant = Assistant()
response = assistant.ask("What can you help me with?")
print(response)
```

## Project Structure

```
dukat/
├── core/                 # Core system components
│   ├── model_manager.py  # Model loading and inference
│   ├── memory.py         # Memory management system
│   ├── tools.py          # Tool calling capabilities
│   └── prompt_manager.py # Prompt templates and optimization
├── plugins/              # Plugin system
│   ├── __init__.py       # Plugin system initialization
│   ├── base.py           # Base plugin class
│   ├── web_search.py     # Web search plugin
│   ├── file_manager.py   # File operations plugin
│   └── system_info.py    # System information plugin
├── memory/               # Memory architecture
│   ├── working.py        # Short-term context management
│   ├── episodic.py       # Interaction history storage
│   ├── semantic.py       # Knowledge storage and retrieval
│   └── procedural.py     # Learned patterns and procedures
├── cli.py                # Command-line interface
├── web.py                # Web interface
├── config.py             # Configuration management
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
│   ├── api/              # API documentation
│   └── user_guide/       # User documentation
├── .gitignore            # Git ignore file
├── PLANNING.md           # Development plan
├── TASKS.md              # Development tasks
├── augment-guidelines.yaml # Project guidelines
├── LICENSE               # License file
├── README.md             # This file
├── pyproject.toml        # Poetry configuration
└── .pre-commit-config.yaml # Pre-commit hooks
```

## Model Support

Dukat uses open-source language models for inference, with different models optimized for different tasks:

| Task            | Preferred Models                     |
| --------------- | ------------------------------------ |
| Conversation    | Llama 3 8B, Mistral 7B Instruct v0.2 |
| Code Generation | CodeLlama 7B Instruct, Llama 3 8B    |
| Reasoning       | Llama 3 8B, Mistral 7B Instruct v0.2 |
| Tool Use        | Llama 3 8B, CodeLlama 7B Instruct    |

Models are run locally using [Ollama](https://ollama.ai/), which provides efficient inference on consumer hardware. DSPy optimizes prompts and model weights to improve performance over time.

## Development Status

Dukat is currently in early development (v0.1.0). The project is following the development plan outlined in [PLANNING.md](PLANNING.md) and the tasks listed in [TASKS.md](TASKS.md).

## Contributing

Contributions are welcome! Please read the [PLANNING.md](PLANNING.md) file to understand the project's direction and check [TASKS.md](TASKS.md) for current development tasks.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

_Last updated: 2025-04-22_
