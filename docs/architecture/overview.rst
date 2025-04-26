
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
