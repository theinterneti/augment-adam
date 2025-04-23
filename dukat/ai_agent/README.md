# Dukat AI Agent

An AI coding agent for development automation using local LLM models.

## Features

- **Model Management**: Download, load, and use local LLM models
- **Documentation Generation**: Automatically generate docstrings and other documentation
- **Test Creation**: Generate test cases for your code
- **Code Review**: Get AI-powered code reviews and suggestions
- **Refactoring**: Receive suggestions for code improvements

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Model Management

```bash
# List available models
python -m dukat.ai_agent.cli model list

# Download a model
python -m dukat.ai_agent.cli model download codellama/CodeLlama-7b-Instruct-hf

# Load a model
python -m dukat.ai_agent.cli model load codellama/CodeLlama-7b-Instruct-hf

# Set default model
python -m dukat.ai_agent.cli model set-default codellama/CodeLlama-7b-Instruct-hf
```

### Documentation Generation

```bash
# Generate docstrings for a Python file
python -m dukat.ai_agent.cli docstring path/to/file.py --style google
```

### Test Generation

```bash
# Generate tests for a Python file
python -m dukat.ai_agent.cli test path/to/file.py --framework pytest --coverage high
```

## Recommended Models

- **CodeLlama-13B-Instruct** - Good balance of performance and resource requirements
- **WizardCoder-Python-13B** - Specialized for Python code generation
- **Mistral-7B-Instruct-v0.2** - Excellent performance for its size

## Requirements

- Python 3.9+
- CUDA-compatible GPU recommended (but not required)
