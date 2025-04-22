# Automated Test Generation

This document describes the automated test generation system for the Dukat project. The system uses local open-source models and tools to generate comprehensive test suites for Python modules.

## Overview

The test generation system combines multiple approaches to create comprehensive test suites:

1. **LLM-based test generation**: Uses local LLMs (via Ollama) to generate tests based on code analysis
2. **Pynguin**: Automated unit test generation for Python using search-based techniques
3. **Hypothesis**: Property-based testing for Python

## Setup

### Prerequisites

- Docker and Docker Compose
- At least 8GB of RAM (16GB recommended)
- NVIDIA GPU (optional, but recommended for faster generation)

### Installation

1. Run the setup script:

```bash
./scripts/setup_test_gen.sh
```

This script will:
- Create necessary directories
- Build the Docker images
- Pull the required Ollama models
- Configure GPU support if available

## Usage

### Basic Usage

To generate tests for a Python module:

```bash
docker-compose -f docker-compose.test-gen.yml run test-generator \
  --source-file path/to/file.py \
  --output-dir tests/
```

This will generate tests using all available methods and save them to the specified output directory.

### Advanced Usage

You can customize the test generation process with various options:

```bash
docker-compose -f docker-compose.test-gen.yml run test-generator \
  --source-file path/to/file.py \
  --output-dir tests/ \
  --config config/test_generator_config.json \
  --model codellama:7b \
  --no-pynguin \
  --ollama-host http://ollama:11434
```

Available options:
- `--source-file`: Path to the source file to generate tests for (required)
- `--output-dir`: Directory to output generated tests (required)
- `--config`: Path to configuration file
- `--no-llm`: Skip LLM-based test generation
- `--no-pynguin`: Skip Pynguin test generation
- `--no-hypothesis`: Skip Hypothesis test generation
- `--model`: LLM model to use (default: codellama:7b)
- `--ollama-host`: Ollama host URL (default: http://localhost:11434)

### Configuration

You can customize the test generation process by editing the `config/test_generator_config.json` file. This file contains settings for:

- LLM models and parameters
- Test frameworks to use
- Templates for generated tests
- Resource requirements for different models

## Available Models

The system includes several models for different use cases:

### Small Models (2-4GB VRAM/RAM)
- **TinyLlama (1.1B)**: Good for simple code completion and basic test scaffolding

### Medium Models (8-16GB VRAM/RAM)
- **CodeLlama-7B**: Meta's code-specialized model, good for test generation

### Large Models (24GB+ VRAM/RAM)
- **WizardCoder-15B**: Specialized for code generation and understanding

## Test Types

The system can generate several types of tests:

1. **Unit Tests**: Basic tests for functions and methods using pytest
2. **Property-Based Tests**: Tests that verify properties of functions using Hypothesis
3. **Integration Tests**: Tests for interactions between components

## Examples

### Generate Tests for a Single Module

```bash
docker-compose -f docker-compose.test-gen.yml run test-generator \
  --source-file dukat/core/async_assistant.py \
  --output-dir tests/unit/
```

### Generate Tests with a Specific Model

```bash
docker-compose -f docker-compose.test-gen.yml run test-generator \
  --source-file dukat/core/async_assistant.py \
  --output-dir tests/unit/ \
  --model tinyllama:1.1b
```

### Generate Only Property-Based Tests

```bash
docker-compose -f docker-compose.test-gen.yml run test-generator \
  --source-file dukat/core/async_assistant.py \
  --output-dir tests/unit/ \
  --no-llm \
  --no-pynguin
```

## Troubleshooting

### Out of Memory Errors

If you encounter out of memory errors, try:
1. Using a smaller model (e.g., tinyllama:1.1b)
2. Increasing Docker's memory limit
3. Splitting large modules into smaller parts

### Model Loading Issues

If Ollama fails to load a model:
1. Check that you have enough disk space
2. Verify that the model name is correct
3. Try pulling the model manually: `docker-compose -f docker-compose.test-gen.yml exec ollama ollama pull <model-name>`

### Test Generation Failures

If test generation fails:
1. Check the logs for error messages
2. Verify that the source file is valid Python
3. Try using a different model or approach

## Extending the System

### Adding New Models

To add a new model:
1. Add the model to the `models` section in `config/test_generator_config.json`
2. Pull the model using Ollama: `ollama pull <model-name>`

### Adding New Test Frameworks

To add a new test framework:
1. Add the framework to the `test_frameworks` list in `config/test_generator_config.json`
2. Create a template file in the `templates/` directory
3. Implement the generator in `scripts/auto_test_generator.py`

## Future Improvements

- Integration with CI/CD pipelines
- Support for more programming languages
- Improved test quality assessment
- Automated test maintenance
