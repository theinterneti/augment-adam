#!/usr/bin/env python3
"""
Script to add diagrams to Sphinx documentation.
"""

import os
import re
from pathlib import Path

def add_diagrams():
    """Add diagrams to documentation files."""
    print("Adding diagrams...")
    
    # Define the files to update
    files = {
        "docs/architecture/overview.rst": """
Overview
========

This document provides an overview of the Augment Adam architecture.

.. include:: ../../docs/architecture/ARCHITECTURE.md
   :parser: myst_parser.sphinx_

System Architecture Diagram
--------------------------

.. mermaid::

    graph TD
        User[User] --> Assistant[Assistant]
        Assistant --> MemorySystem[Memory System]
        Assistant --> ContextEngine[Context Engine]
        Assistant --> AgentCoordination[Agent Coordination]
        Assistant --> PluginSystem[Plugin System]
        Assistant --> TemplateEngine[Template Engine]
        
        MemorySystem --> |Stores| Data[(Data)]
        ContextEngine --> |Retrieves| Data
        ContextEngine --> |Provides Context| AgentCoordination
        AgentCoordination --> |Uses| PluginSystem
        PluginSystem --> |Generates| TemplateEngine
        TemplateEngine --> |Formats| Output[Output]
        
        subgraph Memory
            MemorySystem
            Data
        end
        
        subgraph Processing
            ContextEngine
            AgentCoordination
            PluginSystem
        end
        
        subgraph Presentation
            TemplateEngine
            Output
        end

See Also
--------

* :doc:`memory_system` - Memory System documentation
* :doc:`context_engine` - Context Engine documentation
* :doc:`agent_coordination` - Agent Coordination documentation
* :doc:`plugin_system` - Plugin System documentation
* :doc:`template_engine` - Template Engine documentation
* :doc:`../developer_guide/contributing` - Contributing guidelines
* :doc:`../developer_guide/testing_framework` - Testing Framework documentation
""",
        "docs/architecture/memory_system.rst": """
Memory System
============

This document provides information about the memory system.

.. include:: ../../docs/architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_

Memory System Architecture
-------------------------

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
""",
        "docs/architecture/context_engine.rst": """
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
""",
        "docs/architecture/agent_coordination.rst": """
Agent Coordination
=================

This document provides information about agent coordination.

.. include:: ../../docs/architecture/AGENT_COORDINATION.md
   :parser: myst_parser.sphinx_

Agent Coordination Architecture
-----------------------------

.. mermaid::

    graph TD
        Task[Task] --> |Input| Coordinator[Coordinator]
        Coordinator --> |Decompose| TaskDecomposer[Task Decomposer]
        TaskDecomposer --> |Create| Subtasks[Subtasks]
        
        Subtasks --> |Assign| AgentSelector[Agent Selector]
        AgentSelector --> |Select| Agent1[Agent 1]
        AgentSelector --> |Select| Agent2[Agent 2]
        AgentSelector --> |Select| Agent3[Agent 3]
        
        Agent1 --> |Execute| Result1[Result 1]
        Agent2 --> |Execute| Result2[Result 2]
        Agent3 --> |Execute| Result3[Result 3]
        
        Result1 --> |Collect| ResultAggregator[Result Aggregator]
        Result2 --> |Collect| ResultAggregator
        Result3 --> |Collect| ResultAggregator
        
        ResultAggregator --> |Synthesize| FinalResult[Final Result]
        
        subgraph Agent Coordination
            Coordinator
            TaskDecomposer
            AgentSelector
            ResultAggregator
        end
        
        subgraph Agents
            Agent1
            Agent2
            Agent3
        end

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/agent` - Agent API reference
""",
        "docs/architecture/plugin_system.rst": """
Plugin System
============

This document provides information about the plugin system.

.. include:: ../../docs/architecture/PLUGIN_SYSTEM.md
   :parser: myst_parser.sphinx_

Plugin System Architecture
------------------------

.. mermaid::

    graph TD
        Core[Core System] --> |Loads| PluginManager[Plugin Manager]
        PluginManager --> |Discovers| PluginRegistry[Plugin Registry]
        PluginRegistry --> |Registers| Plugin1[Plugin 1]
        PluginRegistry --> |Registers| Plugin2[Plugin 2]
        PluginRegistry --> |Registers| Plugin3[Plugin 3]
        
        Core --> |Requests| PluginManager
        PluginManager --> |Validates| PluginValidator[Plugin Validator]
        PluginValidator --> |Validates| Plugin1
        PluginValidator --> |Validates| Plugin2
        PluginValidator --> |Validates| Plugin3
        
        PluginManager --> |Executes| PluginExecutor[Plugin Executor]
        PluginExecutor --> |Executes| Plugin1
        PluginExecutor --> |Executes| Plugin2
        PluginExecutor --> |Executes| Plugin3
        
        Plugin1 --> |Returns| Result1[Result 1]
        Plugin2 --> |Returns| Result2[Result 2]
        Plugin3 --> |Returns| Result3[Result 3]
        
        Result1 --> |Collects| ResultCollector[Result Collector]
        Result2 --> |Collects| ResultCollector
        Result3 --> |Collects| ResultCollector
        
        ResultCollector --> |Returns| Core
        
        subgraph Plugin System
            PluginManager
            PluginRegistry
            PluginValidator
            PluginExecutor
            ResultCollector
        end
        
        subgraph Plugins
            Plugin1
            Plugin2
            Plugin3
        end

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/plugin` - Plugin API reference
""",
        "docs/architecture/template_engine.rst": """
Template Engine
==============

This document provides information about the template engine.

.. include:: ../../docs/architecture/TEMPLATE_ENGINE.md
   :parser: myst_parser.sphinx_

Template Engine Architecture
--------------------------

.. mermaid::

    graph TD
        Data[Data] --> |Input| TemplateEngine[Template Engine]
        TemplateEngine --> |Loads| TemplateLoader[Template Loader]
        TemplateLoader --> |Loads| Template[Template]
        
        Template --> |Parse| TemplateParser[Template Parser]
        TemplateParser --> |Create| AST[Abstract Syntax Tree]
        
        Data --> |Provide| ContextBuilder[Context Builder]
        ContextBuilder --> |Build| RenderContext[Render Context]
        
        AST --> |Render| TemplateRenderer[Template Renderer]
        RenderContext --> |Provide| TemplateRenderer
        
        TemplateRenderer --> |Output| RenderedOutput[Rendered Output]
        
        subgraph Template Engine
            TemplateLoader
            TemplateParser
            ContextBuilder
            TemplateRenderer
        end

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/template` - Template API reference
"""
    }
    
    # Write the updated files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Added diagram to {file_path}")

def main():
    """Main function."""
    print("Adding diagrams to Sphinx documentation...")
    
    # Add diagrams
    add_diagrams()
    
    print("Done!")

if __name__ == "__main__":
    main()
