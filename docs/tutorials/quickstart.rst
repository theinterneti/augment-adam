
Quickstart
==========

This document provides a quickstart guide for Augment Adam.

Getting Started
---------------

To get started with Augment Adam, follow these steps:

1. Install Augment Adam:

   .. code-block:: bash

      pip install augment-adam

2. Import the necessary modules:

   .. code-block:: python

      from augment_adam.memory import VectorMemory
      from augment_adam.context_engine import ContextEngine
      from augment_adam.ai_agent import Agent

3. Initialize the components:

   .. code-block:: python

      memory = VectorMemory()
      context_engine = ContextEngine(memory=memory)
      agent = Agent(context_engine=context_engine)

4. Run the agent:

   .. code-block:: python

      response = agent.run("What is the capital of France?")
      print(response)

Next Steps
----------

- Learn more about the :doc:`memory_tutorial`
- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`agent_tutorial`
- Learn more about the :doc:`plugin_tutorial`
