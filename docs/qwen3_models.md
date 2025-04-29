# Using Qwen 3 Models

This document explains how to use Qwen 3 models with the Augment Adam model management system.

## Overview

Qwen 3 is a family of large language models (LLMs) developed by Alibaba Cloud. These models offer excellent performance with large context windows, making them ideal for tasks that require processing large amounts of text.

The Augment Adam model management system provides support for Qwen 3 models through both HuggingFace and Ollama backends, with HuggingFace as the primary backend and Ollama as a fallback.

## Available Qwen 3 Models

The following Qwen 3 models are supported:

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

## Using Qwen 3 Models

### Basic Usage

```python
from src.models.model_manager import ModelManager

# Create a model manager for Qwen 3
manager = ModelManager(
    model_type="huggingface",  # or "ollama"
    model_size="qwen3_medium",  # or any other Qwen 3 size
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
from src.models.model_manager import ModelManager

# Create a model manager for Qwen 3
manager = ModelManager(
    model_type="huggingface",
    model_size="qwen3_medium"
)

# Generate a streaming response
for chunk in manager.generate_stream(
    prompt="Write a short story about a robot learning to paint.",
    temperature=0.7,
    max_tokens=500
):
    print(chunk, end="", flush=True)
```

### Command-Line Interface

You can also use Qwen 3 models from the command line:

```bash
python src/models/generate_response.py \
    --prompt "What are the key features of Python 3.12?" \
    --model_type huggingface \
    --model_size qwen3_medium
```

For streaming responses:

```bash
python src/models/generate_response.py \
    --prompt "Write a short story about a robot learning to paint." \
    --model_type huggingface \
    --model_size qwen3_medium \
    --stream
```

## Model Sharing

The model management system is designed to efficiently share models between backends. When you load a Qwen 3 model with HuggingFace, it can be automatically shared with Ollama, allowing you to use the same model with both backends without downloading it twice.

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

## Installation and Setup

To set up the model management system with Qwen 3 models:

1. Install the required dependencies:

```bash
python scripts/setup_models.py --install_deps --backend all
```

2. Download the Qwen 3 models:

```bash
python scripts/setup_models.py --backend all --domains qwen3_small qwen3_medium
```

## Performance Considerations

- Qwen 3 models have very large context windows (32K-128K tokens), which makes them ideal for tasks that require processing large amounts of text.
- The smaller models (0.6B, 1.7B, 4B) can run on most modern hardware, while the larger models (8B+) require more powerful GPUs.
- For the best performance with HuggingFace, use quantization (4-bit or 8-bit) and Flash Attention if available.
- For Ollama, make sure you have enough RAM and disk space to run the models.

## Troubleshooting

If you encounter issues with Qwen 3 models:

1. Check that you have the required dependencies installed:
   - For HuggingFace: `torch`, `transformers`, `huggingface_hub`, `sentence-transformers`
   - For Ollama: Ollama installed and running

2. Check that the model is available:
   - For HuggingFace: Check that you have access to the model on the HuggingFace Hub
   - For Ollama: Check that the model is available with `ollama list`

3. Check the logs for error messages:
   - Look for error messages in the console output
   - Check the model manager logs for more detailed information

4. Try a smaller model:
   - If you're having memory issues, try a smaller model like `qwen3_small` or `qwen3_medium`

5. Try a different backend:
   - If HuggingFace is not working, try Ollama
   - If Ollama is not working, try HuggingFace
