# Building Agents with Augment Adam

This guide explains how to build specialized agents using Augment Adam.

## Introduction

In Augment Adam, agents represent an LLM with a system prompt, output instructions, and other inference characteristics. Agents may have specialized tools and can be deployed as MCP servers via fastapi-mcp.

Agents come in two varieties:
- **Synchronous Agents**: Regular agents that process requests synchronously
- **Asynchronous Agents (Workers)**: Agents that process tasks asynchronously

## Agent Components

An agent consists of the following components:

1. **Model**: The underlying LLM used by the agent
2. **System Prompt**: Instructions that guide the agent's behavior
3. **Output Format**: The format for agent responses (text or JSON)
4. **Tools**: Specialized functions that the agent can use
5. **Inference Settings**: Parameters like temperature, top_p, etc.

## Creating a Basic Agent

Here's how to create a basic agent:

```python
from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent

# Create a model
model = create_model(
    model_type="huggingface",
    model_size="small_context"
)

# Create an agent
agent = create_agent(
    agent_type="conversational",
    name="My Agent",
    description="A helpful AI assistant",
    model=model,
    system_prompt="You are a helpful AI assistant...",
    output_format="text"
)

# Process a request
result = agent.process("Hello, how are you?")
print(result["response"])
```

## System Prompts

The system prompt is a critical component that guides the agent's behavior. It should include:

1. **Role Definition**: What the agent is and what it does
2. **Behavioral Guidelines**: How the agent should respond
3. **Output Instructions**: Format for responses
4. **Constraints**: Any limitations or restrictions

Example system prompt:

```
You are a helpful AI assistant specialized in answering questions about Python programming.

Your goal is to provide accurate, concise, and helpful responses to user queries.
Always include code examples when appropriate.

When you don't know something, admit it rather than making up information.
Always be respectful and professional in your responses.
```

## Output Formats

Agents support two output formats:

1. **Text**: Simple text responses
2. **JSON**: Structured JSON responses

For JSON output, you should specify the expected structure in the system prompt:

```python
agent = create_agent(
    # ...
    output_format="json",
    strict_output=True,  # Enforce valid JSON
    system_prompt="""
    You must respond in valid JSON format with the following structure:
    {
        "response": "Your response text here",
        "confidence": 0.9,
        "sources": []
    }
    """
)
```

## Tools

Tools are specialized functions that agents can use to perform specific tasks. Each tool has:

1. **Name**: Identifier for the tool
2. **Description**: What the tool does
3. **Parameters**: Inputs for the tool
4. **Execute Method**: Function that performs the tool's action

Example tool:

```python
from augment_adam.ai_agent.tools import Tool

class CalculatorTool(Tool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic arithmetic calculations",
            parameters={
                "expression": {
                    "type": "str",
                    "description": "The arithmetic expression to evaluate",
                    "required": True
                }
            }
        )
    
    def execute(self, expression: str):
        try:
            result = eval(expression)
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e), "expression": expression}

# Add tool to agent
calculator_tool = CalculatorTool()
agent.add_tool(calculator_tool)
```

## Worker Agents

Worker agents process tasks asynchronously, which is useful for long-running tasks:

```python
# Create a worker agent
worker = create_agent(
    agent_type="worker",
    name="Worker Agent",
    description="A worker agent for async processing",
    model=model,
    max_concurrent_tasks=3  # Process up to 3 tasks concurrently
)

# Start the worker
await worker.start()

# Submit a task
task_id = await worker.submit_task("Analyze this data...")

# Check task status
status = worker.get_task_status(task_id)
print(status["status"])  # "queued", "processing", "completed", or "error"

# Get task result when completed
if status["status"] == "completed":
    print(status["result"]["response"])

# Stop the worker when done
await worker.stop()
```

## MCP Agents

MCP agents are designed to be deployed as MCP servers via fastapi-mcp:

```python
# Create an MCP agent
mcp_agent = create_agent(
    agent_type="mcp",
    name="MCP Agent",
    description="An MCP agent for server deployment",
    model=model,
    output_format="json",
    strict_output=True
)

# Get MCP schema
schema = mcp_agent.get_mcp_schema()
```

## Deploying Agents as Servers

Agents can be deployed as FastAPI servers:

```python
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()
agent_registry = {"my_agent": agent}

@app.post("/agents/{agent_id}/process")
async def process_input(agent_id: str, request: Request):
    agent = agent_registry[agent_id]
    data = await request.json()
    result = agent.process(data["input"])
    return result

uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Best Practices

1. **Keep Tool Lists Digestible**: LLMs struggle with too many tools, so keep the list manageable
2. **Use Specialized Agents**: Create agents for specific tasks rather than one agent for everything
3. **Optimize System Prompts**: Spend time refining system prompts for better performance
4. **Use JSON for Structured Data**: When you need structured responses, use JSON output format
5. **Test Thoroughly**: Test agents with a variety of inputs to ensure they behave as expected
6. **Monitor Performance**: Keep track of agent performance and adjust as needed

## Examples

See the examples directory for complete examples:

- `simple_agent_example.py`: Basic agent with system prompt
- `worker_agent_example.py`: Asynchronous worker agent
- `mcp_server_example.py`: MCP server with agents

## Conclusion

Agents are a powerful way to create specialized AI assistants with Augment Adam. By combining models, system prompts, and tools, you can create agents that excel at specific tasks and deploy them as servers for client use.
