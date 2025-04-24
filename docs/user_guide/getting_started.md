# Getting Started with Dukat v0.1.0

*Last updated: 2025-04-22*

This guide will help you get started with Dukat, an open-source AI assistant focused on personal automation.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.10 or higher
- [Ollama](https://ollama.ai/) for running models locally

## Installation

### 1. Install Dukat

You can install Dukat using pip:

```bash
pip install augment-adam
```

Or, if you prefer to install from source:

```bash
git clone https://github.com/augment-adam/augment-adam.git
cd augment-adam
pip install -e .
```

### 2. Set Up Ollama

If you haven't already, install Ollama:

```bash
# On Linux or macOS
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows, download from https://ollama.ai/download
```

Then, pull a model:

```bash
ollama pull llama3:8b
```

## Configuration

Dukat can be configured through a `config.yaml` file in your home directory:

```yaml
# ~/.augment_adam/config.yaml
model: llama3:8b  # Model to use for inference
ollama_host: http://localhost:11434  # Ollama API endpoint
memory:
  vector_db: chroma  # Vector database for memory (chroma or faiss)
  persist_dir: ~/.augment_adam/memory  # Directory to store memory
log_level: INFO  # Logging level
```

## Basic Usage

### Command Line Interface

To start the Dukat CLI:

```bash
augment-adam
```

This will launch an interactive session where you can chat with the assistant.

### Web Interface

To start the Dukat web interface:

```bash
augment-adam web
```

This will start a web server at http://localhost:7860 where you can interact with the assistant through a browser.

### Python API

You can also use Dukat programmatically in your Python code:

```python
from augment_adam.core import Assistant

# Initialize the assistant
assistant = Assistant()

# Ask a question
response = assistant.ask("What can you help me with?")
print(response)

# Start a new conversation
assistant.new_conversation()

# Ask another question
response = assistant.ask("Tell me about DSPy.")
print(response)
```

## Next Steps

- Check out the [API Documentation](../api/index.md) for more details on using Dukat programmatically
- Learn about [Creating Plugins](plugins.md) to extend Dukat's capabilities
- Explore [Advanced Configuration](configuration.md) options

## Troubleshooting

### Common Issues

#### Ollama Connection Error

If you see an error like "Failed to connect to Ollama", make sure:

1. Ollama is running (`ollama serve`)
2. The Ollama host in your config is correct
3. You have pulled the model you're trying to use

#### Memory Errors

If you encounter memory-related errors:

1. Check that the memory directory exists and is writable
2. Try clearing the memory: `rm -rf ~/.augment_adam/memory/*`
3. Ensure you have enough disk space

### Getting Help

If you encounter any issues not covered here, please:

1. Check the [FAQ](faq.md) for common questions
2. Search for similar issues in the [GitHub repository](https://github.com/yourusername/augment_adam/issues)
3. Open a new issue if your problem is not already reported
