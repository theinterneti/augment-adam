Advanced Context Engine Example
===============================

This document provides advanced examples of using the Context Engine.

Context Engine with Multiple Memory Sources
-------------------------------------------

This example shows how to use the Context Engine with multiple memory sources:

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

Context Engine with Custom Retrieval Strategy
---------------------------------------------

This example shows how to use the Context Engine with a custom retrieval strategy:

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

Context Engine with Query Expansion
-----------------------------------

This example shows how to use the Context Engine with query expansion:

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

Context Engine with Caching
---------------------------

This example shows how to use the Context Engine with caching:

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

See Also
--------

* :doc:`context_engine_example` - Basic context engine example
* :doc:`../api/context_engine` - Context Engine API reference
* :doc:`../tutorials/context_engine_tutorial` - Context Engine tutorial
