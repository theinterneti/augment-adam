# Configuration Guide

This guide explains how to configure Augment Adam for your specific needs.

## Configuration Methods

Augment Adam can be configured using several methods:

1. **Environment Variables**: Set environment variables to configure Augment Adam
2. **Configuration File**: Use a YAML or JSON configuration file
3. **Programmatic Configuration**: Configure Augment Adam programmatically

## Environment Variables

You can configure Augment Adam using environment variables:

```bash
# Set the log level
export AUGMENT_ADAM_LOG_LEVEL=INFO

# Set the memory backend
export AUGMENT_ADAM_MEMORY_BACKEND=faiss

# Set the model provider
export AUGMENT_ADAM_MODEL_PROVIDER=openai

# Set the API key for the model provider
export AUGMENT_ADAM_API_KEY=your-api-key
```

## Configuration File

You can create a configuration file in YAML or JSON format:

### YAML Configuration

```yaml
# config.yaml
log_level: INFO
memory:
  backend: faiss
  path: ./data/memory
model:
  provider: openai
  api_key: your-api-key
  model_name: gpt-4
context_engine:
  chunk_size: 1024
  overlap: 128
  embedding_model: text-embedding-ada-002
```

### JSON Configuration

```json
{
  "log_level": "INFO",
  "memory": {
    "backend": "faiss",
    "path": "./data/memory"
  },
  "model": {
    "provider": "openai",
    "api_key": "your-api-key",
    "model_name": "gpt-4"
  },
  "context_engine": {
    "chunk_size": 1024,
    "overlap": 128,
    "embedding_model": "text-embedding-ada-002"
  }
}
```

### Loading a Configuration File

```python
from augment_adam.core.settings import load_config

# Load a configuration file
config = load_config("config.yaml")

# Use the configuration
from augment_adam.core import Assistant
assistant = Assistant(config=config)
```

## Programmatic Configuration

You can configure Augment Adam programmatically:

```python
from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory
from augment_adam.models import OpenAIModel

# Create a memory system
memory = FAISSMemory(path="./data/memory")

# Create a model
model = OpenAIModel(api_key="your-api-key", model_name="gpt-4")

# Create an assistant with custom configuration
assistant = Assistant(
    memory=memory,
    model=model,
    log_level="INFO",
    context_engine_config={
        "chunk_size": 1024,
        "overlap": 128,
        "embedding_model": "text-embedding-ada-002"
    }
)
```

## Configuration Options

### General Configuration

| Option | Description | Default | Environment Variable |
| ------ | ----------- | ------- | ------------------- |
| `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | AUGMENT_ADAM_LOG_LEVEL |
| `data_dir` | Directory for storing data | ./data | AUGMENT_ADAM_DATA_DIR |

### Memory Configuration

| Option | Description | Default | Environment Variable |
| ------ | ----------- | ------- | ------------------- |
| `memory.backend` | Memory backend (faiss, neo4j) | faiss | AUGMENT_ADAM_MEMORY_BACKEND |
| `memory.path` | Path to memory storage | ./data/memory | AUGMENT_ADAM_MEMORY_PATH |
| `memory.neo4j_uri` | Neo4j URI (if using Neo4j) | bolt://localhost:7687 | AUGMENT_ADAM_NEO4J_URI |
| `memory.neo4j_user` | Neo4j username (if using Neo4j) | neo4j | AUGMENT_ADAM_NEO4J_USER |
| `memory.neo4j_password` | Neo4j password (if using Neo4j) | password | AUGMENT_ADAM_NEO4J_PASSWORD |

### Model Configuration

| Option | Description | Default | Environment Variable |
| ------ | ----------- | ------- | ------------------- |
| `model.provider` | Model provider (openai, anthropic, ollama) | openai | AUGMENT_ADAM_MODEL_PROVIDER |
| `model.api_key` | API key for the model provider | None | AUGMENT_ADAM_API_KEY |
| `model.model_name` | Name of the model to use | gpt-4 | AUGMENT_ADAM_MODEL_NAME |
| `model.temperature` | Temperature for model generation | 0.7 | AUGMENT_ADAM_TEMPERATURE |
| `model.max_tokens` | Maximum tokens for model generation | 1024 | AUGMENT_ADAM_MAX_TOKENS |

### Context Engine Configuration

| Option | Description | Default | Environment Variable |
| ------ | ----------- | ------- | ------------------- |
| `context_engine.chunk_size` | Size of chunks for context | 1024 | AUGMENT_ADAM_CHUNK_SIZE |
| `context_engine.overlap` | Overlap between chunks | 128 | AUGMENT_ADAM_CHUNK_OVERLAP |
| `context_engine.embedding_model` | Model for embeddings | text-embedding-ada-002 | AUGMENT_ADAM_EMBEDDING_MODEL |

## Docker Configuration

When using Docker, you can configure Augment Adam using environment variables in your docker-compose.yml file:

```yaml
version: '3'
services:
  augment-adam:
    build: .
    environment:
      - AUGMENT_ADAM_LOG_LEVEL=INFO
      - AUGMENT_ADAM_MEMORY_BACKEND=faiss
      - AUGMENT_ADAM_MODEL_PROVIDER=openai
      - AUGMENT_ADAM_API_KEY=your-api-key
    volumes:
      - ./data:/app/data
```

## Next Steps

After configuring Augment Adam, check out the [Getting Started Guide](getting_started.md) to learn how to use it.
