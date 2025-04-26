Advanced Context Engine Tutorial
================================

This document provides an advanced tutorial for using the Context Engine.

Introduction
------------

In this tutorial, we'll explore advanced features of the Context Engine, including:

1. Multiple memory sources
2. Custom retrieval strategies
3. Query expansion
4. Context caching
5. Context filtering and ranking

Prerequisites
-------------

Before proceeding with this tutorial, make sure you have:

1. Completed the :doc:`context_engine_tutorial`
2. Installed Augment Adam
3. Basic understanding of the Memory System

Multiple Memory Sources
-----------------------

The Context Engine can use multiple memory sources:

.. code-block:: python

    from augment_adam.memory import VectorMemory, KeywordMemory
    from augment_adam.context_engine import ContextEngine
    
    # Initialize vector memory
    vector_memory = VectorMemory()
    vector_memory.add("Paris is the capital of France")
    vector_memory.add("Berlin is the capital of Germany")
    
    # Initialize keyword memory
    keyword_memory = KeywordMemory()
    keyword_memory.add("The Eiffel Tower is in Paris, France")
    keyword_memory.add("The Brandenburg Gate is in Berlin, Germany")
    
    # Initialize context engine with multiple memory sources
    context_engine = ContextEngine(
        memory_sources=[vector_memory, keyword_memory],
        memory_weights=[0.6, 0.4]  # 60% weight to vector memory, 40% to keyword memory
    )
    
    # Get context
    context = context_engine.get_context("What is the capital of France?")
    print(context)  # Results from both vector and keyword memory, weighted

Custom Retrieval Strategies
---------------------------

You can create custom retrieval strategies:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine, RetrievalStrategy
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    memory.add("The Eiffel Tower is in Paris, France")
    memory.add("The Brandenburg Gate is in Berlin, Germany")
    memory.add("The Colosseum is in Rome, Italy")
    
    # Create a custom retrieval strategy
    class CustomRetrievalStrategy(RetrievalStrategy):
        def retrieve(self, query, memory, max_results=5, threshold=0.7):
            # Custom retrieval logic
            # First, search for capitals
            capital_results = memory.search(
                f"capital {query}",
                max_results=max_results // 2,
                threshold=threshold
            )
            
            # Then, search for landmarks
            landmark_results = memory.search(
                f"landmark {query}",
                max_results=max_results // 2,
                threshold=threshold
            )
            
            # Combine results
            return capital_results + landmark_results
    
    # Initialize context engine with custom retrieval strategy
    context_engine = ContextEngine(
        memory=memory,
        retrieval_strategy=CustomRetrievalStrategy()
    )
    
    # Get context
    context = context_engine.get_context("France")
    print(context)  # ["Paris is the capital of France", "The Eiffel Tower is in Paris, France"]

Query Expansion
---------------

Query expansion can improve retrieval by expanding the query with related terms:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.utils.text import QueryExpander
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    
    # Initialize query expander
    query_expander = QueryExpander()
    
    # Initialize context engine with query expansion
    context_engine = ContextEngine(
        memory=memory,
        query_expander=query_expander
    )
    
    # Get context
    context = context_engine.get_context("What is the main city in France?")
    print(context)  # ["Paris is the capital of France"]
    
    # The query expander expands "main city" to include "capital"

Context Caching
---------------

Caching can improve performance by storing previously retrieved context:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.utils.cache import LRUCache
    
    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")
    
    # Initialize cache
    cache = LRUCache(max_size=100)
    
    # Initialize context engine with caching
    context_engine = ContextEngine(
        memory=memory,
        cache=cache
    )
    
    # Get context (first time, not cached)
    context = context_engine.get_context("What is the capital of France?")
    print(context)  # ["Paris is the capital of France"]
    
    # Get context again (cached)
    context = context_engine.get_context("What is the capital of France?")
    print(context)  # ["Paris is the capital of France"] (retrieved from cache)

Context Filtering and Ranking
-----------------------------

You can filter and rank context results:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    
    # Initialize memory
    memory = VectorMemory()
    
    # Add data with metadata
    memory.add(
        "Paris is the capital of France",
        metadata={"country": "France", "continent": "Europe", "population": 2165423}
    )
    memory.add(
        "Berlin is the capital of Germany",
        metadata={"country": "Germany", "continent": "Europe", "population": 3700000}
    )
    memory.add(
        "Rome is the capital of Italy",
        metadata={"country": "Italy", "continent": "Europe", "population": 2873000}
    )
    memory.add(
        "Tokyo is the capital of Japan",
        metadata={"country": "Japan", "continent": "Asia", "population": 13960000}
    )
    
    # Initialize context engine
    context_engine = ContextEngine(memory=memory)
    
    # Get context with filter
    context = context_engine.get_context(
        "What are the capitals in Europe?",
        filter={"continent": "Europe"}
    )
    print(context)  # European capitals
    
    # Get context with filter and sort
    context = context_engine.get_context(
        "What are the capitals in Europe?",
        filter={"continent": "Europe"},
        sort_by="population",
        sort_order="desc"
    )
    print(context)  # European capitals sorted by population (descending)

Conclusion
----------

In this tutorial, we've explored advanced features of the Context Engine, including multiple memory sources, custom retrieval strategies, query expansion, context caching, and context filtering and ranking.

Next Steps
----------

- Explore the :doc:`advanced_memory_tutorial`
- Explore the :doc:`advanced_agent_tutorial`
- Explore the :doc:`advanced_plugin_tutorial`
- Check out the :doc:`../examples/advanced_context_engine_example`
