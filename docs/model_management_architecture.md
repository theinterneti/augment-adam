# Model Management System Architecture

This document describes the architecture of the Augment Adam model management system.

## Overview

The model management system is designed to be modular and extensible, with support for multiple model backends. The current implementation includes support for HuggingFace and Ollama backends, with a focus on Qwen 3 models.

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                           ModelManager                                 │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                        ModelRegistry                            │  │
│  │                                                                 │  │
│  │  ┌─────────────────┐         ┌─────────────────┐               │  │
│  │  │  HuggingFace    │         │     Ollama      │               │  │
│  │  │    Backend      │◄───────►│    Backend      │               │  │
│  │  └─────────────────┘         └─────────────────┘               │  │
│  │                                                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │
                                   │
                                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                           Applications                                 │
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │  CLI Interface  │  │  Web Interface  │  │  API Interface  │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Components

### ModelBackend

The `ModelBackend` is an abstract base class that defines the interface for all model backends. It includes methods for:

- Initializing the model
- Generating text
- Streaming text generation
- Counting tokens
- Generating embeddings
- Getting model information
- Checking model availability
- Formatting prompts
- Sharing models between backends

### HuggingFaceModel

The `HuggingFaceModel` is an implementation of the `ModelBackend` interface for HuggingFace models. It provides:

- Support for loading and running HuggingFace models
- Quantization options (4-bit, 8-bit)
- Flash Attention support
- Embedding generation
- Model sharing with Ollama

### OllamaModel

The `OllamaModel` is an implementation of the `ModelBackend` interface for Ollama models. It provides:

- Support for loading and running Ollama models
- API-based interaction with Ollama
- Streaming generation
- Integration with shared models from HuggingFace

### ModelRegistry

The `ModelRegistry` is a registry for model backends, allowing for easy switching between different model implementations. It provides:

- Registration of model backends
- Creation of model instances
- Retrieval of model instances
- Listing of available models and backends
- Model sharing between backends

### ModelManager

The `ModelManager` is the main entry point for the system, providing a high-level interface for working with models. It provides:

- Initialization of models based on type, size, and domain
- Text generation
- Streaming text generation
- Embedding generation
- Model information retrieval
- Environment information (Docker, WSL)

## Data Flow

1. The application creates a `ModelManager` instance with the desired configuration.
2. The `ModelManager` initializes the `ModelRegistry` and registers the available backends.
3. The `ModelManager` creates a model instance using the registry.
4. The application calls methods on the `ModelManager` to generate text, embeddings, etc.
5. The `ModelManager` delegates the calls to the appropriate model backend.
6. The model backend processes the request and returns the results.

## Model Sharing

The system is designed to efficiently share models between backends. When a model is loaded with HuggingFace, it can be shared with Ollama, allowing both backends to use the same model files without duplicating them.

The model sharing process works as follows:

1. The HuggingFace model is loaded and initialized.
2. The model files are saved to a shared location.
3. Metadata about the model is saved to a JSON file.
4. When an Ollama model with the same name is requested, it checks for shared model files.
5. If shared files are found, Ollama uses them instead of downloading the model again.

This approach allows for efficient use of disk space and reduces the need to download models multiple times.
