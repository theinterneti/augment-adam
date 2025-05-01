# Model Management System

This PR introduces a comprehensive model management system for Augment Adam, providing a unified interface for working with language models from different providers.

## Features

- **Unified Interface**: A single interface for working with different model backends
- **Multiple Backends**: Support for HuggingFace and Ollama backends
- **Model Sharing**: Efficient model sharing between backends to avoid duplicate downloads
- **Streaming Generation**: Support for streaming text generation
- **Embedding Generation**: Support for generating embeddings
- **Qwen 3 Models**: Special support for Qwen 3 models with long context windows
- **Domain-Specific Models**: Support for domain-specific models (Docker, WSL, devcontainers, etc.)
- **Hardware-Aware**: Automatic selection of models based on available hardware

## Components

The system consists of the following components:

- `ModelBackend`: Abstract base class defining the interface for all model backends
- `ModelRegistry`: Registry for model backends, allowing for easy switching between implementations
- `ModelManager`: Main entry point providing a high-level interface for working with models
- `HuggingFaceModel`: Implementation of ModelBackend for HuggingFace models
- `OllamaModel`: Implementation of ModelBackend for Ollama models

## Usage

### Basic Usage

```python
from src.models.model_manager import ModelManager

# Create a model manager
manager = ModelManager(
    model_type="huggingface",  # or "ollama"
    model_size="qwen3_medium",  # or any other size
    domain="code"  # optional domain specialization
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
# Generate a streaming response
for chunk in manager.generate_stream(
    prompt="Write a short story about a robot learning to paint.",
    temperature=0.7,
    max_tokens=500
):
    print(chunk, end="", flush=True)
```

### Embeddings

```python
# Generate embeddings for a text
embeddings = manager.embed("This is a sample text for embedding.")

# Generate embeddings for multiple texts
batch_embeddings = manager.batch_embed(["Text 1", "Text 2", "Text 3"])
```

### Model Sharing

```python
# Create a model manager with model sharing enabled
manager = ModelManager(
    model_type="huggingface",
    model_size="qwen3_medium",
    share_with_ollama=True  # Enable model sharing
)
```

## Qwen 3 Models

The system includes special support for Qwen 3 models, with the following sizes available:

| Size | HuggingFace Model ID | Ollama Model ID | Context Window |
|------|---------------------|----------------|----------------|
| Small | Qwen/Qwen3-0.6B-Chat | qwen3:0.6b | 32K tokens |
| Medium | Qwen/Qwen3-1.7B-Chat | qwen3:1.7b | 32K tokens |
| Large | Qwen/Qwen3-4B-Chat | qwen3:4b | 32K tokens |
| XL | Qwen/Qwen3-8B-Chat | qwen3:8b | 128K tokens |
| XXL | Qwen/Qwen3-14B-Chat | qwen3:14b | 128K tokens |
| XXXL | Qwen/Qwen3-32B-Chat | qwen3:32b | 128K tokens |

Additionally, the following Mixture-of-Experts (MoE) models are available:

| Size | HuggingFace Model ID | Context Window |
|------|---------------------|----------------|
| MoE Small | Qwen/Qwen3-30B-A3B-Chat | 128K tokens |
| MoE Large | Qwen/Qwen3-235B-A22B-Chat | 128K tokens |

## Hardware Considerations

When selecting models, consider the following hardware requirements:

### CPU Only
- Smaller models (1-2B parameters)
- Models optimized for CPU inference
- Examples: TinyLlama-1.1B, Qwen3-0.6B, Phi-3-Mini, Gemma-2-2B

### Low-End GPU (2-4GB VRAM)
- Small to medium models (2-7B parameters)
- Models that can be quantized to 4-bit
- Examples: Qwen3-1.7B, Phi-3-Mini, Mistral-7B, Gemma-2-2B

### Mid-Range GPU (8-16GB VRAM)
- Medium models (7-13B parameters)
- Models with good performance-to-size ratio
- Examples: Qwen3-4B, Mistral-7B, Llama-3-8B, Gemma-2-9B

### High-End GPU (24GB+ VRAM)
- Larger models (13B+ parameters)
- Models with state-of-the-art performance
- Examples: Qwen3-8B, Llama-3-70B, Claude-3-Haiku

## Documentation

For more information, see the [Model Management Guidelines](docs/development/MODEL_MANAGEMENT.md).

## Examples

The `examples` directory contains several examples demonstrating how to use the model management system:

- `basic_usage.py`: Basic usage example
- `streaming_example.py`: Streaming generation example
- `embedding_example.py`: Embedding generation example
- `model_sharing_example.py`: Model sharing example
- `qwen3_example.py`: Qwen 3 models example

## Tests

The system includes a comprehensive test suite:

- Unit tests for each component
- Integration tests for the entire system
- Tests for Qwen 3 models

## Future Work

- Add support for more model backends (OpenAI, Anthropic, etc.)
- Add support for more model architectures
- Add support for fine-tuning models
- Add support for model quantization
- Add support for model pruning
- Add support for model distillation
- Add support for model evaluation
