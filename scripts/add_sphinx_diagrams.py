#!/usr/bin/env python3
"""
Script to add sample diagrams to the Sphinx documentation.

This script adds sample diagrams using Mermaid to the documentation.
"""

import os
from pathlib import Path

def add_architecture_diagram():
    """Add an architecture diagram to the overview page."""
    print("Adding architecture diagram...")
    
    file_path = "docs/architecture/overview.rst"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has a diagram
        if ".. mermaid::" in content:
            print("  Architecture diagram already exists")
            return
        
        # Add a diagram
        diagram = """
System Architecture Diagram
------------------------

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
"""
        
        # Append the diagram to the content
        new_content = content + diagram
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"  Added architecture diagram to {file_path}")

def add_memory_system_diagram():
    """Add a memory system diagram."""
    print("Adding memory system diagram...")
    
    file_path = "docs/architecture/memory_system.rst"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has a diagram
        if ".. mermaid::" in content:
            print("  Memory system diagram already exists")
            return
        
        # Add a diagram
        diagram = """
Memory System Architecture
-----------------------

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
"""
        
        # Append the diagram to the content
        new_content = content + diagram
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"  Added memory system diagram to {file_path}")

def add_context_engine_diagram():
    """Add a context engine diagram."""
    print("Adding context engine diagram...")
    
    file_path = "docs/architecture/context_engine.rst"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has a diagram
        if ".. mermaid::" in content:
            print("  Context engine diagram already exists")
            return
        
        # Add a diagram
        diagram = """
Context Engine Architecture
------------------------

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
"""
        
        # Append the diagram to the content
        new_content = content + diagram
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"  Added context engine diagram to {file_path}")

def add_agent_coordination_diagram():
    """Add an agent coordination diagram."""
    print("Adding agent coordination diagram...")
    
    file_path = "docs/architecture/agent_coordination.rst"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has a diagram
        if ".. mermaid::" in content:
            print("  Agent coordination diagram already exists")
            return
        
        # Add a diagram
        diagram = """
Agent Coordination Architecture
---------------------------

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
"""
        
        # Append the diagram to the content
        new_content = content + diagram
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"  Added agent coordination diagram to {file_path}")

def add_plugin_system_diagram():
    """Add a plugin system diagram."""
    print("Adding plugin system diagram...")
    
    file_path = "docs/architecture/plugin_system.rst"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has a diagram
        if ".. mermaid::" in content:
            print("  Plugin system diagram already exists")
            return
        
        # Add a diagram
        diagram = """
Plugin System Architecture
-----------------------

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
"""
        
        # Append the diagram to the content
        new_content = content + diagram
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"  Added plugin system diagram to {file_path}")

def add_template_engine_diagram():
    """Add a template engine diagram."""
    print("Adding template engine diagram...")
    
    file_path = "docs/architecture/template_engine.rst"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has a diagram
        if ".. mermaid::" in content:
            print("  Template engine diagram already exists")
            return
        
        # Add a diagram
        diagram = """
Template Engine Architecture
-------------------------

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
"""
        
        # Append the diagram to the content
        new_content = content + diagram
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"  Added template engine diagram to {file_path}")

def main():
    """Main function."""
    print("Adding diagrams to Sphinx documentation...")
    
    # Add architecture diagram
    add_architecture_diagram()
    
    # Add memory system diagram
    add_memory_system_diagram()
    
    # Add context engine diagram
    add_context_engine_diagram()
    
    # Add agent coordination diagram
    add_agent_coordination_diagram()
    
    # Add plugin system diagram
    add_plugin_system_diagram()
    
    # Add template engine diagram
    add_template_engine_diagram()
    
    print("Done!")

if __name__ == "__main__":
    main()
