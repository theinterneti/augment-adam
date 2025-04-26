
Context Engine Example
======================

This document provides an example of using the Context Engine.

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Get context
    context = context_engine.get_context("What is the capital of France?")
    print(context)  # ["Paris is the capital of France"]

    # Get context with additional parameters
    context = context_engine.get_context(
        "What are the capitals in Europe?",
        max_results=3,
        threshold=0.7
    )
    print(context)  # ["Paris is the capital of France", "Berlin is the capital of Germany", "Rome is the capital of Italy"]
