# Dukat Core API Reference v0.3.0

_Last updated: 2025-04-27_

This document provides reference information for the core API of Dukat.

## Additional Documentation

- [Parallel Execution](core/parallel_execution.md): Documentation for the parallel execution system
- [Task Scheduling](core/task_scheduling.md): Documentation for the task scheduling system
- [Circuit Breakers](core/circuit_breakers.md): Documentation for the circuit breaker pattern

## Assistant

The `Assistant` class is the main entry point for interacting with Dukat programmatically.

```python
from augment_adam.core import Assistant

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
- `persist_dir` (str, optional): Directory to persist memory data. Default: None (uses "~/.augment_adam/memory")
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
from augment_adam.core.model_manager import ModelManager, get_model_manager

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
from augment_adam.core.memory import Memory, get_memory

# Create a new instance
memory = Memory(
    persist_dir=None,
    collection_name="augment_adam_memory",
)

# Or get the default instance
memory = get_memory()
```

### Parameters

- `persist_dir` (str, optional): Directory to persist memory data. Default: None (uses "~/.augment_adam/memory")
- `collection_name` (str, optional): Name of the default collection. Default: "augment_adam_memory"

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
from augment_adam.config import Config, load_config, save_config, get_config

# Create a new instance
config = Config(
    model="llama3:8b",
    ollama_host="http://localhost:11434",
)

# Load from a file
config = load_config("~/.augment_adam/config.yaml")

# Save to a file
save_config(config, "~/.augment_adam/config.yaml")

# Get the default instance
config = get_config()
```

### Methods

#### `load_config(config_path=None)`

Load configuration from a file.

```python
config = load_config("~/.augment_adam/config.yaml")
```

**Parameters:**

- `config_path` (str, optional): Path to the configuration file. Default: None (uses default path)

**Returns:**

- `Config`: The loaded configuration.

#### `save_config(config, config_path=None)`

Save configuration to a file.

```python
save_config(config, "~/.augment_adam/config.yaml")
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

## AsyncAssistant

The `AsyncAssistant` class is an asynchronous version of the `Assistant` class that integrates with the task queue system for background processing.

```python
import asyncio
from augment_adam.core import AsyncAssistant, get_async_assistant

async def main():
    # Create a new instance
    assistant = AsyncAssistant(
        model_name="llama3:8b",
        ollama_host="http://localhost:11434",
        max_messages=100,
        conversation_id=None,
        max_parallel_tasks=5,
    )

    # Or get an instance with the task queue started
    assistant = await get_async_assistant(
        model_name="llama3:8b",
        ollama_host="http://localhost:11434",
        max_parallel_tasks=5,
    )

    # Use the assistant
    await assistant.add_message("Hello, how are you?")
    response = await assistant.generate_response()
    print(response)

# Run the async function
asyncio.run(main())
```

> **Note on Event Loops**: The `AsyncAssistant` class uses the current event loop for all asynchronous operations. When creating an instance, it automatically gets the current event loop using `asyncio.get_event_loop()`. For more information on working with event loops, see the [Asynchronous Programming and Event Loops](core/async_event_loops.md) documentation.

### Parameters

- `model_name` (str, optional): The name of the model to use. Default: "llama3:8b"
- `ollama_host` (str, optional): The host address for the Ollama API. Default: "http://localhost:11434"
- `max_messages` (int, optional): Maximum number of messages to keep in memory. Default: 100
- `conversation_id` (str, optional): The ID of the conversation to continue. Default: None (generates a new ID)
- `max_parallel_tasks` (int, optional): Maximum number of tasks to execute in parallel. Default: 5

### Methods

#### `add_message(content, role="user", metadata=None)`

Add a message to the conversation asynchronously.

```python
message = await assistant.add_message(
    content="Hello, how are you?",
    role="user",
    metadata={"source": "web_interface"},
)
```

**Parameters:**

- `content` (Union[str, Message]): The content of the message or a Message object.
- `role` (str, optional): The role of the sender (user, assistant, system). Default: "user"
- `metadata` (Dict[str, Any], optional): Additional metadata for the message. Default: None

**Returns:**

- `Message`: The added message.

#### `generate_response(system_prompt=None, max_tokens=1024, temperature=0.7, timeout=30.0, priority=10)`

Generate a response asynchronously.

```python
response = await assistant.generate_response(
    system_prompt="You are a helpful assistant.",
    max_tokens=1024,
    temperature=0.7,
    timeout=30.0,
)
```

**Parameters:**

- `system_prompt` (str, optional): Optional system prompt to use. Default: None
- `max_tokens` (int, optional): Maximum number of tokens to generate. Default: 1024
- `temperature` (float, optional): Temperature for generation. Default: 0.7
- `timeout` (float, optional): Maximum time to wait for generation. Default: 30.0
- `priority` (int, optional): Priority of the generation task. Default: 10

**Returns:**

- `str`: The generated response.

#### `search_memory(query, n_results=5, filter_metadata=None)`

Search memory for relevant messages asynchronously.

```python
results = await assistant.search_memory(
    query="hello",
    n_results=5,
    filter_metadata={"role": "user"},
)
```

**Parameters:**

- `query` (str): The search query.
- `n_results` (int, optional): Maximum number of results to return. Default: 5
- `filter_metadata` (Dict[str, Any], optional): Metadata filters to apply. Default: None

**Returns:**

- `List[Dict[str, Any]]`: A list of relevant messages.

#### `clear_messages()`

Clear all messages from memory asynchronously.

```python
await assistant.clear_messages()
```

#### `new_conversation()`

Start a new conversation asynchronously.

```python
conversation_id = await assistant.new_conversation()
```

**Returns:**

- `str`: The ID of the new conversation.

#### `save_conversation(file_path)`

Save the conversation to a file asynchronously.

```python
success = await assistant.save_conversation("conversation.json")
```

**Parameters:**

- `file_path` (str): The path to save the file.

**Returns:**

- `bool`: True if successful, False otherwise.

#### `load_conversation(file_path)`

Load a conversation from a file asynchronously.

```python
success = await assistant.load_conversation("conversation.json")
```

**Parameters:**

- `file_path` (str): The path to load the file from.

**Returns:**

- `bool`: True if successful, False otherwise.

#### `get_active_tasks()`

Get information about active tasks asynchronously.

```python
tasks = await assistant.get_active_tasks()
```

**Returns:**

- `Dict[str, Dict[str, Any]]`: A dictionary mapping task IDs to task information.

#### `cancel_active_tasks()`

Cancel all active tasks asynchronously.

```python
count = await assistant.cancel_active_tasks()
```

**Returns:**

- `int`: The number of tasks cancelled.

#### `get_messages(n=None, roles=None, reverse=False)`

Get messages from the conversation asynchronously.

```python
messages = await assistant.get_messages(
    n=10,
    roles=["user", "assistant"],
    reverse=False,
)
```

**Parameters:**

- `n` (int, optional): Maximum number of messages to return. Default: None (all messages)
- `roles` (List[str], optional): Only return messages with these roles. Default: None (all roles)
- `reverse` (bool, optional): Whether to return messages in reverse order. Default: False

**Returns:**

- `List[Message]`: A list of messages.

#### `get_last_message(role=None)`

Get the last message in the conversation asynchronously.

```python
message = await assistant.get_last_message(role="user")
```

**Parameters:**

- `role` (str, optional): Only return a message with this role. Default: None (any role)

**Returns:**

- `Optional[Message]`: The last message, or None if there are no messages.

#### `format_history(n=None, include_roles=True, separator="\n")`

Format the conversation history as a string asynchronously.

```python
history = await assistant.format_history(
    n=10,
    include_roles=True,
    separator="\n",
)
```

**Parameters:**

- `n` (int, optional): Maximum number of messages to include. Default: None (all messages)
- `include_roles` (bool, optional): Whether to include roles in the output. Default: True
- `separator` (str, optional): The separator between messages. Default: "\n"

**Returns:**

- `str`: The formatted conversation history.

#### `get_queue_stats()`

Get statistics about the task queue asynchronously.

```python
stats = await assistant.get_queue_stats()
```

**Returns:**

- `Dict[str, Any]`: A dictionary with queue statistics.

#### `execute_tasks_in_parallel(tasks, max_concurrency=None)`

Execute multiple tasks in parallel.

```python
results = await assistant.execute_tasks_in_parallel([
    {
        "func": task_1,
        "task_id": "task_1",
        "description": "Task 1",
    },
    {
        "func": task_2,
        "task_id": "task_2",
        "description": "Task 2",
        "dependencies": ["task_1"],  # This task depends on task_1
    },
])
```

**Parameters:**

- `tasks` (List[Dict[str, Any]]): List of task definitions. Each task should have:
  - `func`: The function to execute
  - `args`: List of positional arguments (optional)
  - `kwargs`: Dictionary of keyword arguments (optional)
  - `task_id`: Task ID (optional)
  - `priority`: Task priority (optional)
  - `timeout`: Task timeout (optional)
  - `dependencies`: List of task IDs that this task depends on (optional)
  - `resource_requirements`: List of resource requirements (optional)
  - `circuit_breaker_name`: Name of the circuit breaker to use (optional)
- `max_concurrency` (int, optional): Maximum number of tasks to execute concurrently. Default: None (uses self.max_parallel_tasks)

**Returns:**

- `Dict[str, Any]`: A dictionary mapping task IDs to results.

#### `schedule_periodic_task(func, interval, args=None, kwargs=None, task_id=None, max_runs=None, priority=0, timeout=None, retry_count=0, retry_delay=1.0, description="", task_type="periodic_task")`

Schedule a task to run periodically.

```python
task_id = await assistant.schedule_periodic_task(
    func=my_function,
    interval=timedelta(minutes=10),
    args=[arg1, arg2],
    kwargs={"key": "value"},
    max_runs=5,
    description="Run my_function every 10 minutes, 5 times",
)
```

**Parameters:**

- `func` (Union[Callable[..., Any], Callable[..., Awaitable[Any]]]): The function to execute.
- `interval` (Union[float, timedelta]): The interval between runs.
- `args` (List[Any], optional): Positional arguments to pass to the function. Default: None
- `kwargs` (Dict[str, Any], optional): Keyword arguments to pass to the function. Default: None
- `task_id` (str, optional): A unique identifier for the task. Default: None (generates a UUID)
- `max_runs` (int, optional): Maximum number of times to run the task. Default: None (runs indefinitely)
- `priority` (int, optional): The priority of the task. Higher values indicate higher priority. Default: 0
- `timeout` (float, optional): Maximum time in seconds to wait for the task to complete. Default: None
- `retry_count` (int, optional): Number of times to retry the task if it fails. Default: 0
- `retry_delay` (float, optional): Delay in seconds between retries. Default: 1.0
- `description` (str, optional): Description of the task. Default: ""
- `task_type` (str, optional): Type of the task for tracking purposes. Default: "periodic_task"

**Returns:**

- `str`: The ID of the scheduled task.

#### `schedule_task_at_time(func, schedule_time, args=None, kwargs=None, task_id=None, priority=0, timeout=None, retry_count=0, retry_delay=1.0, description="", task_type="scheduled_task")`

Schedule a task to run at a specific time.

```python
task_id = await assistant.schedule_task_at_time(
    func=my_function,
    schedule_time=datetime.now() + timedelta(minutes=5),
    args=[arg1, arg2],
    kwargs={"key": "value"},
    description="Run my_function in 5 minutes",
)
```

**Parameters:**

- `func` (Union[Callable[..., Any], Callable[..., Awaitable[Any]]]): The function to execute.
- `schedule_time` (Union[float, datetime]): The time to run the task.
- `args` (List[Any], optional): Positional arguments to pass to the function. Default: None
- `kwargs` (Dict[str, Any], optional): Keyword arguments to pass to the function. Default: None
- `task_id` (str, optional): A unique identifier for the task. Default: None (generates a UUID)
- `priority` (int, optional): The priority of the task. Higher values indicate higher priority. Default: 0
- `timeout` (float, optional): Maximum time in seconds to wait for the task to complete. Default: None
- `retry_count` (int, optional): Number of times to retry the task if it fails. Default: 0
- `retry_delay` (float, optional): Delay in seconds between retries. Default: 1.0
- `description` (str, optional): Description of the task. Default: ""
- `task_type` (str, optional): Type of the task for tracking purposes. Default: "scheduled_task"

**Returns:**

- `str`: The ID of the scheduled task.

#### `cancel_scheduled_task(task_id)`

Cancel a scheduled task.

```python
cancelled = await assistant.cancel_scheduled_task(task_id)
```

**Parameters:**

- `task_id` (str): The ID of the task to cancel.

**Returns:**

- `bool`: True if the task was cancelled, False otherwise.

## TaskQueue

The `TaskQueue` class provides a system for asynchronous processing of tasks in the background.

```python
import asyncio
from augment_adam.core import TaskQueue, Task, add_task, wait_for_task, get_task_queue

async def my_task(x, y):
    await asyncio.sleep(1)  # Simulate some work
    return x + y

async def main():
    # Create a new instance
    queue = TaskQueue(
        max_workers=5,
        max_queue_size=100,
    )

    # Or get the default instance
    queue = get_task_queue()

    # Start the queue
    await queue.start()

    # Add a task
    task = await queue.add_task(
        func=my_task,
        args=[5, 10],
        task_id="addition_task",
        priority=10,
        timeout=5.0,
        retry_count=3,
        retry_delay=1.0,
    )

    # Or use the global function
    task = await add_task(
        func=my_task,
        args=[5, 10],
        task_id="addition_task",
        priority=10,
        timeout=5.0,
        retry_count=3,
        retry_delay=1.0,
    )

    # Wait for the task to complete
    result = await wait_for_task("addition_task", timeout=10.0)
    print(f"Result: {result}")  # Output: Result: 15

    # Stop the queue
    await queue.stop()

# Run the async function
asyncio.run(main())
```

### Parameters

- `max_workers` (int, optional): Maximum number of worker tasks to run concurrently. Default: 5
- `max_queue_size` (int, optional): Maximum number of tasks to queue. Default: 100

### Methods

#### `start()`

Start the task queue.

```python
await queue.start()
```

#### `stop()`

Stop the task queue.

```python
await queue.stop()
```

#### `add_task(func, args=None, kwargs=None, task_id=None, priority=0, timeout=None, retry_count=0, retry_delay=1.0, dependencies=None)`

Add a task to the queue.

```python
task = await queue.add_task(
    func=my_task,
    args=[5, 10],
    task_id="addition_task",
    priority=10,
    timeout=5.0,
    retry_count=3,
    retry_delay=1.0,
    dependencies=["other_task"],
)
```

**Parameters:**

- `func` (Union[Callable[..., Any], Callable[..., Awaitable[Any]]]): The function to execute.
- `args` (List[Any], optional): Positional arguments to pass to the function. Default: None
- `kwargs` (Dict[str, Any], optional): Keyword arguments to pass to the function. Default: None
- `task_id` (str, optional): A unique identifier for the task. Default: None (generates a UUID)
- `priority` (int, optional): The priority of the task. Higher values indicate higher priority. Default: 0
- `timeout` (float, optional): Maximum time in seconds to wait for the task to complete. Default: None
- `retry_count` (int, optional): Number of times to retry the task if it fails. Default: 0
- `retry_delay` (float, optional): Delay in seconds between retries. Default: 1.0
- `dependencies` (List[str], optional): List of task IDs that must complete before this task can run. Default: None

**Returns:**

- `Task`: The created task.

#### `get_task(task_id)`

Get a task by ID.

```python
task = await queue.get_task("addition_task")
```

**Parameters:**

- `task_id` (str): The ID of the task to get.

**Returns:**

- `Optional[Task]`: The task, or None if not found.

#### `cancel_task(task_id)`

Cancel a task.

```python
success = await queue.cancel_task("addition_task")
```

**Parameters:**

- `task_id` (str): The ID of the task to cancel.

**Returns:**

- `bool`: True if the task was cancelled, False otherwise.

#### `wait_for_task(task_id, timeout=None)`

Wait for a task to complete.

```python
result = await queue.wait_for_task("addition_task", timeout=10.0)
```

**Parameters:**

- `task_id` (str): The ID of the task to wait for.
- `timeout` (float, optional): Maximum time in seconds to wait for the task to complete. Default: None

**Returns:**

- `Optional[Any]`: The result of the task, or None if the task was not found or timed out.

#### `get_queue_stats()`

Get statistics about the task queue.

```python
stats = await queue.get_queue_stats()
```

**Returns:**

- `Dict[str, Any]`: A dictionary with queue statistics.
