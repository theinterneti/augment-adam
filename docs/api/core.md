# Dukat Core API Reference v0.1.0

*Last updated: 2025-04-22*

This document provides reference information for the core API of Dukat.

## Assistant

The `Assistant` class is the main entry point for interacting with Dukat programmatically.

```python
from dukat.core import Assistant

assistant = Assistant(
    model_name="llama3:8b",
    ollama_host="http://localhost:11434",
    persist_dir=None,
    conversation_id=None,
)
```

### Parameters

- `model_name` (str, optional): The name of the model to use. Default: "llama3:8b"
- `ollama_host` (str, optional): The host address for the Ollama API. Default: "http://localhost:11434"
- `persist_dir` (str, optional): Directory to persist memory data. Default: None (uses "~/.dukat/memory")
- `conversation_id` (str, optional): The ID of the conversation to continue. Default: None (generates a new ID)

### Methods

#### `ask(question, include_history=True, max_history_items=5)`

Ask a question to the assistant.

```python
response = assistant.ask("What is DSPy?")
print(response)
```

**Parameters:**
- `question` (str): The question to ask.
- `include_history` (bool, optional): Whether to include conversation history. Default: True
- `max_history_items` (int, optional): Maximum number of history items to include. Default: 5

**Returns:**
- `str`: The assistant's response.

#### `new_conversation()`

Start a new conversation.

```python
conversation_id = assistant.new_conversation()
```

**Returns:**
- `str`: The ID of the new conversation.

#### `get_conversation_history(max_items=10)`

Get the history of the current conversation.

```python
history = assistant.get_conversation_history()
for item in history:
    print(f"{item['type']}: {item['text']}")
```

**Parameters:**
- `max_items` (int, optional): Maximum number of history items to return. Default: 10

**Returns:**
- `List[Dict[str, Any]]`: A list of conversation messages with metadata.

## ModelManager

The `ModelManager` class handles loading, configuring, and using language models through DSPy and Ollama.

```python
from dukat.core.model_manager import ModelManager, get_model_manager

# Create a new instance
model_manager = ModelManager(
    model_name="llama3:8b",
    ollama_host="http://localhost:11434",
    api_key="",
)

# Or get the default instance
model_manager = get_model_manager()
```

### Parameters

- `model_name` (str, optional): The name of the model to use. Default: "llama3:8b"
- `ollama_host` (str, optional): The host address for the Ollama API. Default: "http://localhost:11434"
- `api_key` (str, optional): The API key for the model provider (not needed for Ollama). Default: ""

### Methods

#### `generate_response(prompt, **kwargs)`

Generate a response from the language model.

```python
response = model_manager.generate_response("What is DSPy?")
print(response)
```

**Parameters:**
- `prompt` (str): The prompt to send to the model.
- `**kwargs`: Additional arguments to pass to the model.

**Returns:**
- `str`: The generated response.

#### `create_module(signature)`

Create a DSPy module with the specified signature.

```python
module = model_manager.create_module("question -> answer")
prediction = module(question="What is DSPy?")
print(prediction.answer)
```

**Parameters:**
- `signature` (str): The signature for the module.

**Returns:**
- `dspy.Module`: A DSPy module instance.

## Memory

The `Memory` class provides the core memory management functionality for storing and retrieving information across conversations.

```python
from dukat.core.memory import Memory, get_memory

# Create a new instance
memory = Memory(
    persist_dir=None,
    collection_name="dukat_memory",
)

# Or get the default instance
memory = get_memory()
```

### Parameters

- `persist_dir` (str, optional): Directory to persist memory data. Default: None (uses "~/.dukat/memory")
- `collection_name` (str, optional): Name of the default collection. Default: "dukat_memory"

### Methods

#### `add(text, metadata=None, collection_name="main", id_prefix="mem")`

Add a memory to the specified collection.

```python
memory_id = memory.add(
    text="This is a test memory",
    metadata={"type": "note", "tags": ["test", "example"]},
)
```

**Parameters:**
- `text` (str): The text content to store.
- `metadata` (Dict[str, Any], optional): Additional metadata for the memory. Default: None
- `collection_name` (str, optional): Name of the collection to store in. Default: "main"
- `id_prefix` (str, optional): Prefix for the generated ID. Default: "mem"

**Returns:**
- `str`: The ID of the stored memory.

#### `retrieve(query, n_results=5, collection_name="main", filter_metadata=None)`

Retrieve memories based on a query.

```python
results = memory.retrieve(
    query="test memory",
    n_results=3,
    filter_metadata={"type": "note"},
)
```

**Parameters:**
- `query` (str): The query text to search for.
- `n_results` (int, optional): Number of results to return. Default: 5
- `collection_name` (str, optional): Name of the collection to search in. Default: "main"
- `filter_metadata` (Dict[str, Any], optional): Metadata filters to apply. Default: None

**Returns:**
- `List[Dict[str, Any]]`: A list of matching memories with their metadata.

#### `get_by_id(memory_id, collection_name="main")`

Retrieve a specific memory by ID.

```python
memory_item = memory.get_by_id("mem_20250422123456")
```

**Parameters:**
- `memory_id` (str): The ID of the memory to retrieve.
- `collection_name` (str, optional): Name of the collection to search in. Default: "main"

**Returns:**
- `Dict[str, Any]`: The memory with its metadata, or None if not found.

#### `delete(memory_id, collection_name="main")`

Delete a memory by ID.

```python
success = memory.delete("mem_20250422123456")
```

**Parameters:**
- `memory_id` (str): The ID of the memory to delete.
- `collection_name` (str, optional): Name of the collection to delete from. Default: "main"

**Returns:**
- `bool`: True if successful, False otherwise.

#### `clear(collection_name="main")`

Clear all memories from a collection.

```python
success = memory.clear()
```

**Parameters:**
- `collection_name` (str, optional): Name of the collection to clear. Default: "main"

**Returns:**
- `bool`: True if successful, False otherwise.

## Config

The `Config` class handles loading, validating, and providing access to configuration settings for the Dukat assistant.

```python
from dukat.config import Config, load_config, save_config, get_config

# Create a new instance
config = Config(
    model="llama3:8b",
    ollama_host="http://localhost:11434",
)

# Load from a file
config = load_config("~/.dukat/config.yaml")

# Save to a file
save_config(config, "~/.dukat/config.yaml")

# Get the default instance
config = get_config()
```

### Methods

#### `load_config(config_path=None)`

Load configuration from a file.

```python
config = load_config("~/.dukat/config.yaml")
```

**Parameters:**
- `config_path` (str, optional): Path to the configuration file. Default: None (uses default path)

**Returns:**
- `Config`: The loaded configuration.

#### `save_config(config, config_path=None)`

Save configuration to a file.

```python
save_config(config, "~/.dukat/config.yaml")
```

**Parameters:**
- `config` (Config): The configuration to save.
- `config_path` (str, optional): Path to the configuration file. Default: None (uses default path)

**Returns:**
- `bool`: True if successful, False otherwise.

#### `get_config(config_path=None)`

Get or load the configuration.

```python
config = get_config()
```

**Parameters:**
- `config_path` (str, optional): Path to the configuration file. Default: None (uses default path)

**Returns:**
- `Config`: The loaded configuration.
