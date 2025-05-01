# Model Management Guidelines

This document provides guidelines for using and extending the model management system in Augment Adam.

## Overview

The model management system provides a unified interface for working with language models from different providers. It is designed to be modular and extensible, with support for multiple model backends.

## Architecture

The system is built around the following components:

- `ModelBackend`: An abstract base class that defines the interface for all model backends.
- `HuggingFaceModel`: An implementation of `ModelBackend` for HuggingFace models.
- `OllamaModel`: An implementation of `ModelBackend` for Ollama models.
- `ModelRegistry`: A registry for model backends, allowing for easy switching between different model implementations.
- `ModelManager`: The main entry point for the system, providing a high-level interface for working with models.

## Model Backends

### HuggingFace Backend

The HuggingFace backend is the primary backend for the model management system. It provides:

- Support for loading and running HuggingFace models
- Quantization options (4-bit, 8-bit)
- Flash Attention support
- Embedding generation
- Model sharing with Ollama

Configuration options:

- `model_id`: The ID of the model on HuggingFace Hub
- `cache_dir`: Directory to cache models
- `device`: Device to use for inference ("cpu", "cuda", "auto")
- `quantization`: Quantization method to use ("4bit", "8bit", None)
- `use_flash_attention`: Whether to use Flash Attention if available
- `embedding_model_id`: ID of the embedding model to use

### Ollama Backend

The Ollama backend is the secondary/development backend for the model management system. It provides:

- Support for loading and running Ollama models
- API-based interaction with Ollama
- Streaming generation
- Integration with shared models from HuggingFace

Configuration options:

- `model_id`: The ID of the model in Ollama
- `cache_dir`: Directory to cache models (shared with HuggingFace)
- `ollama_host`: The host URL for Ollama API
- `embedding_model_id`: ID of the embedding model to use

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

## Model Sharing

The model management system is designed to efficiently share models between backends. When you load a model with HuggingFace, it can be automatically shared with Ollama, allowing you to use the same model with both backends without downloading it twice.

To enable model sharing:

```python
from src.models.model_manager import ModelManager

# Create a model manager with model sharing enabled
manager = ModelManager(
    model_type="huggingface",
    model_size="qwen3_medium",
    share_with_ollama=True  # Enable model sharing
)
```

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

## Performance Optimization

To optimize model performance:

1. **Quantization**: Use 4-bit or 8-bit quantization for larger models to reduce memory usage.
2. **Flash Attention**: Enable Flash Attention for faster inference on supported models.
3. **Batch Processing**: Process multiple inputs in a batch when possible.
4. **Caching**: Use the shared model cache to avoid downloading models multiple times.
5. **Async Processing**: Run performance-intensive tasks asynchronously if they will take more than 60 seconds.

## Integration Guidelines

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
embeddings = manager.generate_embeddings(
    text="This is a sample text for embedding."
)

# Generate embeddings for multiple texts
batch_embeddings = manager.generate_batch_embeddings(
    texts=["Text 1", "Text 2", "Text 3"]
)
```

## Development Guidelines

When extending the model management system:

1. **Follow the Interface**: Implement the `ModelBackend` interface for new backends.
2. **Register Backends**: Register new backends with the `ModelRegistry`.
3. **Share Models**: Implement model sharing between backends when possible.
4. **Error Handling**: Implement proper error handling and fallback mechanisms.
5. **Documentation**: Document new backends and models.
6. **Testing**: Write unit tests for new backends and models.

## Testing Guidelines

When testing the model management system:

1. **Unit Tests**: Write unit tests for each component.
2. **Integration Tests**: Write integration tests for the entire system.
3. **Performance Tests**: Write performance tests for critical paths.
4. **Mock Models**: Use mock models for testing to avoid downloading large models.
5. **Test All Backends**: Test all backends with the same test suite.
6. **Test Model Sharing**: Test model sharing between backends.
