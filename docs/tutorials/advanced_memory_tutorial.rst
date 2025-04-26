Advanced Memory Tutorial
========================

This document provides an advanced tutorial for using the Memory System.

Introduction
------------

In this tutorial, we'll explore advanced features of the Memory System, including:

1. Custom embedding models
2. Hybrid memory systems
3. Memory persistence
4. Memory chunking
5. Memory filtering and ranking

Prerequisites
-------------

Before proceeding with this tutorial, make sure you have:

1. Completed the :doc:`memory_tutorial`
2. Installed Augment Adam
3. Basic understanding of vector embeddings

Custom Embedding Models
-----------------------

By default, the VectorMemory class uses a pre-configured embedding model. However, you can provide your own embedding model:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.embeddings import EmbeddingModel
    
    # Create a custom embedding model
    class CustomEmbeddingModel(EmbeddingModel):
        def embed(self, text):
            # Custom embedding logic
            # This is a simplified example - in practice, you would use a real embedding model
            return [0.1, 0.2, 0.3, 0.4, 0.5]  # Example embedding vector
    
    # Initialize memory with custom embedding model
    embedding_model = CustomEmbeddingModel()
    memory = VectorMemory(embedding_model=embedding_model)
    
    # Add data to memory
    memory.add("Paris is the capital of France")
    
    # Search memory
    results = memory.search("capital of France")
    print(results)

You can also use pre-trained models from popular libraries:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.embeddings import HuggingFaceEmbeddingModel
    
    # Initialize memory with a Hugging Face embedding model
    embedding_model = HuggingFaceEmbeddingModel("sentence-transformers/all-MiniLM-L6-v2")
    memory = VectorMemory(embedding_model=embedding_model)
    
    # Add data to memory
    memory.add("Paris is the capital of France")
    
    # Search memory
    results = memory.search("capital of France")
    print(results)

Hybrid Memory Systems
---------------------

You can combine different memory implementations to create a hybrid memory system:

.. code-block:: python

    from augment_adam.memory import VectorMemory, KeywordMemory, HybridMemory
    
    # Initialize vector memory
    vector_memory = VectorMemory()
    vector_memory.add("Paris is the capital of France")
    vector_memory.add("Berlin is the capital of Germany")
    
    # Initialize keyword memory
    keyword_memory = KeywordMemory()
    keyword_memory.add("The Eiffel Tower is in Paris, France")
    keyword_memory.add("The Brandenburg Gate is in Berlin, Germany")
    
    # Initialize hybrid memory
    hybrid_memory = HybridMemory([vector_memory, keyword_memory])
    
    # Search hybrid memory
    results = hybrid_memory.search("capital of France")
    print(results)  # Results from both vector and keyword memory
    
    # Search with weights
    results = hybrid_memory.search(
        "Paris landmarks",
        weights=[0.3, 0.7]  # 30% weight to vector memory, 70% to keyword memory
    )
    print(results)

Memory Persistence
------------------

You can save and load memory to/from disk:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    
    # Initialize memory with persistence
    memory = VectorMemory(persistence_path="./memory_data")
    
    # Add data to memory
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    
    # Save memory to disk
    memory.save()
    
    # Load memory from disk
    new_memory = VectorMemory(persistence_path="./memory_data")
    new_memory.load()
    
    # Search memory
    results = new_memory.search("capital of France")
    print(results)  # ["Paris is the capital of France"]

Memory Chunking
---------------

For large documents, you can use chunking to break them into smaller pieces:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.utils.text import TextChunker
    
    # Initialize memory
    memory = VectorMemory()
    
    # Initialize text chunker
    chunker = TextChunker(chunk_size=100, overlap=20)
    
    # Large document
    document = """
    Paris is the capital and most populous city of France. 
    It has an estimated population of 2,165,423 residents as of 2019 in an area of more than 105 km².
    Since the 17th century, Paris has been one of the world's major centres of finance, diplomacy, commerce, fashion, gastronomy, and science.
    
    Berlin is the capital and largest city of Germany by both area and population. 
    Its 3.7 million inhabitants make it the European Union's most populous city, according to population within city limits.
    Berlin is a world city of culture, politics, media, and science.
    """
    
    # Chunk the document
    chunks = chunker.chunk(document)
    
    # Add chunks to memory
    for chunk in chunks:
        memory.add(chunk)
    
    # Search memory
    results = memory.search("capital of France")
    print(results)  # Returns the chunk containing "Paris is the capital of France"

Memory Filtering and Ranking
----------------------------

You can filter and rank memory results:

.. code-block:: python

    from augment_adam.memory import VectorMemory
    
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
    
    # Search with filter
    results = memory.search(
        "capital",
        filter={"continent": "Europe"}
    )
    print(results)  # European capitals
    
    # Search with filter and sort
    results = memory.search(
        "capital",
        filter={"continent": "Europe"},
        sort_by="population",
        sort_order="desc"
    )
    print(results)  # European capitals sorted by population (descending)

Conclusion
----------

In this tutorial, we've explored advanced features of the Memory System, including custom embedding models, hybrid memory systems, memory persistence, memory chunking, and memory filtering and ranking.

Next Steps
----------

- Explore the :doc:`advanced_context_engine_tutorial`
- Explore the :doc:`advanced_agent_tutorial`
- Explore the :doc:`advanced_plugin_tutorial`
- Check out the :doc:`../examples/advanced_memory_example`
