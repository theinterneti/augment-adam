
Memory API
=========

This document provides reference documentation for the Memory API.

Overview
-------

The Memory API provides various memory implementations for storing and retrieving information.

Core Components
-------------

* **VectorMemory**: Stores and retrieves information using vector embeddings
* **EpisodeMemory**: Stores and retrieves episodic information
* **SemanticMemory**: Stores and retrieves semantic information
* **WorkingMemory**: Stores and retrieves working memory information

VectorMemory
----------

The VectorMemory class provides a memory implementation that uses vector embeddings to store and retrieve information.

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

API Reference
-----------

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. automodule:: augment_adam.memory.core
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. automodule:: augment_adam.memory.vector
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/memory_system` - Memory System documentation
