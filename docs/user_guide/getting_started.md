# Getting Started

This guide explains how to get started with Augment Adam.

## Installation

Before you can use Augment Adam, you need to install it. You can install it using pip:

```python
pip install augment-adam
```

### Development Installation

If you want to contribute to Augment Adam, you can install it in development mode:

```python
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam
pip install -e ".[dev]"
```

## Basic Usage

Once you have installed Augment Adam, you can start using it. Here's a simple example:

```python
from augment_adam.core import Assistant

# Create an assistant
assistant = Assistant()

# Chat with the assistant
response = assistant.chat("Hello, how are you?")
print(response)
```

### Using Memory

You can use memory to store and retrieve information:

```python
from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory

# Create a memory
memory = FAISSMemory(path="./data/faiss")

# Create an assistant with memory
assistant = Assistant(memory=memory)

# Chat with the assistant
response = assistant.chat("Remember that my name is Alice.")
print(response)

response = assistant.chat("What's my name?")
print(response)
```

### Using Models

You can use different models with the assistant:

```python
from augment_adam.core import Assistant
from augment_adam.models import OpenAIModel

# Create a model
model = OpenAIModel(api_key="your-api-key", model_name="gpt-4")

# Create an assistant with the model
assistant = Assistant(model=model)

# Chat with the assistant
response = assistant.chat("What is the capital of France?")
print(response)
```

## Using the Context Engine

The context engine helps the assistant understand the context of the conversation:

```python
from augment_adam.core import Assistant
from augment_adam.context_engine import ContextEngine

# Create a context engine
context_engine = ContextEngine()

# Add documents to the context engine
context_engine.add_document("France is a country in Western Europe. Its capital is Paris.")
context_engine.add_document("Paris is known for the Eiffel Tower and the Louvre Museum.")

# Create an assistant with the context engine
assistant = Assistant(context_engine=context_engine)

# Chat with the assistant
response = assistant.chat("What is the capital of France?")
print(response)

response = assistant.chat("What is it known for?")
print(response)
```

## Using Plugins

You can extend the assistant's capabilities with plugins:

```python
from augment_adam.core import Assistant
from augment_adam.plugins import FileManagerPlugin, WebSearchPlugin

# Create plugins
file_manager = FileManagerPlugin()
web_search = WebSearchPlugin(api_key="your-api-key")

# Create an assistant with plugins
assistant = Assistant(plugins=[file_manager, web_search])

# Chat with the assistant
response = assistant.chat("Create a file called hello.txt with the content 'Hello, World!'")
print(response)

response = assistant.chat("Search for information about Python programming language")
print(response)
```

## Using Agents

You can use multiple agents to work together:

```python
from augment_adam.core import Assistant
from augment_adam.ai_agent import MCPAgent, WorkerAgent

# Create agents
mcp_agent = MCPAgent()
worker_agent = WorkerAgent()

# Create an assistant with agents
assistant = Assistant(agents=[mcp_agent, worker_agent])

# Chat with the assistant
response = assistant.chat("Solve this complex problem: What is the optimal strategy for the Prisoner's Dilemma?")
print(response)
```



## Examples

### Simple Conversation

A simple conversation with the assistant.

```python
from augment_adam.core import Assistant

# Create an assistant
assistant = Assistant()

# Chat with the assistant
response = assistant.chat("Hello, how are you?")
print(f"Assistant: {response}")

response = assistant.chat("What can you do?")
print(f"Assistant: {response}")

response = assistant.chat("Tell me a joke.")
print(f"Assistant: {response}")
```

Output:
```
Assistant: I'm doing well, thank you for asking! How can I help you today?

Assistant: I can assist you with a variety of tasks, including answering questions, generating text, providing information, and having conversations. I can also help with more specific tasks like coding, writing, summarizing, and creative content generation. What would you like help with?

Assistant: Why don't scientists trust atoms? Because they make up everything!
```

### Using Memory and Context

Using memory and context to maintain a conversation.

```python
from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory
from augment_adam.context_engine import ContextEngine

# Create a memory
memory = FAISSMemory(path="./data/faiss")

# Create a context engine
context_engine = ContextEngine()
context_engine.add_document("Alice is a software engineer who likes Python and machine learning.")

# Create an assistant with memory and context
assistant = Assistant(memory=memory, context_engine=context_engine)

# Chat with the assistant
response = assistant.chat("Hi, I'm Alice.")
print(f"Assistant: {response}")

response = assistant.chat("What do I do for a living?")
print(f"Assistant: {response}")

response = assistant.chat("What programming languages do I like?")
print(f"Assistant: {response}")
```

Output:
```
Assistant: Hello Alice! It's nice to meet you. How can I assist you today?

Assistant: You're a software engineer, Alice.

Assistant: Based on the information I have, you like Python as a programming language. You're also interested in machine learning.
```



## Troubleshooting

### Installation Errors

If you encounter errors during installation, make sure you have the latest version of pip and the required dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you're still having issues, check the error message for specific dependency problems.

### API Key Errors

If you're using a model that requires an API key (like OpenAI or Anthropic), make sure you've set the API key correctly:

```python
from augment_adam.models import OpenAIModel

# Create a model with your API key
model = OpenAIModel(api_key="your-api-key")
```

You can also set the API key as an environment variable:

```bash
export AUGMENT_ADAM_API_KEY=your-api-key
```

### Memory Persistence Issues

If you're having issues with memory persistence, make sure the directory exists and is writable:

```python
import os
from augment_adam.memory import FAISSMemory

# Create the directory if it doesn't exist
os.makedirs("./data/faiss", exist_ok=True)

# Create a memory
memory = FAISSMemory(path="./data/faiss")
```



## Next Steps

- [Configuration](configuration.md): Learn how to configure Augment Adam
- [Memory System](../architecture/MEMORY_SYSTEM.md): Learn about the memory system architecture
- [Context Engine](../architecture/CONTEXT_ENGINE.md): Learn about the context engine architecture
- [Agent Coordination](agent_coordination.md): Learn how to coordinate multiple agents

