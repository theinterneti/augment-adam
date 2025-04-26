Search Functionality
====================

This document provides information about using the search functionality in Augment Adam.

Overview
--------

Augment Adam provides powerful search capabilities through its Memory System and Context Engine. This guide will help you understand how to use these search capabilities effectively.

Basic Search
------------

The most basic way to search is through the Memory System:

.. code-block:: python

    from augment_adam.memory import VectorMemory

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Search memory
    results = memory.search("capital of France")
    print(results)  # ["Paris is the capital of France"]

Advanced Search
---------------

For more advanced search capabilities, you can use metadata filters:

.. code-block:: python

    # Add data with metadata
    memory.add(
        "Madrid is the capital of Spain",
        metadata={"country": "Spain", "continent": "Europe"}
    )
    memory.add(
        "Paris is the capital of France",
        metadata={"country": "France", "continent": "Europe"}
    )
    memory.add(
        "Tokyo is the capital of Japan",
        metadata={"country": "Japan", "continent": "Asia"}
    )

    # Search with metadata filter
    results = memory.search(
        "capital",
        filter={"continent": "Europe"}
    )
    print(results)  # ["Madrid is the capital of Spain", "Paris is the capital of France"]

    # Search with multiple metadata filters
    results = memory.search(
        "capital",
        filter={"continent": "Europe", "country": "France"}
    )
    print(results)  # ["Paris is the capital of France"]

Context-Aware Search
--------------------

For context-aware search, you can use the Context Engine:

.. code-block:: python

    from augment_adam.context_engine import ContextEngine

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
    print(context)  # ["Paris is the capital of France", "Madrid is the capital of Spain"]

Semantic Search
---------------

Augment Adam uses semantic search to find relevant information even when the exact words don't match:

.. code-block:: python

    # Add data
    memory.add("The Eiffel Tower is in Paris")
    memory.add("The Colosseum is in Rome")
    memory.add("The Brandenburg Gate is in Berlin")

    # Search with semantic meaning
    results = memory.search("famous landmarks in France")
    print(results)  # ["The Eiffel Tower is in Paris"]

    # Search with semantic meaning and metadata filter
    results = memory.search(
        "famous landmarks",
        filter={"continent": "Europe"}
    )
    print(results)  # ["The Eiffel Tower is in Paris", "The Colosseum is in Rome", "The Brandenburg Gate is in Berlin"]

Search Parameters
-----------------

You can customize the search behavior with various parameters:

* **max_results**: Maximum number of results to return
* **threshold**: Minimum similarity score for a result to be included
* **filter**: Metadata filter to apply to the search
* **sort**: Sort results by similarity score (default: True)
* **include_metadata**: Include metadata in the results (default: False)

.. code-block:: python

    # Search with parameters
    results = memory.search(
        "capital",
        max_results=2,
        threshold=0.8,
        filter={"continent": "Europe"},
        sort=True,
        include_metadata=True
    )
    print(results)

See Also
--------

* :doc:`../api/memory` - Memory API reference
* :doc:`../api/context_engine` - Context Engine API reference
* :doc:`../tutorials/memory_tutorial` - Memory System tutorial
* :doc:`../tutorials/context_engine_tutorial` - Context Engine tutorial
