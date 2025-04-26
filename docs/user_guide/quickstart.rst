
Quickstart
==========

This document provides a quickstart guide for Augment Adam.

Installation
------------

.. code-block:: bash

    pip install augment-adam

Basic Usage
-----------

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Initialize agent
    agent = Agent(context_engine=context_engine)

    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)  # "The capital of France is Paris."

Next Steps
----------

* :doc:`installation` - Installation guide
* :doc:`getting_started` - Getting started guide
* :doc:`configuration` - Configuration guide
* :doc:`../tutorials/memory_tutorial` - Memory System tutorial
* :doc:`../tutorials/context_engine_tutorial` - Context Engine tutorial
* :doc:`../tutorials/agent_tutorial` - Agent tutorial
* :doc:`../tutorials/plugin_tutorial` - Plugin tutorial
