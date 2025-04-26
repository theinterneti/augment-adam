
Context Engine
=============

This document provides information about the context engine.

.. include:: ../../docs/architecture/CONTEXT_ENGINE.md
   :parser: myst_parser.sphinx_

Context Engine Architecture
-------------------------

.. mermaid::

    graph TD
        Query[Query] --> |Input| ContextEngine[Context Engine]
        ContextEngine --> |Analyze| QueryAnalyzer[Query Analyzer]
        QueryAnalyzer --> |Extract| Entities[Entities]
        QueryAnalyzer --> |Extract| Keywords[Keywords]
        QueryAnalyzer --> |Extract| Intent[Intent]
        
        Entities --> |Search| ContextRetriever[Context Retriever]
        Keywords --> |Search| ContextRetriever
        Intent --> |Search| ContextRetriever
        
        ContextRetriever --> |Query| MemorySystem[Memory System]
        ContextRetriever --> |Query| KnowledgeBase[Knowledge Base]
        ContextRetriever --> |Query| ExternalSources[External Sources]
        
        MemorySystem --> |Return| RelevantContext[Relevant Context]
        KnowledgeBase --> |Return| RelevantContext
        ExternalSources --> |Return| RelevantContext
        
        RelevantContext --> |Filter| ContextFilter[Context Filter]
        ContextFilter --> |Rank| ContextRanker[Context Ranker]
        ContextRanker --> |Format| ContextFormatter[Context Formatter]
        ContextFormatter --> |Output| FormattedContext[Formatted Context]

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`memory_system` - Memory System documentation
* :doc:`../api/context_engine` - Context Engine API reference
