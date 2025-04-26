
Memory Tutorial
=============

This document provides a tutorial for using the Memory System.

Introduction
-----------

The Memory System provides various memory implementations for storing and retrieving information.

Vector Memory
-----------

The most common memory implementation is the Vector Memory, which stores and retrieves information using vector embeddings.

.. code-block:: python

    from augment_adam.memory import VectorMemory

    # Initialize memory
    memory = VectorMemory()

    # Add data to memory
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Search memory
    results = memory.search("capital of France")
    print(results)  # ["Paris is the capital of France"]

Advanced Usage
------------

You can also add metadata to your memory entries:

.. code-block:: python

    # Add data with metadata
    memory.add(
        "Madrid is the capital of Spain",
        metadata={"country": "Spain", "continent": "Europe"}
    )

    # Search with metadata filter
    results = memory.search(
        "capital",
        filter={"continent": "Europe"}
    )
    print(results)  # ["Madrid is the capital of Spain"]

Next Steps
---------

- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`agent_tutorial`
- Learn more about the :doc:`plugin_tutorial`
