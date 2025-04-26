
Getting Started
===============

This document provides a guide to getting started with Augment Adam.

Basic Usage
-----------

To get started with Augment Adam, follow these steps:

1. Import the necessary modules:

   .. code-block:: python

      from augment_adam.memory import VectorMemory
      from augment_adam.context_engine import ContextEngine
      from augment_adam.ai_agent import Agent

2. Initialize the components:

   .. code-block:: python

      memory = VectorMemory()
      context_engine = ContextEngine(memory=memory)
      agent = Agent(context_engine=context_engine)

3. Run the agent:

   .. code-block:: python

      response = agent.run("What is the capital of France?")
      print(response)

Advanced Usage
--------------

For more advanced usage, see the following sections:

* :doc:`configuration` - Configuration options
* :doc:`../tutorials/memory_tutorial` - Memory System tutorial
* :doc:`../tutorials/context_engine_tutorial` - Context Engine tutorial
* :doc:`../tutorials/agent_tutorial` - Agent tutorial
* :doc:`../tutorials/plugin_tutorial` - Plugin tutorial
