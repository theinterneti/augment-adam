# Model Management

The Dukat project includes a robust model management system for handling AI models. This document provides guidance on using the model management system.

## Overview

The model management system allows you to:

1. Download models from Hugging Face Hub
2. Load models into memory
3. Generate text using loaded models
4. Unload models to free up memory
5. List available and loaded models
6. Set a default model

## ModelManager

The `ModelManager` class is the main interface for model management.

```python
from augment_adam.ai_agent.models import ModelManager

# Create a model manager
manager = ModelManager(
    models_dir="/path/to/models",
    config_path="/path/to/config.json",
    default_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    device_map="auto"  # Use "auto" for GPU, "cpu" for CPU
)

# Download a model
manager.download_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Load a model
manager.load_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0", quantization="4bit")

# Generate text
response, metadata = manager.generate(
    prompt="Write a function to calculate the factorial of a number.",
    model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    system_prompt="You are a helpful coding assistant.",
    temperature=0.7,
    max_new_tokens=100
)

# Unload a model
manager.unload_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# List available models
available_models = manager.list_available_models()

# List loaded models
loaded_models = manager.list_loaded_models()

# Set default model
manager.set_default_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
```

## Model Configuration

The model manager uses a configuration file to store information about models. The configuration file is a JSON file with the following structure:

```json
{
  "models": {
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0": {
      "description": "TinyLlama 1.1B Chat model",
      "quantization": "4bit",
      "default_parameters": {
        "temperature": 0.7,
        "top_p": 0.95,
        "max_new_tokens": 1024
      }
    }
  },
  "default_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
}
```

## Model Types

The model manager supports various model types, including:

- LLaMA models (including TinyLlama)
- Mistral models
- GPT models
- BERT models
- RoBERTa models
- T5 models
- Falcon models
- BLOOM models
- OPT models
- Gemma models

## Prompt Formatting

The model manager automatically formats prompts based on the model type. For example:

- For Mistral models: `<s>[INST] {system_prompt}\n\n{prompt} [/INST]`
- For LLaMA Instruct models: `<s>[INST] {system_prompt}\n\n{prompt} [/INST]`
- For TinyLlama models: `<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>`

## Response Cleaning

The model manager automatically cleans responses based on the model type. For example:

- For Mistral models: Removes any trailing `[INST]` tags
- For TinyLlama models: Removes any trailing `<|user|>` or `<|system|>` tags

## Quantization

The model manager supports various quantization methods:

- `4bit`: 4-bit quantization (default)
- `8bit`: 8-bit quantization
- `none`: No quantization

## Device Mapping

The model manager supports various device mapping options:

- `auto`: Automatically determine the best device mapping
- `cpu`: Use CPU only
- `cuda:0`: Use the first CUDA device
- `cuda:1`: Use the second CUDA device
- etc.

## Best Practices

1. **Use 4-bit Quantization for Large Models**: For large models, use 4-bit quantization to reduce memory usage.

2. **Unload Models When Not in Use**: Unload models when they're not in use to free up memory.

3. **Use System Prompts**: Use system prompts to provide context to the model.

4. **Set Appropriate Generation Parameters**: Set appropriate generation parameters based on the task.

5. **Handle Model-Specific Formatting**: The model manager handles model-specific formatting, but be aware of the differences between models.

## Troubleshooting

### Model Loading Issues

If you encounter issues loading a model, try the following:

1. Check that the model is downloaded correctly
2. Try a different quantization method
3. Check that you have enough memory
4. Check that the model is compatible with the current version of transformers

### Model Type Issues

If you encounter issues with model types, the model manager will attempt to infer the model type from the model ID. If this fails, you can manually set the model type in the config.json file.

### Memory Issues

If you encounter memory issues, try the following:

1. Use 4-bit quantization
2. Unload models when not in use
3. Use a smaller model
4. Use CPU instead of GPU

## References

- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/index)
- [Hugging Face Hub](https://huggingface.co/models)
- [BitsAndBytes Documentation](https://huggingface.co/docs/transformers/main_classes/quantization)
