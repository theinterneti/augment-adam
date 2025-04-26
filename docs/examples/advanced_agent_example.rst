Advanced Agent Example
======================

This document provides advanced examples of using the Agent API.

Agent with Custom Prompt Template
---------------------------------

This example shows how to use an agent with a custom prompt template:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    
    # Initialize context engine
    context_engine = ContextEngine(memory=memory)
    
    # Custom prompt template
    prompt_template = """
    You are a helpful assistant that answers questions based on the provided context.
    
    Context:
    {context}
    
    User: {query}
    
    Please provide a detailed answer to the user's question based on the context.
    If the context doesn't contain the information needed, say "I don't have that information."
    
    Assistant:
    """
    
    # Initialize agent with custom prompt template
    agent = Agent(
        context_engine=context_engine,
        prompt_template=prompt_template
    )
    
    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)

Agent with Tool Use
-------------------

This example shows how to use an agent with tools:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent
    from augment_adam.tools import Tool, ToolRegistry
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    
    # Initialize context engine
    context_engine = ContextEngine(memory=memory)
    
    # Define a calculator tool
    class CalculatorTool(Tool):
        name = "calculator"
        description = "A tool for performing calculations"
        
        def add(self, a, b):
            return a + b
        
        def subtract(self, a, b):
            return a - b
        
        def multiply(self, a, b):
            return a * b
        
        def divide(self, a, b):
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
    
    # Define a weather tool
    class WeatherTool(Tool):
        name = "weather"
        description = "A tool for getting weather information"
        
        def get_weather(self, location):
            # This is a simplified example - in practice, you would call a weather API
            if location.lower() == "paris":
                return "Sunny, 25°C"
            elif location.lower() == "berlin":
                return "Cloudy, 18°C"
            elif location.lower() == "rome":
                return "Sunny, 30°C"
            else:
                return "Unknown location"
    
    # Initialize tool registry
    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())
    tool_registry.register(WeatherTool())
    
    # Initialize agent with tools
    agent = Agent(
        context_engine=context_engine,
        tool_registry=tool_registry
    )
    
    # Run the agent with tool use
    response = agent.run("What is the weather in Paris?")
    print(response)  # The agent will use the weather tool to get the weather in Paris
    
    response = agent.run("What is 5 + 3?")
    print(response)  # The agent will use the calculator tool to calculate 5 + 3

Agent with Multi-Turn Conversation
----------------------------------

This example shows how to use an agent with multi-turn conversation:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent, Conversation
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    
    # Initialize context engine
    context_engine = ContextEngine(memory=memory)
    
    # Initialize agent
    agent = Agent(context_engine=context_engine)
    
    # Initialize conversation
    conversation = Conversation()
    
    # First turn
    response = agent.run(
        "What is the capital of France?",
        conversation=conversation
    )
    print("User: What is the capital of France?")
    print(f"Assistant: {response}")
    
    # Second turn
    response = agent.run(
        "What about Germany?",
        conversation=conversation
    )
    print("User: What about Germany?")
    print(f"Assistant: {response}")
    
    # Third turn
    response = agent.run(
        "And Italy?",
        conversation=conversation
    )
    print("User: And Italy?")
    print(f"Assistant: {response}")

Agent with Streaming Response
-----------------------------

This example shows how to use an agent with streaming response:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    
    # Initialize context engine
    context_engine = ContextEngine(memory=memory)
    
    # Initialize agent
    agent = Agent(context_engine=context_engine)
    
    # Run the agent with streaming
    for chunk in agent.stream("What is the capital of France?"):
        print(chunk, end="", flush=True)  # Print each chunk as it arrives
    print()  # Print a newline at the end

See Also
--------

* :doc:`agent_example` - Basic agent example
* :doc:`../api/agent` - Agent API reference
* :doc:`../tutorials/agent_tutorial` - Agent tutorial
