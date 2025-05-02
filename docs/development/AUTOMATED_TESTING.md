# Automated Background Testing Framework

This document describes the automated background testing framework for the Augment Adam project. The framework automatically generates, runs, and validates tests in the background while you develop new features.

## Overview

The automated background testing framework consists of several components:

1. **Background Test Service**: Monitors code changes and triggers test generation and execution
2. **Test Generator**: Generates tests using Hugging Face models
3. **Test Executor**: Runs tests in the background
4. **Test Reporter**: Reports test results in real-time
5. **Test Dashboard**: Provides a web interface for viewing test results
6. **Resource Monitor**: Monitors system resources to avoid overloading

## Setup

### Prerequisites

- Python 3.9 or higher
- NVIDIA GPU (optional, but recommended for faster test generation)
- At least 8GB of RAM (16GB recommended)

### Installation

1. Install the required dependencies:

```bash
pip install -e ".[dev]"
```

2. Set up the Hugging Face models:

```bash
./scripts/setup_huggingface_models.sh
```

This script will:
- Install the required dependencies
- Download the appropriate models based on your hardware
- Create configuration files
- Test the setup

## Usage

### Starting the Background Test Service

To start the background test service, run:

```bash
./scripts/run_background_tests.sh
```

This script will:
- Start the test dashboard server
- Start the background test service
- Monitor code changes and generate/run tests automatically

### Viewing Test Results

The test dashboard is available at:

```
http://localhost:8080
```

The dashboard provides:
- A summary of test results
- A list of recent test runs
- Detailed test output

### Configuration

The background test service can be configured by editing the following files:

- `config/test_generator_config.json`: Configuration for the test generator
- `config/model_config.json`: Configuration for the Hugging Face models

## Components

### Background Test Service

The background test service (`scripts/background_test_service.py`) is the main component of the framework. It:

- Monitors code changes using the test watcher
- Triggers test generation when code changes
- Runs tests in the background
- Reports test results
- Updates the TASKS.md file with test results

### Test Generator

The test generator (`scripts/test_generator.py`) generates tests using Hugging Face models. It:

- Analyzes the code to understand its behavior
- Generates tests with meaningful assertions
- Merges with existing tests if requested
- Handles abstract classes and interfaces intelligently

### Test Executor

The test executor (`scripts/test_executor.py`) runs tests in the background. It:

- Runs tests in parallel
- Limits the number of concurrent test runs
- Captures test output
- Reports test results

### Test Reporter

The test reporter (`scripts/test_reporter.py`) reports test results in real-time. It:

- Saves test results to files
- Updates the test summary
- Provides an API for the test dashboard

### Test Dashboard

The test dashboard (`scripts/test_dashboard.py`) provides a web interface for viewing test results. It:

- Displays a summary of test results
- Shows a list of recent test runs
- Provides detailed test output
- Auto-refreshes to show the latest results

### Resource Monitor

The resource monitor (`scripts/resource_monitor.py`) monitors system resources to avoid overloading. It:

- Monitors CPU, memory, and disk usage
- Throttles test execution when resources are constrained
- Provides an API for the background test service

## Models

The framework uses Qwen models from Alibaba, which are optimized for code generation and understanding:

### Small Models (2-4GB VRAM/RAM)

- **Qwen2-1.5B-Instruct**: Compact model for basic test generation, can run on CPU

### Medium Models (8-16GB VRAM/RAM)

- **Qwen2-7B-Instruct**: Well-balanced model for comprehensive test generation, recommended for most use cases

### Large Models (24GB+ VRAM/RAM)

- **Qwen2.5-14B-Instruct**: Larger model for advanced test generation with better understanding of complex code

## Test Types

The framework can generate several types of tests:

1. **Unit Tests**: Basic tests for functions and methods using pytest
2. **Integration Tests**: Tests for interactions between components
3. **Property-Based Tests**: Tests that verify properties of functions using Hypothesis

## Customization

### Using Different Models

To use a different model, edit the `config/model_config.json` file or specify the model when starting the background test service:

```bash
python scripts/background_test_service.py --model-name "Qwen/Qwen2.5-14B-Instruct"
```

### Adjusting Resource Usage

To adjust resource usage, edit the `config/test_generator_config.json` file or specify the resource threshold when starting the background test service:

```bash
python scripts/background_test_service.py --resource-threshold 0.7
```

### Changing Test Generation Parameters

To change test generation parameters, edit the `config/test_generator_config.json` file or specify the parameters when starting the background test service:

```bash
python scripts/background_test_service.py --temperature 0.3 --max-length 2048
```

## Troubleshooting

### Out of Memory Errors

If you encounter out of memory errors, try:

1. Using a smaller model (e.g., TinyLlama)
2. Reducing the number of concurrent tests
3. Increasing the resource threshold

### Slow Test Generation

If test generation is slow, try:

1. Using a GPU if available
2. Using a smaller model
3. Reducing the maximum length of generated tests

### Test Generation Failures

If test generation fails, check:

1. The log files in the `logs` directory
2. The model configuration
3. The code being tested (complex or unusual code may be difficult to generate tests for)

## Future Improvements

Planned improvements to the framework include:

1. Support for more test types (e.g., end-to-end tests)
2. Integration with CI/CD pipelines
3. Improved test generation quality
4. Support for more programming languages
5. Better handling of complex code structures
