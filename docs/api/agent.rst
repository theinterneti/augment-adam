
Agent API
========

This document provides reference documentation for the Agent API.

Overview
-------

The Agent API provides a high-level interface for creating and running AI agents.

Core Components
-------------

* **Agent**: The main agent class
* **AgentConfig**: Configuration for the agent
* **AgentContext**: Context for the agent
* **AgentResponse**: Response from the agent

Usage
----

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

    # Run the agent with additional parameters
    response = agent.run(
        "What are the capitals in Europe?",
        max_tokens=100,
        temperature=0.7
    )
    print(response)  # "The capitals in Europe include Paris (France), Berlin (Germany), and Rome (Italy)."

API Reference
-----------

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/agent_coordination` - Agent Coordination documentation
