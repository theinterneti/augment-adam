# Model Management System

This directory contains the model management system for Augment Adam, which provides a unified interface for working with language models from different providers.

## Overview

The model management system is designed to be modular and extensible, with support for multiple model backends. The current implementation includes support for:

- HuggingFace models (including Qwen 3)
- Ollama models

The system is designed to efficiently share models between backends, allowing you to download a model once and use it with multiple backends.

## Architecture

The system is built around the following components:

- `ModelBackend`: An abstract base class that defines the interface for all model backends.
- `HuggingFaceModel`: An implementation of `ModelBackend` for HuggingFace models.
- `OllamaModel`: An implementation of `ModelBackend` for Ollama models.
- `ModelRegistry`: A registry for model backends, allowing for easy switching between different model implementations.
- `ModelManager`: The main entry point for the system, providing a high-level interface for working with models.

## Usage

### Basic Usage

```python
from src.models.model_manager import ModelManager

# Create a model manager for Qwen 3
manager = ModelManager(
    model_type="huggingface",
    model_size="qwen3_medium",
    domain="code"
)

# Generate a response
response = manager.generate_response(
    prompt="What are the key features of Python 3.12?",
    temperature=0.7,
    max_tokens=500
)
print(response)
```

### Streaming Responses

```python
from src.models.model_manager import ModelManager

# Create a model manager
manager = ModelManager(model_type="ollama", model_size="medium")

# Generate a streaming response
for chunk in manager.generate_stream(
    prompt="Write a short story about a robot learning to paint.",
    temperature=0.7,
    max_tokens=500
):
    print(chunk, end="", flush=True)
```

### Command-Line Interface

The system includes a command-line interface for generating responses:

```bash
python src/models/generate_response.py --prompt "What are the key features of Python 3.12?" --model_type huggingface --model_size qwen3_medium
```

For streaming responses:

```bash
python src/models/generate_response.py --prompt "Write a short story about a robot learning to paint." --model_type ollama --model_size medium --stream
```

## Model Sharing

The system is designed to efficiently share models between backends. When you load a HuggingFace model, it can be automatically shared with Ollama, allowing you to use the same model with both backends without downloading it twice.

To enable model sharing:

```python
from src.models.model_manager import ModelManager

# Create a model manager with model sharing enabled
manager = ModelManager(
    model_type="huggingface",
    model_size="qwen3_medium",
    share_with_ollama=True
)
```

## Qwen 3 Models

The system includes special support for Qwen 3 models, with the following sizes available:

- `qwen3_small`: Qwen/Qwen3-0.6B-Chat
- `qwen3_medium`: Qwen/Qwen3-1.7B-Chat
- `qwen3_large`: Qwen/Qwen3-4B-Chat
- `qwen3_xl`: Qwen/Qwen3-8B-Chat
- `qwen3_xxl`: Qwen/Qwen3-14B-Chat
- `qwen3_xxxl`: Qwen/Qwen3-32B-Chat

Qwen 3 models have very large context windows (32K tokens for small/medium/large, 128K tokens for xl/xxl/xxxl), making them ideal for tasks that require processing large amounts of text.

## Examples

The `examples` directory contains example scripts for working with the model management system:

- `qwen3_model_test.py`: Demonstrates how to use Qwen 3 models with HuggingFace and Ollama backends.
- `streaming_test.py`: Demonstrates how to generate streaming responses from models.

## Future Work

- Add support for more model backends (e.g., OpenAI, Anthropic, etc.)
- Improve model sharing between backends
- Add support for more model types and architectures
- Implement better error handling and fallback mechanisms
