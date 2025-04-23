# Dukat: AI-Powered Development Automation v0.3.3

An open-source AI coding agent focused on development automation, built entirely with open-source models and packages.

_Last updated: 2025-04-27_

[![Test Coverage: 90%](https://img.shields.io/badge/Test%20Coverage-90%25-brightgreen)](TESTING.md)
[![Tests: 38 passing](https://img.shields.io/badge/Tests-38%20passing-brightgreen)](TESTING.md)

## Project Status

Dukat is currently in active development. We have completed the foundation phase with the implementation of the model management framework and are now working on core capabilities. The current test coverage is at 90% with all tests passing.

See [TASKS.md](TASKS.md) for current progress, [PLANNING.md](PLANNING.md) for the overall development plan, and [TESTING.md](TESTING.md) for testing status and approach.

## Overview

Dukat is an open-source AI coding agent that focuses on development automation. It leverages the power of locally-run open-source language models to provide high-quality code assistance while prioritizing:

- **High-Quality Code Generation**: Automated documentation, testing, and code quality
- **Local-First**: Runs entirely on your machine with open source models for privacy and control
- **Development Workflow Integration**: Seamless integration with Git, IDEs, and CI/CD pipelines
- **Performance Optimization**: Efficient model inference through quantization and caching
- **Extensibility**: Modular architecture for adding new capabilities

## Features

- **Model Management**: Download, load, and use local LLM models with quantization support
- **Code Generation**: Create docstrings, tests, and other code artifacts automatically
- **Code Analysis**: Get explanations, reviews, and refactoring suggestions
- **CLI Interface**: User-friendly command-line tools for all features
- **Comprehensive Testing**: Extensive test suite for reliability and quality
- **Example Scripts**: Ready-to-use examples for common tasks

## Technology Stack

Dukat is built using the following technologies:

- **Hugging Face Transformers**: Framework for model loading and inference
- **PyTorch**: Deep learning framework for model execution
- **Accelerate/BitsAndBytes**: Model optimization and quantization
- **Typer/Rich**: CLI interface with rich formatting
- **Pytest**: Comprehensive testing framework
- **ChromaDB/FAISS**: Vector storage for code context (upcoming)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- CUDA-compatible GPU recommended (but not required)

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/dukat.git
   cd dukat
   ```

2. Install dependencies:

   ```bash
   pip install -r dukat/ai_agent/requirements.txt
   ```

3. Run the CLI interface:

   ```bash
   python -m dukat.ai_agent.cli model list
   ```

4. Download a model:

   ```bash
   python -m dukat.ai_agent.cli model download TinyLlama/TinyLlama-1.1B-Chat-v1.0
   ```

### Basic Usage

```bash
# List available models
python -m dukat.ai_agent.cli model list

# Download a model
python -m dukat.ai_agent.cli model download codellama/CodeLlama-7b-Instruct-hf

# Generate docstrings for a Python file
python -m dukat.ai_agent.cli docstring path/to/file.py

# Generate tests for a Python file
python -m dukat.ai_agent.cli test path/to/file.py
```

### Example Script

Try the example script to see Dukat in action:

```bash
# Run the model management demo
./examples/model_management_demo.py --task docstring --file path/to/your/file.py
```

## Project Structure

```
dukat/
├── ai_agent/              # Core AI agent module
│   ├── models/            # Model management
│   │   ├── manager.py     # Model downloading and inference
│   │   └── prompts.py     # Code-specific prompt templates
│   ├── cli.py             # Command-line interface
│   └── requirements.txt   # Dependencies
├── examples/              # Example scripts
│   └── model_management_demo.py  # Demo for model usage
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   │   └── ai_agent/      # Tests for AI agent module
│   └── integration/       # Integration tests
│       └── ai_agent/      # Integration tests for AI agent
├── .gitignore             # Git ignore file
├── PLANNING.md            # Development plan
├── TASKS.md               # Development tasks
├── LICENSE                # License file
├── README.md              # This file
└── pytest.ini             # Pytest configuration
```

## Recommended Models

Dukat works with various models from Hugging Face. Here are some recommended models:

| Model                    | Size | Best For        | Notes                                     |
| ------------------------ | ---- | --------------- | ----------------------------------------- |
| CodeLlama-13B-Instruct   | 13B  | General coding  | Good balance of performance and quality   |
| CodeLlama-7B-Instruct    | 7B   | General coding  | Faster, works on less powerful hardware   |
| TinyLlama-1.1B-Chat      | 1.1B | Quick tasks     | Lightweight, works on CPU                 |
| WizardCoder-Python-13B   | 13B  | Python-specific | Specialized for Python development        |
| Mistral-7B-Instruct-v0.2 | 7B   | Documentation   | Excellent for natural language generation |

All models are run locally using Hugging Face Transformers with quantization for efficiency.

## Development Status

Dukat is currently in active development (v0.3.3). The project is following the development plan outlined in [PLANNING.md](PLANNING.md) and the tasks listed in [TASKS.md](TASKS.md).

### Current Progress

- ✅ Model management framework with Hugging Face integration
- ✅ Code-specific prompt templates for various tasks
- ✅ CLI interface for model interaction and code generation
- ✅ Comprehensive testing framework (90% coverage)
- ✅ Example scripts for common use cases
- 🔄 Git and IDE integration
- 🔄 Memory system for code context
- 🔄 Performance optimizations
- ⏳ Web interface
- ⏳ Multi-file code generation

## Agent Reference Documentation

- [ONBOARDING.md](ONBOARDING.md): Quickstart and orientation for new AI coding agents. Contains project meta, core principles, key files, and agent responsibilities.
- [CHANGELOG.md](CHANGELOG.md): Chronological, agent-readable log of significant project changes, with links to related tasks and planning items.
- [SECURITY.md](SECURITY.md): Security policies, agent responsibilities, and procedures for handling vulnerabilities or sensitive operations.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): Agent behavior standards, collaboration protocols, and escalation procedures.

## Contributing

Contributions are welcome! Please read the [PLANNING.md](PLANNING.md) file to understand the project's direction and check [TASKS.md](TASKS.md) for current development tasks.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

_Last updated: 2025-04-27_
