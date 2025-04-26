
Agent Tutorial
============

This document provides a tutorial for using the Agent API.

Introduction
-----------

The Agent API provides a high-level interface for creating and running AI agents.

Basic Usage
---------

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

    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)  # "The capital of France is Paris."

Advanced Usage
------------

You can customize the agent's behavior with additional parameters:

.. code-block:: python

    # Run the agent with additional parameters
    response = agent.run(
        "What are the capitals in Europe?",
        max_tokens=100,
        temperature=0.7
    )
    print(response)  # "The capitals in Europe include Paris (France), Berlin (Germany), and Rome (Italy)."

Next Steps
---------

- Learn more about the :doc:`memory_tutorial`
- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`plugin_tutorial`
