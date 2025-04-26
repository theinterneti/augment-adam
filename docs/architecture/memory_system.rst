
Memory System
=============

This document provides information about the memory system.

.. include:: ../../docs/architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_

Memory System Architecture
--------------------------

.. mermaid::

    graph TD
        Client[Client] --> |Request| MemoryInterface[Memory Interface]
        MemoryInterface --> |Store| MemoryStore[Memory Store]
        MemoryInterface --> |Retrieve| MemoryStore
        MemoryInterface --> |Query| MemoryIndex[Memory Index]
        MemoryIndex --> |Search| MemoryStore
        
        subgraph Memory System
            MemoryInterface
            MemoryStore
            MemoryIndex
        end
        
        MemoryStore --> |Stores| VectorData[(Vector Data)]
        MemoryStore --> |Stores| MetadataData[(Metadata)]
        MemoryStore --> |Stores| DocumentData[(Document Data)]
        
        MemoryIndex --> |Indexes| VectorData
        MemoryIndex --> |Indexes| MetadataData

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`context_engine` - Context Engine documentation
* :doc:`../api/memory` - Memory API reference
