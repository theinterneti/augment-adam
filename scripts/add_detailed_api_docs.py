#!/usr/bin/env python3
"""
Script to add more detailed API documentation.
"""

import os
import re
from pathlib import Path

def add_detailed_api_docs():
    """Add more detailed API documentation."""
    print("Adding detailed API documentation...")
    
    # Define the files to update
    files = {
        "docs/api/memory.rst": """
Memory API
=========

This document provides reference documentation for the Memory API.

Overview
-------

The Memory API provides various memory implementations for storing and retrieving information.

Core Components
-------------

* **VectorMemory**: Stores and retrieves information using vector embeddings
* **EpisodeMemory**: Stores and retrieves episodic information
* **SemanticMemory**: Stores and retrieves semantic information
* **WorkingMemory**: Stores and retrieves working memory information

VectorMemory
----------

The VectorMemory class provides a memory implementation that uses vector embeddings to store and retrieve information.

.. code-block:: python

    from augment_adam.memory import VectorMemory

    # Initialize memory
    memory = VectorMemory()

    # Add data to memory
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Search memory
    results = memory.search("capital of France")
    print(results)  # ["Paris is the capital of France"]

    # Add data with metadata
    memory.add(
        "Madrid is the capital of Spain",
        metadata={"country": "Spain", "continent": "Europe"}
    )

    # Search with metadata filter
    results = memory.search(
        "capital",
        filter={"continent": "Europe"}
    )
    print(results)  # ["Madrid is the capital of Spain"]

API Reference
-----------

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. automodule:: augment_adam.memory.core
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. automodule:: augment_adam.memory.vector
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/memory_system` - Memory System documentation
""",
        "docs/api/context_engine.rst": """
Context Engine API
================

This document provides reference documentation for the Context Engine API.

Overview
-------

The Context Engine is responsible for managing and retrieving relevant context for the assistant.

Core Components
-------------

* **ContextRetriever**: Retrieves relevant context from various sources
* **ContextAnalyzer**: Analyzes context to determine relevance
* **ContextManager**: Manages context storage and retrieval
* **ContextFormatter**: Formats context for use by the assistant

Usage
----

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

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
    print(context)  # ["Paris is the capital of France", "Berlin is the capital of Germany", "Rome is the capital of Italy"]

API Reference
-----------

.. automodule:: augment_adam.context_engine
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/context_engine` - Context Engine documentation
""",
        "docs/api/agent.rst": """
Agent API
========

This document provides reference documentation for the Agent API.

Overview
-------

The Agent API provides a high-level interface for creating and running AI agents.

Core Components
-------------

* **Agent**: The main agent class
* **AgentConfig**: Configuration for the agent
* **AgentContext**: Context for the agent
* **AgentResponse**: Response from the agent

Usage
----

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Initialize agent
    agent = Agent(context_engine=context_engine)

    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)  # "The capital of France is Paris."

    # Run the agent with additional parameters
    response = agent.run(
        "What are the capitals in Europe?",
        max_tokens=100,
        temperature=0.7
    )
    print(response)  # "The capitals in Europe include Paris (France), Berlin (Germany), and Rome (Italy)."

API Reference
-----------

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/agent_coordination` - Agent Coordination documentation
""",
        "docs/api/plugin.rst": """
Plugin API
=========

This document provides reference documentation for the Plugin API.

Overview
-------

The Plugin API enables the extension of the assistant's capabilities through plugins.

Core Components
-------------

* **Plugin**: Base class for plugins
* **PluginRegistry**: Registry for plugins
* **PluginLoader**: Loads plugins
* **PluginExecutor**: Executes plugins

Usage
----

.. code-block:: python

    from augment_adam.plugins import PluginRegistry, Plugin

    # Define a plugin
    class CalculatorPlugin(Plugin):
        name = "calculator"
        description = "A plugin for performing calculations"
        
        def add(self, a, b):
            return a + b
        
        def subtract(self, a, b):
            return a - b
        
        def multiply(self, a, b):
            return a * b
        
        def divide(self, a, b):
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b

    # Initialize plugin registry
    registry = PluginRegistry()

    # Register plugin
    registry.register(CalculatorPlugin())

    # Use plugin
    calculator = registry.get_plugin("calculator")
    result = calculator.add(2, 3)
    print(result)  # 5

    result = calculator.multiply(4, 5)
    print(result)  # 20

API Reference
-----------

.. automodule:: augment_adam.plugins
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/plugin_system` - Plugin System documentation
""",
        "docs/api/template.rst": """
Template API
==========

This document provides reference documentation for the Template API.

Overview
-------

The Template API manages templates for various outputs.

Core Components
-------------

* **TemplateEngine**: The main template engine class
* **Template**: Base class for templates
* **TemplateLoader**: Loads templates
* **TemplateRenderer**: Renders templates

Usage
----

.. code-block:: python

    from augment_adam.utils.templates import TemplateEngine

    # Initialize template engine
    engine = TemplateEngine()

    # Register a template
    engine.register_template("greeting", "Hello, {{ name }}!")

    # Render a template
    result = engine.render("greeting", {"name": "World"})
    print(result)  # "Hello, World!"

    # Register a template from a file
    engine.register_template_file("email", "templates/email.jinja2")

    # Render a template from a file
    result = engine.render("email", {
        "recipient": "John",
        "sender": "Jane",
        "subject": "Hello",
        "body": "This is a test email."
    })
    print(result)

API Reference
-----------

.. automodule:: augment_adam.utils.templates
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/template_engine` - Template Engine documentation
"""
    }
    
    # Write the updated files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Updated {file_path}")

def main():
    """Main function."""
    print("Adding detailed API documentation...")
    
    # Add detailed API documentation
    add_detailed_api_docs()
    
    print("Done!")

if __name__ == "__main__":
    main()
