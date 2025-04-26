Advanced Memory Example
=======================

This document provides advanced examples of using the Memory System.

Vector Memory with Custom Embeddings
------------------------------------

This example shows how to use Vector Memory with custom embeddings:

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

Hybrid Memory System
--------------------

This example shows how to use a hybrid memory system combining vector and keyword search:

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

Memory with Persistence
-----------------------

This example shows how to use memory with persistence:

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

Memory with Chunking
--------------------

This example shows how to use memory with chunking for large documents:

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

See Also
--------

* :doc:`memory_example` - Basic memory example
* :doc:`../api/memory` - Memory API reference
* :doc:`../tutorials/memory_tutorial` - Memory System tutorial
